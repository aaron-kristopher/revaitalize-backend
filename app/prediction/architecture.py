import tensorflow as tf

import os
from typing import Union


@tf.keras.utils.register_keras_serializable()
class ErrorF1Score(tf.keras.metrics.Metric):
    def __init__(self, name="error_f1", **kwargs):
        super().__init__(name=name, **kwargs)
        self.precision = tf.keras.metrics.Precision(thresholds=0.5)
        self.recall = tf.keras.metrics.Recall(thresholds=0.5)

    def update_state(self, y_true, y_pred, sample_weight=None):
        self.precision.update_state(y_true, y_pred, sample_weight)
        self.recall.update_state(y_true, y_pred, sample_weight)

    def result(self):
        p = self.precision.result()
        r = self.recall.result()
        return 2 * ((p * r) / (p + r + tf.keras.backend.epsilon()))

    def reset_state(self):
        self.precision.reset_state()
        self.recall.reset_state()


try:
    custom_objects = {"error_f1": ErrorF1Score}
    model: Union[tf.keras.Model, None] = tf.keras.models.load_model(
        "models/finetuned_model.keras",
        custom_objects=custom_objects,
    )
    os.system("clear")
    if model:
        print("LSTM model loaded successfully!")
    else:
        print("Model empty")
except Exception as e:
    os.system("clear")
    print(f"Error loading model: {e}")
    model = None
