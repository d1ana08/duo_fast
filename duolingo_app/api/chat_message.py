from typing import Dict, Set, List, Optional, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from duolingo_app.database.db import SessionLocal
from duolingo_app.database.models import UserProfile, ChatMessage, ChatGroup, GroupPeople
from duolingo_app.config import SECRET_KEY, ALGORITHM


chat_router = APIRouter(tags=['Chat WS'])

def _extract_token(websocket: WebSocket, token_q: Optional[str]) -> Optional[str]:
    if token_q:
        return token_q

    auth = websocket.headers.get('authorization')
    if not auth:
        return None

    parts = auth.split()
    if len(parts) == 2 and parts[0].lower() == 'Bearer':
        return parts[1]
    return None

def get_user_from_token(db: Session, token: str) -> UserProfile:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get('sub')
        if not username:
            raise JWTError('no sub')
    except JWTError:
        raise ValueError('Invalid token')
    user = db.query(UserProfile).filter(UserProfile.username == username).first()
    if not user:
        raise ValueError('User not found')
    return user


class ConnectManager:
    def __init__(self) -> None:
        self._connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, user_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.setdefault(user_id, set()).add(websocket)

    def disconnect(self, user_id: int, websocket: WebSocket) -> None:
        if user_id in self._connections:
            self._connections[user_id].discard(websocket)
            if not self._connections[user_id]:
                self._connections.pop(user_id, None)

    async def send_to_user(self, user_id: int, payload: dict) -> None:
        conns = list(self._connections.get(user_id, []))
        dead: List[WebSocket] = []
        for ws in conns:
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(user_id, ws)

    async def broadcast_to_users(self, user_ids: List[int], payload: dict) -> None:
        for uid in set(user_ids):
            await self.send_to_user(uid, payload)

manager = ConnectManager()


def is_member(db: Session, group_id: int, user_id: int) -> bool:
    return db.query(GroupPeople).filter(GroupPeople.group_id == group_id, GroupPeople.user_id == user_id).first() is not None


def get_group(db: Session, group_id: int) ->Optional[ChatGroup]:
    return db.query(ChatGroup).filter(ChatGroup.id == group_id).first()

def group_member_ids(db: Session, group_id: int) -> List[int]:
    rows = db.query(GroupPeople.user_id).filter(GroupPeople.group_id == group_id).all()
    return [r[0] for r in rows]

def group_to_dict(g: ChatGroup) -> dict:
    return {
        'id': g.id,
        'name': g.name,
        'owner_id': g.owner_id,
        'create_date': g.created_date.isoformat() if g.created_date else None

    }

def msg_to_dict(m: ChatMessage) -> dict:
    return {
        'id':m.id,
        'group_id': m.group_id,
        'sender_id': m.sender_id,
        'text': m.text,
        'created_date': m.created_date.isoformat() if m.created_date else None,

    }

