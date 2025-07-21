from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import os

from app.features.users.routes import router as users_router
from app.features.exercises.routes import router as exercise_router
from app.features.sessions.routes import router as session_router
from app.prediction.routes import router as prediction_router
from app.auth_routes import router as auth_router
from app.db.database import Base, engine

# _ = [
#     User,
#     UserProblem,
#     Onboarding,
#     Exercise,
#     Session,
#     SessionRequirement,
#     ExerciseSet,
#     Repetition,
# ]

app = FastAPI()
Base.metadata.create_all(bind=engine)

origins = ["http://localhost:5173", "http://127.0.0.1:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


routers = [
    auth_router,
    users_router,
    prediction_router,
    exercise_router,
    session_router,
]

os.makedirs("app/static/images", exist_ok=True)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

for router in routers:
    app.include_router(router)
