from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    File,
    UploadFile,
    Form,
    HTTPException,
)
from numpy.typing import ArrayLike, NDArray
import numpy as np

import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Union

from app.prediction.architecture import model
from app.prediction.schemas import (
    PoseSequence,
    WebsocketMessage,
    ConfigPayload,
    FramePayload,
)

router = APIRouter(prefix="/predict", tags=["lstm"])

OPTIMAL_THRESHOLDS_DICT = {
    "hiding_face": np.array([0.4, 0.45, 0.45, 0.35, 0.4, 0.45]),
    "torso_rotation": np.array([0.35, 0.55, 0.35, 0.3, 0.45, 0.3]),
    "flank_stretch": np.array([0.5, 0.6, 0.55, 0.35, 0.35, 0.5]),
}

SESSION_DATA_CACHE: Dict[str, Dict] = {}


@router.post("/api/predict/")
def get_prediction(sequence: PoseSequence):
    """
    This is the endpoint for real-time form correction during a user session.
    It is not used for dataset recording.
    """

    threshold: ArrayLike = OPTIMAL_THRESHOLDS_DICT.get(
        sequence.exercise_name, OPTIMAL_THRESHOLDS_DICT["hiding_face"]
    )

    np_landmarks: ArrayLike = np.array(
        sequence.list_landmarks, dtype="float32"
    ).reshape(1, 20, 42)

    if model:
        print("Model loaded")
    else:
        print("Model empty")

    raw_pred: NDArray = model.predict(np_landmarks)
    binary_pred: NDArray = (raw_pred >= threshold).astype(int)
    return {"prediction": binary_pred.tolist()}


@router.websocket("/api/ws/create-dataset")
async def websocket_create_dataset_entry(websocket: WebSocket):
    """
    Handles the real-time streaming of landmark data from the frontend.
    It populates a cache entry which is later used by the HTTP upload endpoint.
    """
    await websocket.accept()
    print("INFO:\tWebSocket connection opened.")

    session_key: Union[str, None] = None

    try:
        while True:
            data = await websocket.receive_json()
            message = WebsocketMessage(**data)

            if message.event == "config":
                if isinstance(message.payload, ConfigPayload):
                    config = message.payload
                    session_key = config.filename
                    SESSION_DATA_CACHE[session_key] = {"config": config, "frames": {}}
                    print(f"INFO:\tReceived config for session: {session_key}")

            elif message.event == "frame":
                if (
                    session_key
                    and session_key in SESSION_DATA_CACHE
                    and isinstance(message.payload, FramePayload)
                ):
                    frame = message.payload
                    SESSION_DATA_CACHE[session_key]["frames"][
                        frame.timestamp
                    ] = frame.landmarks

    except WebSocketDisconnect:
        print(f"INFO:\tClient disconnected WebSocket for session: {session_key}.")
        if session_key and session_key in SESSION_DATA_CACHE:
            del SESSION_DATA_CACHE[session_key]
            print(f"INFO:\tCleaned up orphaned cache for session: {session_key}")

    except Exception as e:
        print(f"ERROR:\tAn error occurred on WebSocket for session {session_key}: {e}")
    finally:
        print("INFO:\tWebSocket connection closed.")


@router.post("/api/upload-video-and-finalize")
async def upload_video_and_finalize_dataset(
    video_file: UploadFile = File(...),
    filename: str = Form(...),
    exercise: str = Form(...),
    category: str = Form(...),
):
    session_key = filename
    if not session_key or session_key not in SESSION_DATA_CACHE:
        raise HTTPException(
            status_code=404,
            detail=f"No active recording session found for filename: {session_key}. Please start recording again.",
        )

    print(f"INFO:\tFinalizing session for: {session_key}")
    session_data = SESSION_DATA_CACHE[session_key]

    base_filename = filename.replace(".json", "")
    dataset_dir = Path("/app/datasets")
    save_dir = dataset_dir / exercise / category
    video_dir = save_dir / "video"
    save_dir.mkdir(parents=True, exist_ok=True)
    video_dir.mkdir(parents=True, exist_ok=True)

    json_save_path = save_dir / filename
    mp4_video_path = video_dir / f"{base_filename}.mp4"

    final_json_to_save = {"positions": session_data["frames"]}
    try:
        with open(json_save_path, "w") as f:
            json.dump(final_json_to_save, f, indent=4)
        print(f"SUCCESS:\tSaved landmark data to {json_save_path}")
    except Exception as e:
        del SESSION_DATA_CACHE[session_key]
        raise HTTPException(status_code=500, detail=f"Failed to save JSON file: {e}")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
            shutil.copyfileobj(video_file.file, tmp)
            temp_webm_path = Path(tmp.name)

        ffmpeg_command = [
            "ffmpeg",
            "-i",
            str(temp_webm_path),
            "-vf",
            "hflip",
            "-c:v",
            "libx264",
            "-crf",
            "18",
            "-preset",
            "fast",
            "-an",
            "-y",
            str(mp4_video_path),
        ]

        print("INFO:\tRunning FFMPEG to convert and mirror...")
        subprocess.run(ffmpeg_command, check=True, capture_output=True, text=True)
        print(f"SUCCESS:\tCreated mirrored video: {mp4_video_path}")

    except subprocess.CalledProcessError as e:
        print("ERROR:\tFFMPEG process failed.")
        print("FFMPEG Stderr:", e.stderr)
        raise HTTPException(
            status_code=500, detail=f"ffmpeg conversion failed: {e.stderr}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Unexpected error during video processing: {e}"
        )
    finally:
        if "temp_webm_path" in locals() and temp_webm_path.exists():
            temp_webm_path.unlink()
            print(f"INFO:\tCleaned up temporary file: {temp_webm_path}")
        if session_key in SESSION_DATA_CACHE:
            del SESSION_DATA_CACHE[session_key]
            print(f"INFO:\tCleaned up cache for {session_key}")

    return {"message": "Dataset entry and mirrored video saved successfully."}
