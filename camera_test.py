import cv2
import time

print("=" * 60)
print("TRINEXIS CAMERA DETECTOR")
print("=" * 60)

found = []

for index in range(10):

    print(f"\nTesting camera index {index}...")

    cap = cv2.VideoCapture(
        index,
        cv2.CAP_DSHOW
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

    # Give DirectShow time to initialize
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