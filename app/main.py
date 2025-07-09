from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import os

from app.features.users.routes import router as users_router
from app.features.exercises.routes import router as exercise_router
from app.prediction.routes import router as prediction_router
from app.db.database import Base, engine
from app.features.users.models import User, UserProblem, Onboarding
from app.features.exercises.models import Exercise
from app.features.sessions.models import (
    Session,
    SessionRequirement,
    ExerciseSet,
    Repetition,
)

_ = [
    User,
    UserProblem,
    Onboarding,
    Exercise,
    Session,
    SessionRequirement,
    ExerciseSet,
    Repetition,
]

app = FastAPI()
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

routers = [users_router, prediction_router, exercise_router]

os.makedirs("app/static/images", exist_ok=True)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

for router in routers:
    app.include_router(router)
