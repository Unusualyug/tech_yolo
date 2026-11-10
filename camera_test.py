import cv2
import os
import time

from trinexis_core import camera_config

_CAMERA_CONFIG = camera_config(os.environ)
_BACKEND_NAME = _CAMERA_CONFIG["backend"]
_BACKEND = {
    "AUTO": cv2.CAP_ANY,
    "DSHOW": getattr(cv2, "CAP_DSHOW", cv2.CAP_ANY),
    "MSMF": getattr(cv2, "CAP_MSMF", cv2.CAP_ANY),
    "V4L2": getattr(cv2, "CAP_V4L2", cv2.CAP_ANY),
}.get(_BACKEND_NAME, cv2.CAP_ANY)

print("=" * 60)
print("TRINEXIS CAMERA DETECTOR")
print("=" * 60)

found = []

for index in range(10):

    print(f"\nTesting camera index {index}...")

    cap = cv2.VideoCapture(
        index,
        _BACKEND
    )

    if not cap.isOpened():

        print("  [X] Cannot open")
        cap.release()
        continue

    cap.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        1280
    )

    cap.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        720
    )

    # Give the selected backend time to initialize.
    time.sleep(1)

    valid_frames = 0
    brightness = []

    for _ in range(10):

        ret, frame = cap.read()

        if ret and frame is not None:

            valid_frames += 1

            gray = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2GRAY
            )

            brightness.append(
                float(gray.mean())
            )

        time.sleep(0.05)

    if valid_frames == 0:

        print(
            "  [X] Camera opened but "
            "returned NO frames"
        )

        cap.release()
        continue

    avg_brightness = (
        sum(brightness)
        / len(brightness)
    )

    print(
        f"  Frames: {valid_frames}/10"
    )

    print(
        f"  Brightness: {avg_brightness:.2f}"
    )

    if avg_brightness < 3:

        print(
            "  [!] Camera appears BLACK"
        )

    else:

        print(
            "  [✓] VALID CAMERA"
        )

        found.append(index)


    cap.release()


print("\n" + "=" * 60)
print("RESULT")
print("=" * 60)

if found:

    print(
        "Working camera indexes:",
        found
    )

    print()
    print(
        "Use the EXTERNAL webcam index "
        "in app.py."
    )

else:

    print(
        "NO VALID CAMERA FOUND."
    )

print("=" * 60)