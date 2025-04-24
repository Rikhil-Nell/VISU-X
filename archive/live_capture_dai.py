import depthai as dai
import cv2
from deepface import DeepFace
import os

# ----------- Config ----------- #
DB_PATH = "db"
MODEL = "Facenet512"
DETECTOR = "opencv"
NORMALIZATION = "base"
DISTANCE_METRIC = "cosine"
FRAME_INTERVAL = 10
THRESHOLD = 0.7  # Adjust if needed
# ------------------------------ #

# === DepthAI Pipeline Setup ===
pipeline = dai.Pipeline()
cam_rgb = pipeline.createColorCamera()
cam_rgb.setPreviewSize(640, 480)
cam_rgb.setInterleaved(False)
cam_rgb.setBoardSocket(dai.CameraBoardSocket.RGB)

xout_rgb = pipeline.createXLinkOut()
xout_rgb.setStreamName("rgb")
cam_rgb.preview.link(xout_rgb.input)

frame_count = 0

print("[INFO] Starting DepthAI + DeepFace face recognition. Press Ctrl+C to quit.")

with dai.Device(pipeline) as device:
    q_rgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)

    try:
        while True:
            in_rgb = q_rgb.get()
            frame = in_rgb.getCvFrame()
            frame_count += 1

            # Uncomment to visualize feed
            # cv2.imshow("DepthAI Feed", frame)
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break

            if frame_count % FRAME_INTERVAL == 0:
                try:
                    results = DeepFace.find(
                        img_path=frame,
                        db_path=DB_PATH,
                        model_name=MODEL,
                        distance_metric=DISTANCE_METRIC,
                        detector_backend=DETECTOR,
                        normalization=NORMALIZATION,
                        threshold=THRESHOLD,
                        enforce_detection=False,
                        silent=True
                    )
                    if results and not results[0].empty:
                        identity_path = results[0].iloc[0]["identity"]
                        label = os.path.basename(os.path.dirname(identity_path))
                        with open("user_id.txt", "w") as f:
                            f.write(label)
                        print(f"[MATCH] Detected: {label}")
                    else:
                        print("[INFO] No match found.")

                except Exception as e:
                    print(f"[ERROR] DeepFace failed: {e}")

    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user.")

    finally:
        cv2.destroyAllWindows()