@chat_router.websocket("/ws/chat")
async def chat_ws(websocket: WebSocket, token: Optional[str] = Query(default=None)):
    db = SessionLocal()
    user: Optional[UserProfile] = None

    try:
        tok = _extract_token(websocket, token)
        if not tok:
            await websocket.accept()
            await websocket.send_json({'event': 'error', 'detail': 'Missing token'})
            await websocket.close(code=1008)
            return
        try:
            user = get_user_from_token(db, tok)
        except ValueError:
            await websocket.accept()
            await websocket.send_json({'event': 'error', 'detail': 'Invalid token'})
            await websocket.close(code=1008)
            return


        await manager.connect(user.id, websocket)
        await websocket.send_json({'event': 'connected', 'user_id': user.id, 'username': user.username})

        while True:
            data: Dict[str, Any] = await websocket.receive_json()
            action = data.get('action')

            if action == 'create_group':
               name = (data.get('name')or "").strip()
               if not name:
                   await websocket.send_json({'event': 'error', 'action': action, 'detail': 'name is required'})
                   continue

               existing = db.query(ChatGroup).filter(ChatGroup.name == name).first()
               if existing:
                   await websocket.send_json({"event": "error", "detail": "Group already exists"})
                   continue

               g = ChatGroup(name=name, owner_id=user.id)
               db.add(g)
               db.commit()
               db.refresh(g)

               db.add(GroupPeople(group_id=g.id, user_id=user.id))
               db.commit()

               await websocket.send_json({'event': 'group_created', 'group': group_to_dict(g)})
               continue

            if action == 'list_groups':
                groups = (
                    db.query(ChatGroup).join(GroupPeople, GroupPeople.group_id == ChatGroup.id).
                    filter(GroupPeople.user_id == user.id).
                    order_by(ChatGroup.id.desc()).all()
                )
                await websocket.send_json({'event': 'groups', 'items': [group_to_dict(g) for g in groups]})
                continue

            if action == 'rename_group':
                group_id = data.get('group_id')
                new_name = (data.get('name') or "").strip()

                if  not group_id or not new_name:
                    await websocket.send_json({'event': 'error', 'action': action, 'detail': 'group_id and name required'})
                    continue

                g = get_group(db, int(group_id))
                if not g:
                    await websocket.send_json({'event': 'error', 'action': action, 'detail': 'group not found'})
                    continue
                if g.owner_id != user.id:
                    await websocket.send_json({'event': 'error', 'action': action, 'detail': 'only owner can rename'})
                    continue
                g.name = new_name
                db.commit()
                db.refresh(g)

                members = group_member_ids(db, g.id)
                await manager.broadcast_to_users(members, {'event': 'group_renamed', 'group': group_to_dict(g)})
                continue

            if action == 'add_members':
                group_id = data.get('group_id')
                user_ids = data.get('user_ids') or []

                if not group_id or not isinstance(user_ids, list) or not user_ids:
                    await websocket.send_json({'event': 'error', 'action': action, 'detail': 'group_id and user_ids required'})
                    continue

                g = get_group(db, int(group_id))
                if not g:
                    await websocket.send_json({'event': 'error', 'action': action, 'detail': 'group not found'})
                    continue

                if g.owner_id != user.id:
                    await websocket.send_json({'event': 'error', 'action': action, 'detail': 'only owner can add members'})
                    continue

                added: List[int] = []
                for uid in user_ids:
                    if not isinstance(uid, int):
                        continue
                    exists_user = db.query(UserProfile.id).filter(UserProfile.id == uid).first()
                    if not exists_user:
                        continue
                    already = db.query(GroupPeople).filter(GroupPeople.group_id == g.id,GroupPeople.user_id == uid).first()
                    if already:
                        continue
                    db.add(GroupPeople(group_id=g.id, user_id=uid))
                    added.append(uid)

                    db.commit()

                    members = group_member_ids(db, g.id)
                    await manager.broadcast_to_users(members, {'event': 'members added', 'group_id': g.id, 'added_user_ids': added})
                    continue


            if action == 'send_message':
                group_id = data.get('group_id')
                text = (data.get('text')or "").strip()
                if not group_id or not text:
                    await websocket.send_json({'event': 'error', 'action': action, 'detail': 'group_id and text required'})
                    continue

                if not is_member(db, int(group_id), user.id):
                    await websocket.send_json(
                        {'event': 'error', 'action': action, 'detail': 'You are not a member of this group'})
                    continue

                m = ChatMessage(group_id=group_id, sender_id=user.id, text=text)
                db.add(m)
                db.commit()
                db.refresh(m)

                members = group_member_ids(db, group_id)
                await manager.broadcast_to_users(members, {'event': 'message', 'message': msg_to_dict(m)})
                continue

            if action == 'fetch_messages':
                group_id = data.get('group_id')
                limit = int(data.get('limit') or 50)
                before_id = data.get('before_id')

                if not group_id:
                    await websocket.send_json({'event': 'error', 'action': action, 'detail': 'group_id required'})
                    continue

                group_id = int(group_id)
                if not is_member(db, group_id, user.id):
                    await websocket.send_json({'event': 'error', 'action': action, 'detail': 'not a member'})
                    continue

                q = db.query(ChatMessage).filter(ChatMessage.group_id == group_id)
                if before_id:
                    q =  q.filter(ChatMessage.id < int(before_id))
                msgs = q.order_by(ChatMessage.id.desc()).limit(min(limit, 200)).all()
                msgs = list(reversed(msgs))

                await websocket.send_json({'event': 'messages', 'group_id': group_id, 'items': [msg_to_dict(x) for x in msgs]})
                continue

            await websocket.send_json({'event': 'error', 'detail': f'Unknown action: {action}'})


            if action == 'leave_group':
                group_id = data.get('group_id')
                if not group_id:
                    await websocket.send_json({'event': 'error', 'action': action, 'detail': 'group_id required'})
                    continue

                group_id = int(group_id)
                if not is_member(db, group_id, user.id):
                    await websocket.send_json({'event': 'error', 'action': action, 'detail': 'You are not a member'})
                    continue
                g = get_group(db, int(group_id))
                if not g:
                    await websocket.send_json({'event': 'error', 'detail': 'group not found'})
                    continue

                if not is_member(db, g.id, user.id):
                    await websocket.send_json({'event': 'error', 'detail': 'not a member'})
                    continue

                if g.owner_id == user.id:
                    other_members = db.query(GroupPeople).filter(GroupPeople.group_id == g.id,
                                                                 GroupPeople.user_id != user.id).all()
                    if other_members:
                        new_owner = other_members[0].user_id
                        g.owner_id = new_owner
                        db.commit()
                        await manager.broadcast_to_users(
                            group_member_ids(db, g.id),
                            {'event': 'owner_changed', 'group_id': g.id, 'new_owner': new_owner}
                        )
                    else:
                        db.delete(g)
                        db.commit()
                        await websocket.send_json({'event': 'group_deleted', 'group_id': g.id})
                        continue

                gp = db.query(GroupPeople).filter(GroupPeople.group_id == group_id,
                                                  GroupPeople.user_id == user.id).first()
                if gp:
                    db.delete(gp)
                    db.commit()

                await websocket.send_json({'event': 'left_group', 'group_id': group_id})
                continue

            if action == 'delete_group':
                group_id = data.get('group_id')
                if not group_id:
                    await websocket.send_json({'event': 'error', 'action': action, 'detail': 'group_id required'})
                    continue

                group_id = int(group_id)
                g = get_group(db, group_id)
                if not g:
                    await websocket.send_json({'event': 'error', 'action': action, 'detail': 'group not found'})
                    continue

                if g.owner_id != user.id:
                    await websocket.send_json({'event': 'error', 'action': action, 'detail': 'only owner can delete'})
                    continue

                db.query(GroupPeople).filter(GroupPeople.group_id == group_id).delete()
                db.delete(g)
                db.commit()

                await websocket.send_json({'event': 'group_deleted', 'group_id': group_id})
                continue

    except WebSocketDisconnect:
        pass
    finally:
        if user is not None:
            manager.disconnect(user.id, websocket)
        db.close()

