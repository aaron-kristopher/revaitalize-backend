from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import tensorflow as tf

from typing import List
import os

from app.prediction.architecture import ErrorF1Score
from app.db.database import engine
from app.features.users import models

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)
os.makedirs("app/static/images", exist_ok=True)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


OPTIMAL_THRESHOLDS = np.array([0.4, 0.45, 0.45, 0.35, 0.4, 0.45])

"""
Hiding Face Optimal thresholds per keypoint: [0.4  0.45 0.45 0.35 0.4  0.45]
Torso Rotation Optimal thresholds per keypoint: [0.35 0.55 0.35 0.3  0.45 0.3 ]
Flank Stretch Optimal thresholds per keypoint: [0.5  0.6  0.55 0.35 0.35 0.5 ]
"""

try:
    custom_objects = {"error_f1": ErrorF1Score}
    model = tf.keras.models.load_model(
        "models/run_13.keras",
        custom_objects=custom_objects,
    )
    os.system("clear")
    print("LSTM model loaded successfully!")
except Exception as e:
    os.system("clear")
    print(f"Error loading model: {e}")
    model = None


class PoseSequence(BaseModel):
    list_landmarks: List[List[float]]


@app.get("/")
def health_check():
    return {"message": "API is running well"}


@app.post("/api/predict/")
def index(landmarks: PoseSequence):
    np_landmarks = np.array(landmarks.list_landmarks, dtype="float32").reshape(
        1, 20, 42
    )

    np.set_printoptions(precision=3, suppress=True)

    raw_pred = model.predict(np_landmarks)
    binary_pred = (raw_pred >= OPTIMAL_THRESHOLDS).astype(int)

    return {"prediction": binary_pred.tolist()}


from app.features.users.routes import router as users_router

app.include_router(users_router)
