from datetime import datetime, date
from typing import Optional, Dict, Any, Union
from pydantic import BaseModel, EmailStr, ConfigDict, Field
from .models import RoleChoices, LevelChoices, TypeChoices, OptionChoices


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class UserProfileOutSchema(ORMBase):
    id: int
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: Optional[str] = None
    role: RoleChoices
    is_active: bool
    created_at: datetime
    avatar: Optional[str] = None
    age: Optional[int] = None


class UserProfileInputSchema(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    phone_number: Optional[str] = None
    avatar: Optional[str] = None
    age: Optional[int] = None


class UserLoginSchema(BaseModel):
    username: str
    password: str

class RefreshTokenOutSchema(ORMBase):
    id: int
    user_id: int
    token: str
    created_date: datetime


class RefreshTokenInputSchema(BaseModel):
    user_id: int
    token: str

class UserProgressOutSchema(ORMBase):
    id: int
    completed: bool
    score: int
    completed_at: datetime
    user_id: int
    lesson_id: int

class UserProgressInputSchema(BaseModel):
    completed: bool = False
    score: int = 0
    user_id: int
    lesson_id: int

class LanguageOutSchema(ORMBase):
    id: int
    language_name: str
    code: str
    is_active: bool

class LanguageInputSchema(BaseModel):
    language_name: str
    code: str
    is_active: bool = True

class CourseOutSchema(ORMBase):
    id: int
    title: str
    description: str
    level: LevelChoices
    order: int
    language_id: int

class CourseInputSchema(BaseModel):
    title: str
    description: str
    level: LevelChoices = LevelChoices.A1
    order: int
    language_id: int

class SubCourseOutSchema(ORMBase):
    id: int
    course_name: str
    course_id: int

class SubCourseInputSchema(BaseModel):
    course_name: str
    course_id: int

class LessonOutSchema(ORMBase):
    id: int
    title: str
    order: int
    is_locked: bool
    course_id: int

class LessonInputSchema(BaseModel):
    title: str
    order: int
    is_locked: bool = False
    course_id: int

class ExerciseOutSchema(ORMBase):
    id: int
    type: TypeChoices
    question: str
    options: Optional[Dict[str, Any]] = None
    correct_answer: Union[str, Dict[str, Any]]
    article: OptionChoices
    lesson_id: int

class ExerciseInputSchema(BaseModel):
    type: TypeChoices
    question: str
    options: Optional[Dict[str, Any]] = None
    correct_answer: Union[str, Dict[str, Any]]
    article: OptionChoices = OptionChoices.an
    lesson_id: int

class XPHistoryOutSchema(ORMBase):
    id: int
    xp: int
    reason: str
    created_at: datetime
    user_id: int

class XPHistoryInputSchema(BaseModel):
    xp: int
    reason: str
    user_id: int

class StreakOutSchema(ORMBase):
    id: int
    current_streak: int
    last_activity: date
    user_id: int

class StreakInputSchema(BaseModel):
    current_streak: int = 0
    last_activity: date = Field(default_factory=date.today)
    user_id: int

class ChatGroupOutSchema(ORMBase):
    id: int
    name: str
    created_date: datetime
    owner_id: int

class ChatGroupInputSchema(BaseModel):
    name: str
    owner_id: int

class GroupPeopleOutSchema(ORMBase):
    id: int
    joined_date: datetime
    group_id: int
    user_id: int

class GroupPeopleInputSchema(BaseModel):
    group_id: int
    user_id: int

class ChatMessageOutSchema(ORMBase):
    id: int
    text: str
    created_date: datetime
    is_read: bool
    group_id: int
    sender_id: int

class ChatMessageInputSchema(BaseModel):
    text: str
    is_read: bool = False
    group_id: int
    sender_id: int

class FollowOutSchema(ORMBase):
    id: int
    created_date: date
    follower_id: int
    followed_id: int

class FollowInputSchema(BaseModel):
    follower_id: int
    followed_id: int

class ReviewOutSchema(ORMBase):
    id: int
    rating: int
    point: int
    course_id: int

class ReviewInputSchema(BaseModel):
    rating: int
    point: int
    course_id: int

class PaidSubScriptionOutSchema(ORMBase):
    id: int
    subscription_name: str
    created_date: date
    user_id: int

class PaidSubScriptionInputSchema(BaseModel):
    subscription_name: str
    user_id: int

class InviteFriendOutSchema(ORMBase):
    id: int
    name: str
    email: EmailStr
    invited_by: str
    user_id: int

class InviteFriendInputSchema(BaseModel):
    name: str
    email: EmailStr
    invited_by: str
    user_id: int
