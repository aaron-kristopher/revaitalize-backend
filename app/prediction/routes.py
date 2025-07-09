from fastapi import APIRouter
import numpy as np


from app.prediction.architecture import model
from app.prediction.schemas import PoseSequence

router = APIRouter(prefix="/predict", tags=["lstm"])


OPTIMAL_THRESHOLDS_DICT = {
    "hiding_face": np.array([0.4, 0.45, 0.45, 0.35, 0.4, 0.45]),
    "torso_rotation": np.array([0.35, 0.55, 0.35, 0.3, 0.45, 0.3]),
    "flank_stretch": np.array([0.5, 0.6, 0.55, 0.35, 0.35, 0.5]),
}


@router.post("/api/predict/")
def index(sequence: PoseSequence):

    # If no exercise name is provided, uses threshold for hiding face as default
    threshold = OPTIMAL_THRESHOLDS_DICT.get(
        sequence.exercise_name, OPTIMAL_THRESHOLDS_DICT["hiding_face"]
    )
    np_landmarks = np.array(sequence.list_landmarks, dtype="float32").reshape(1, 20, 42)

    np.set_printoptions(precision=3, suppress=True)

    raw_pred = model.predict(np_landmarks)
    binary_pred = (raw_pred >= threshold).astype(int)

    return {"prediction": binary_pred.tolist()}
