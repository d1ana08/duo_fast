import uvicorn
from fastapi import FastAPI
from duolingo_app.api import (user, user_progress, subcourse, course, lesson,
                              history, language, streak, exercise)

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


if __name__ == '__main__':
    uvicorn.run(duolingo_app, host='127.0.0.1', port=8001)