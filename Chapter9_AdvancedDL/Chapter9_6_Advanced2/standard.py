import os
from typing import Tuple

import numpy as np
import tensorflow as tf
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.layers import Activation
from tensorflow.keras.layers import BatchNormalization
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import GlobalAveragePooling2D
from tensorflow.keras.layers import Input
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam

from tf_utils.mnistDataAdvanced import MNIST


np.random.seed(0)
tf.random.set_seed(0)


LOGS_DIR = os.path.abspath("C:/Users/Jan/OneDrive/_Coding/UdemyTF/logs/")
if not os.path.exists(LOGS_DIR):
    os.mkdir(LOGS_DIR)


def relu_norm(x: tf.Tensor) -> tf.Tensor:
    x = Activation("relu")(x)
    x = BatchNormalization()(x)
    return x


def conv_block(
    x: tf.Tensor, filters: int, downsample: bool = False
) -> tf.Tensor:
    x = Conv2D(
        filters=filters,
        strides=(1 if not downsample else 2),
        kernel_size=3,
        padding="same",
    )(x)
    x = relu_norm(x)
    x = Conv2D(filters=filters, strides=1, kernel_size=3, padding="same")(x)
    x = relu_norm(x)
    return x


def output_block(x: tf.Tensor, num_classes: int) -> tf.Tensor:
    x = GlobalAveragePooling2D()(x)
    x = Dense(units=num_classes)(x)
    x = Activation("softmax")(x)
    return x


def build_model_standard(
    img_shape: Tuple[int, int, int], num_classes: int
) -> Model:
    input_img = Input(shape=img_shape)

    x = conv_block(x=input_img, filters=32, downsample=False)
    x = conv_block(x=x, filters=64, downsample=True)
    x = conv_block(x=x, filters=64, downsample=False)
    x = conv_block(x=x, filters=128, downsample=True)
    x = conv_block(x=x, filters=128, downsample=False)
    y_pred = output_block(x=x, num_classes=num_classes)

    model = Model(inputs=[input_img], outputs=[y_pred])

    opt = Adam()

    model.compile(
        loss="categorical_crossentropy", optimizer=opt, metrics=["accuracy"]
    )

    return model


if __name__ == "__main__":
    data = MNIST()

    train_dataset = data.get_train_set()
    val_dataset = data.get_val_set()
    test_dataset = data.get_test_set()

    img_shape = data.img_shape
    num_classes = data.num_classes

    # Global params
    epochs = 100
    batch_size = 128

    model = build_model_standard(img_shape, num_classes)

    model.summary()

    model_log_dir = os.path.join(LOGS_DIR, "model_standard_mnist")

    es_callback = EarlyStopping(
        monitor="val_accuracy",
        patience=30,
        verbose=1,
        restore_best_weights=True,
        min_delta=0.0005,
    )

    model.fit(
        train_dataset,
        verbose=1,
        batch_size=batch_size,
        epochs=epochs,
        callbacks=[es_callback],
        validation_data=val_dataset,
    )

    scores = model.evaluate(val_dataset, verbose=0, batch_size=batch_size)
    print(f"Scores: {scores}")
