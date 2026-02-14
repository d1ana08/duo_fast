from sqladmin import ModelView

from duolingo_app.database.models import (UserProfile,UserProgress,Language,Course,SubCourse,Lesson,Exercise,XPHistory,Streak,ChatGroup,GroupPeople,ChatMessage,Follow,Review,PaidSubScription,InviteFriend)


class UserProfileAdmin(ModelView, model=UserProfile):
    column_list = [
        UserProfile.id,
        UserProfile.username,
        UserProfile.first_name,
        UserProfile.last_name,
        UserProfile.email,
        UserProfile.role,
        UserProfile.is_active,
        UserProfile.created_at,
    ]
    name = 'User'
    name_plural = 'Users'


class UserProgressAdmin(ModelView, model=UserProgress):
    column_list = [
        UserProgress.id,
        UserProgress.user_id,
        UserProgress.score,
        UserProgress.completed,
        UserProgress.completed_at,]


class LanguageAdmin(ModelView, model=Language):
    column_list = [Language.id, Language.language_name, Language.code, Language.is_active]


class CourseAdmin(ModelView, model=Course):
    column_list = [
        Course.id,
        Course.title,
        Course.level,
        Course.order,
        Course.language_id,
    ]


class SubCourseAdmin(ModelView, model=SubCourse):
    column_list = [SubCourse.id, SubCourse.course_name, SubCourse.course_id]


class LessonAdmin(ModelView, model=Lesson):
    column_list = [Lesson.id, Lesson.title, Lesson.order, Lesson.is_locked, Lesson.course_id]


class ExerciseAdmin(ModelView, model=Exercise):
    column_list = [
        Exercise.id,
        Exercise.question,
        Exercise.correct_answer,
        Exercise.lesson_id,
    ]


class XPHistoryAdmin(ModelView, model=XPHistory):
    column_list = [XPHistory.id, XPHistory.user_id, XPHistory.xp, XPHistory.reason]


class StreakAdmin(ModelView, model=Streak):
    column_list = [Streak.id, Streak.user_id, Streak.current_streak, Streak.last_activity]


class ChatGroupAdmin(ModelView, model=ChatGroup):
    column_list = [ChatGroup.id, ChatGroup.name, ChatGroup.created_date]


class GroupPeopleAdmin(ModelView, model=GroupPeople):
    column_list = [GroupPeople.id, GroupPeople.group_id, GroupPeople.user_id]


class ChatMessageAdmin(ModelView, model=ChatMessage):
    column_list = [
        ChatMessage.id,
        ChatMessage.text,
        ChatMessage.created_date,
        ChatMessage.is_read,
    ]


class FollowAdmin(ModelView, model=Follow):
    column_list = [Follow.id, Follow.followed_id, Follow.follower_id, Follow.created_date]



class ReviewAdmin(ModelView, model=Review):
    column_list = [Review.id, Review.rating, Review.point, Review.course_id]


class PaidSubscriptionAdmin(ModelView, model=PaidSubScription):
    column_list = [
        PaidSubScription.id,
        PaidSubScription.subscription_name,
        PaidSubScription.created_date,
    ]


class InviteFriendAdmin(ModelView, model=InviteFriend):
    column_list = [
        InviteFriend.id,
        InviteFriend.name,
        InviteFriend.email,
        InviteFriend.invited_by,
    ]
