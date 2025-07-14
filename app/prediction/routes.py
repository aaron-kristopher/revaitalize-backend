from fastapi import APIRouter, HTTPException, Response, status
from numpy.typing import ArrayLike, NDArray
import numpy as np

import json
from pathlib import Path
from typing import Dict, List

from app.prediction.architecture import model
from app.prediction.schemas import PoseSequence, DatasetBase

router = APIRouter(prefix="/predict", tags=["lstm"])


OPTIMAL_THRESHOLDS_DICT = {
    "hiding_face": np.array([0.4, 0.45, 0.45, 0.35, 0.4, 0.45]),
    "torso_rotation": np.array([0.35, 0.55, 0.35, 0.3, 0.45, 0.3]),
    "flank_stretch": np.array([0.5, 0.6, 0.55, 0.35, 0.35, 0.5]),
}


@router.post("/api/predict/")
def get_prediction(sequence: PoseSequence) -> Dict[str, List[float]]:

    # If no exercise name is provided, uses threshold for hiding face as default
    threshold: ArrayLike = OPTIMAL_THRESHOLDS_DICT.get(
        sequence.exercise_name, OPTIMAL_THRESHOLDS_DICT["hiding_face"]
    )
    np_landmarks: ArrayLike = np.array(
        sequence.list_landmarks, dtype="float32"
    ).reshape(1, 20, 42)

    np.set_printoptions(precision=3, suppress=True)

    raw_pred: NDArray = model.predict(np_landmarks)  # pyright: ignore[]
    binary_pred: NDArray = (raw_pred >= threshold).astype(int)

    return {"prediction": binary_pred.tolist()}


@router.post("/api/create-dataset")
def create_dataset_entry(payload: DatasetBase):
    correctness = "incorrect" if payload.is_incorrect else "correct"

    dataset_dir: Path = Path(__file__).resolve().parent.parent
    save_path: Path = dataset_dir / payload.exercise / correctness / payload.filename

    save_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(save_path, "w") as f:
            json.dump(payload.model_dump, f, indent=2)

    except Exception as error:
        print("Error in saving payload to file: ", error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in saving payload to file: {error}",
        )

    return Response(status_code=status.HTTP_201_CREATED)
