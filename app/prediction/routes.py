from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from numpy.typing import ArrayLike, NDArray
import numpy as np

import json
from typing import Union
from pathlib import Path


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


@router.post("/api/predict/")
def get_prediction(sequence: PoseSequence):

    # If no exercise name is provided, uses threshold for hiding face as default
    threshold: ArrayLike = OPTIMAL_THRESHOLDS_DICT.get(
        sequence.exercise_name, OPTIMAL_THRESHOLDS_DICT["hiding_face"]
    )
    np_landmarks: ArrayLike = np.array(
        sequence.list_landmarks, dtype="float32"
    ).reshape(1, 20, 42)

    np.set_printoptions(precision=3, suppress=True)

    raw_pred: NDArray = model.predict(np_landmarks)
    binary_pred: NDArray = (raw_pred >= threshold).astype(int)

    return {"prediction": binary_pred.tolist()}


@router.websocket("/api/ws/create-dataset")
async def websocket_create_dataset_entry(websocket: WebSocket):
    await websocket.accept()

    print("INFO:\tconnection open")

    config_data: Union[ConfigPayload, None] = None
    recorded_frames = {}

    try:
        while True:
            data = await websocket.receive_json()
            message = WebsocketMessage(**data)

            if message.event == "config":
                if isinstance(message.payload, ConfigPayload):
                    config_data = message.payload
                    print(f"Recieved config: {config_data.filename}")
                    recorded_frames = {}
                else:
                    await websocket.close(
                        code=status.WS_1008_POLICY_VIOLATION,
                        reason="Config message must be sent first.",
                    )
                    return

            elif message.event == "frame":
                if not config_data:
                    await websocket.close(
                        code=status.WS_1008_POLICY_VIOLATION,
                        reason="Config message must be sent first.",
                    )
                    return

                if isinstance(message.payload, FramePayload):
                    frame = message.payload
                    recorded_frames[frame.timestamp] = frame.landmarks

                else:
                    await websocket.close(
                        code=status.WS_1008_POLICY_VIOLATION,
                        reason="Config message must be sent first.",
                    )
                    return

            elif message.event == "end":
                if not config_data:
                    await websocket.close(
                        code=status.WS_1008_POLICY_VIOLATION,
                        reason="Config message must be sent first.",
                    )
                    return

                print(f"Received end event for: {config_data.filename}")

                dataset_dir_path: Path = Path(__file__).resolve().parent.parent
                save_path: Path = (
                    dataset_dir_path
                    / "datasets"
                    / config_data.exercise
                    / config_data.category
                )

                save_path.mkdir(parents=True, exist_ok=True)

                final_payload_to_save = {"positions": recorded_frames}

                try:
                    with open(f"{save_path}/{config_data.filename}", "w") as f:
                        json.dump(final_payload_to_save, f, indent=4)

                    await websocket.send_json(
                        {
                            "status": "success",
                            "message": f"File {config_data.filename} saved.",
                        }
                    )
                    print(f"Successfully saved {config_data.filename}.")

                except Exception as error:
                    await websocket.send_json(
                        {"status": "error", "message": str(error)}
                    )
                    print(f"Error saving file: {error}")

                break

    except WebSocketDisconnect:
        print("INFO:\tClient disconnected.")

    except Exception as e:
        print(f"INFO:\tAn unexpected error occured: {e}")

    finally:
        if websocket.client_state != "DISCONNECTED":
            await websocket.close()
        print("INFO:\tWebsocket connection closed.")
