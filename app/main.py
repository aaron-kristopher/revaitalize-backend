from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from psycopg2.extras import RealDictCursor
from pydantic_settings import BaseSettings
import numpy as np
import psycopg2
import tensorflow as tf

from typing import List, Union
import os
import time

from app.prediction.architecture import ErrorF1Score


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


class DbStatus(BaseModel):
    status: str
    db_version: Union[str, None] = None


class Settings(BaseSettings):
    database_url: str

    class Config:
        env_file = ".env"


settings = Settings()


def get_db_connect():
    while True:
        try:
            conn = psycopg2.connect(
                settings.database_url, cursor_factory=RealDictCursor
            )
            print("SUCCESS: Database connection established.")
            return conn
        except Exception as error:
            print("FAILED: Database connection failed.")
            print(f"ERROR: {error}")
            time.sleep(2)


@app.get("/")
def read_root():
    return {"message": "Welcome to RevAItalize API"}


@app.get("/api/db-check", response_model=DbStatus)
def db_check():
    """
    A simple endpoint to check database connection
    """

    try:
        conn = get_db_connect()
        cursor = conn.cursor()

        cursor.execute("SELECT version()")
        db_version_row = cursor.fetchone()

        cursor.close()
        conn.close()

        db_version_string = db_version_row["version"] if db_version_row else "unknown"

        return {"status": "ok", "db_version": db_version_string}
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection error: {error}",
        )


@app.post("/api/predict/")
def index(landmarks: PoseSequence):
    np_landmarks = np.array(landmarks.list_landmarks, dtype="float32").reshape(
        1, 20, 42
    )

    np.set_printoptions(precision=3, suppress=True)

    raw_pred = model.predict(np_landmarks)
    binary_pred = (raw_pred >= OPTIMAL_THRESHOLDS).astype(int)

    return {"prediction": binary_pred.tolist()}
