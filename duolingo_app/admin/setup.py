from fastapi import FastAPI
from sqladmin import Admin
from duolingo_app.database.db import engine
from .views import (UserProfileAdmin,UserProgressAdmin,LanguageAdmin,CourseAdmin,
                    SubCourseAdmin,LessonAdmin,ExerciseAdmin,XPHistoryAdmin,StreakAdmin,ChatGroupAdmin,
                    GroupPeopleAdmin,ChatMessageAdmin,FollowAdmin,ReviewAdmin,PaidSubscriptionAdmin,InviteFriendAdmin,)


def setup_admin(app: FastAPI):
    admin = Admin(app, engine)
    admin.add_view(UserProfileAdmin)
    admin.add_view(UserProgressAdmin)
    admin.add_view(LanguageAdmin)
    admin.add_view(CourseAdmin)
    admin.add_view(SubCourseAdmin)
    admin.add_view(LessonAdmin)
    admin.add_view(ExerciseAdmin)
    admin.add_view(XPHistoryAdmin)
    admin.add_view(StreakAdmin)
    admin.add_view(ChatGroupAdmin)
    admin.add_view(GroupPeopleAdmin)
    admin.add_view(ChatMessageAdmin)
    admin.add_view(FollowAdmin)
    admin.add_view(ReviewAdmin)
    admin.add_view(PaidSubscriptionAdmin)
    admin.add_view(InviteFriendAdmin)




