from __future__ import annotations
from datetime import datetime, date
from enum import Enum as PyEnum
from typing import Optional, List, Dict, Any
from sqlalchemy import (Integer, String, Enum, Boolean, DateTime, Date,
                        ForeignKey, Text, JSON, UniqueConstraint)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base


class RoleChoices(str, PyEnum):
    admin = "admin"
    user = "user"


class LevelChoices(str, PyEnum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"


class TypeChoices(str, PyEnum):
    single_choice = "single_choice"
    multiple_choice = "multiple_choice"
    text = "text"
    matching = "matching"


class OptionChoices(str, PyEnum):
    a = "a"
    an = "an"
    the = "the"

class UserProfile(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    phone_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    role: Mapped[RoleChoices] = mapped_column(Enum(RoleChoices), default=RoleChoices.user, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    avatar: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    progress_user: Mapped[List["UserProgress"]] = relationship(
        "UserProgress", back_populates="user", cascade="all, delete-orphan")
    history_user: Mapped[List["XPHistory"]] = relationship(
        "XPHistory", back_populates="user", cascade="all, delete-orphan")
    streak_user: Mapped[List["Streak"]] = relationship(
        "Streak", back_populates="user", cascade="all, delete-orphan")
    tokens: Mapped[List["RefreshToken"]] = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan")
    chats_owned: Mapped[List["ChatGroup"]] = relationship(
        "ChatGroup", back_populates="owner", cascade="all, delete-orphan")
    group_memberships: Mapped[List["GroupPeople"]] = relationship(
        "GroupPeople", back_populates="user", cascade="all, delete-orphan")
    messages_sent: Mapped[List["ChatMessage"]] = relationship(
        "ChatMessage", back_populates="sender", cascade="all, delete-orphan")

    following_links: Mapped[List["Follow"]] = relationship(
        "Follow",
        back_populates="follower",
        foreign_keys="Follow.follower_id",
        cascade="all, delete-orphan",)
    follower_links: Mapped[List["Follow"]] = relationship(
        "Follow",
        back_populates="followed",
        foreign_keys="Follow.followed_id",
        cascade="all, delete-orphan",)

    paid_subscriptions: Mapped[List["PaidSubScription"]] = relationship(
        "PaidSubScription", back_populates="user", cascade="all, delete-orphan")
    invited_friends: Mapped[List["InviteFriend"]] = relationship(
        "InviteFriend", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<UserProfile id={self.id} username={self.username!r} role={self.role}>"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def deactivate(self) -> None:
        self.is_active = False

    def activate(self) -> None:
        self.is_active = True

    def add_xp(self, xp: int, reason: str = "activity") -> "XPHistory":
        return XPHistory(user_id=self.id, xp=xp, reason=reason)

    def follow(self, other_user_id: int) -> "Follow":
        return Follow(follower_id=self.id, followed_id=other_user_id)

    def unfollow(self, other_user_id: int) -> Dict[str, Any]:
        return {"follower_id": self.id, "followed_id": other_user_id}


class RefreshToken(Base):
    __tablename__ = 'refresh_token'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    token: Mapped[str] = mapped_column(String, nullable=False)
    created_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user: Mapped["UserProfile"] = relationship("UserProfile", back_populates="tokens")

    def __repr__(self) -> str:
        return f'<RefreshToken id={self.id} user_id={self.user_id}>'


class Language(Base):
    __tablename__ = 'language'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    language_name: Mapped[str] = mapped_column(String(30), nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    courses: Mapped[List["Course"]] = relationship(
        "Course", back_populates="language", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Language id={self.id} code={self.code!r}>"


class Course(Base):
    __tablename__ = 'course'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    level: Mapped[LevelChoices] = mapped_column(Enum(LevelChoices), default=LevelChoices.A1, nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)

    language_id: Mapped[int] = mapped_column(ForeignKey("language.id"), nullable=False, index=True)
    language: Mapped["Language"] = relationship("Language", back_populates="courses")

    lessons: Mapped[List["Lesson"]] = relationship(
        "Lesson", back_populates="course", cascade='all, delete-orphan')
    subcourses: Mapped[List["SubCourse"]] = relationship(
        "SubCourse", back_populates="course", cascade='all, delete-orphan')
    reviews: Mapped[List["Review"]] = relationship(
        "Review", back_populates="course", cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return f"<Course id={self.id} title={self.title!r} level={self.level}>"

    def lock_all_lessons(self) -> None:
        for l in self.lessons:
            l.is_locked = True

    def unlock_all_lessons(self) -> None:
        for l in self.lessons:
            l.is_locked = False


class SubCourse(Base):
    __tablename__ = 'subcourse'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    course_name: Mapped[str] = mapped_column(String(50), nullable=False)

    course_id: Mapped[int] = mapped_column(ForeignKey('course.id'), nullable=False, index=True)
    course: Mapped['Course'] = relationship('Course', back_populates='subcourses')

    def __repr__(self) -> str:
        return f"<SubCourse id={self.id} course_name={self.course_name!r}>"


class Lesson(Base):
    __tablename__ = 'lesson'
    __table_args__ = (UniqueConstraint("course_id", "order", name="uq_lesson_course_order"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    course_id: Mapped[int] = mapped_column(ForeignKey("course.id"), nullable=False, index=True)
    course: Mapped["Course"] = relationship("Course", back_populates="lessons")

    exercises: Mapped[List["Exercise"]] = relationship(
        "Exercise", back_populates="lesson", cascade="all, delete-orphan")
    progress: Mapped[List["UserProgress"]] = relationship(
        "UserProgress", back_populates="lesson", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Lesson id={self.id} course_id={self.course_id} order={self.order} locked={self.is_locked}>"

    def lock(self) -> None:
        self.is_locked = True

    def unlock(self) -> None:
        self.is_locked = False


class Exercise(Base):
    __tablename__ = 'exercise'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    type: Mapped[TypeChoices] = mapped_column(Enum(TypeChoices), nullable=False)

    question: Mapped[str] = mapped_column(Text, nullable=False)

    options: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    correct_answer: Mapped[Dict[str, Any] | str] = mapped_column(JSON, nullable=False)

    article: Mapped[OptionChoices] = mapped_column(Enum(OptionChoices), default=OptionChoices.an, nullable=False)

    lesson_id: Mapped[int] = mapped_column(ForeignKey("lesson.id"), nullable=False, index=True)
    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="exercises")

    def __repr__(self) -> str:
        return f"<Exercise id={self.id} type={self.type} lesson_id={self.lesson_id}>"

    def set_correct_answer(self, value: Dict[str, Any] | str) -> None:
        self.correct_answer = value


class UserProgress(Base):
    __tablename__ = 'user_progress'
    __table_args__ = (UniqueConstraint("user_id", "lesson_id", name="uq_progress_user_lesson"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    user: Mapped["UserProfile"] = relationship("UserProfile", back_populates="progress_user")

    lesson_id: Mapped[int] = mapped_column(ForeignKey("lesson.id"), nullable=False, index=True)
    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="progress")

    def __repr__(self) -> str:
        return f"<UserProgress id={self.id} user_id={self.user_id} lesson_id={self.lesson_id} completed={self.completed}>"

    def mark_completed(self, score: int) -> None:
        self.completed = True
        self.score = score
        self.completed_at = datetime.utcnow()


class XPHistory(Base):
    __tablename__ = 'history'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    xp: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    user: Mapped["UserProfile"] = relationship("UserProfile", back_populates="history_user")

    def __repr__(self) -> str:
        return f"<XPHistory id={self.id} user_id={self.user_id} xp={self.xp}>"


class Streak(Base):
    __tablename__ = 'streak'
    __table_args__ = (UniqueConstraint("user_id", name="uq_streak_user"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    current_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_activity: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    user: Mapped["UserProfile"] = relationship("UserProfile", back_populates="streak_user")

    def __repr__(self) -> str:
        return f"<Streak id={self.id} user_id={self.user_id} streak={self.current_streak}>"

    def update_activity(self, activity_date: Optional[date] = None) -> None:
        today = activity_date or date.today()
        if today == self.last_activity:
            return
        if (today - self.last_activity).days == 1:
            self.current_streak += 1
        else:
            self.current_streak = 1
        self.last_activity = today


class ChatGroup(Base):
    __tablename__ = 'chat_group'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    owner: Mapped["UserProfile"] = relationship("UserProfile", back_populates="chats_owned")

    members: Mapped[List["GroupPeople"]] = relationship(
        "GroupPeople", back_populates="group", cascade="all, delete-orphan")
    messages: Mapped[List["ChatMessage"]] = relationship(
        "ChatMessage", back_populates="group", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<ChatGroup id={self.id} name={self.name!r} owner_id={self.owner_id}>"

    def add_member(self, user_id: int) -> "GroupPeople":
        return GroupPeople(group_id=self.id, user_id=user_id)


class GroupPeople(Base):
    __tablename__ = 'group_people'
    __table_args__ = (
        UniqueConstraint("group_id", "user_id", name="uq_group_people_group_user"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    joined_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    group_id: Mapped[int] = mapped_column(ForeignKey("chat_group.id"), nullable=False, index=True)
    group: Mapped["ChatGroup"] = relationship("ChatGroup", back_populates="members")

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    user: Mapped["UserProfile"] = relationship("UserProfile", back_populates="group_memberships")

    def __repr__(self) -> str:
        return f"<GroupPeople id={self.id} group_id={self.group_id} user_id={self.user_id}>"


class ChatMessage(Base):
    __tablename__ = 'message'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    group_id: Mapped[int] = mapped_column(ForeignKey("chat_group.id"), nullable=False, index=True)
    group: Mapped["ChatGroup"] = relationship("ChatGroup", back_populates="messages")

    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    sender: Mapped["UserProfile"] = relationship("UserProfile", back_populates="messages_sent")

    def __repr__(self) -> str:
        return f"<ChatMessage id={self.id} group_id={self.group_id} sender_id={self.sender_id} read={self.is_read}>"

    def mark_read(self) -> None:
        self.is_read = True


class Follow(Base):
    __tablename__ = 'follows'
    __table_args__ = (
        UniqueConstraint("follower_id", "followed_id", name="uq_follows_pair"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)

    follower_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    followed_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    follower: Mapped["UserProfile"] = relationship(
        "UserProfile",
        back_populates="following_links",
        foreign_keys=[follower_id],)
    followed: Mapped["UserProfile"] = relationship(
        "UserProfile",
        back_populates="follower_links",
        foreign_keys=[followed_id],)

    def __repr__(self) -> str:
        return f"<Follow id={self.id} follower_id={self.follower_id} followed_id={self.followed_id}>"


class Review(Base):
    __tablename__ = 'review'
    __table_args__ = (
        UniqueConstraint("course_id", name="uq_review_course"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rating: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    point: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    course_id: Mapped[int] = mapped_column(ForeignKey("course.id"), nullable=False, index=True)
    course: Mapped["Course"] = relationship("Course", back_populates="reviews")

    def __repr__(self) -> str:
        return f"<Review id={self.id} course_id={self.course_id} rating={self.rating}>"


class PaidSubScription(Base):
    __tablename__ = 'paid_subscription'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    subscription_name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_date: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    user: Mapped["UserProfile"] = relationship("UserProfile", back_populates="paid_subscriptions")

    def __repr__(self) -> str:
        return f"<PaidSubScription id={self.id} user_id={self.user_id} name={self.subscription_name!r}>"


class InviteFriend(Base):
    __tablename__ = 'invited_friend'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    invited_by: Mapped[str] = mapped_column(String(255), nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    user: Mapped["UserProfile"] = relationship("UserProfile", back_populates="invited_friends")

    def __repr__(self) -> str:
        return f"<InviteFriend id={self.id} user_id={self.user_id} email={self.email!r}>"
