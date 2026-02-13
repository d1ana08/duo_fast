import uvicorn
from fastapi import FastAPI
from duolingo_app.api.chat_message import chat_router
from duolingo_app.api import (
    user,
    user_progress,
    language,
    course,
    subcourse,
    lesson,
    exercise,
    history,
    streak,
    chatgroup,
    group_people,
    chat_message,
    follow,
    review,
    paid_sub,
    invite,
    auth,)

duolingo_app = FastAPI()
duolingo_app.include_router(user.user_router)
duolingo_app.include_router(user_progress.progress_router)
duolingo_app.include_router(subcourse.sub_router)
duolingo_app.include_router(course.course_router)
duolingo_app.include_router(lesson.lesson_router)
duolingo_app.include_router(history.history_router)
duolingo_app.include_router(language.language_router)
duolingo_app.include_router(streak.streak_router)
duolingo_app.include_router(exercise.exercise_router)
duolingo_app.include_router(chatgroup.group_router)
duolingo_app.include_router(group_people.people_router)
duolingo_app.include_router(chat_message.chat_router)
duolingo_app.include_router(chat_router)
duolingo_app.include_router(follow.follow_router)

duolingo_app.include_router(review.review_router)
duolingo_app.include_router(paid_sub.paid_subscription_router)
duolingo_app.include_router(invite.invited_friend_router)
duolingo_app.include_router(auth.auth_router)



if __name__ == '__main__':
    uvicorn.run(duolingo_app, host='127.0.0.1', port=8003)