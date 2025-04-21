import cv2
from deepface import DeepFace
import os

# ----------- Config ----------- #
DB_PATH = "db"  # adjust relative to script location
MODEL = "VGG-Face"
DETECTOR = "opencv"
NORMALIZATION = "base"
DISTANCE_METRIC = "cosine"
FRAME_INTERVAL = 10
THRESHOLD = None  # use model default
# ------------------------------ #

cap = cv2.VideoCapture(0)
frame_count = 0

print("[INFO] Starting face recognition stream (headless). Press Ctrl+C to quit.")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to grab frame.")
            break

        # === Optional: Show live camera feed ===
        # cv2.imshow("Live Feed", frame)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

        frame_count += 1

        if frame_count % FRAME_INTERVAL == 0:
            try:
                results = DeepFace.find(
                    img_path=frame,
                    db_path=DB_PATH,
                    model_name=MODEL,
                    distance_metric=DISTANCE_METRIC,
                    detector_backend=DETECTOR,
                    normalization=NORMALIZATION,
                    enforce_detection=False,
                    silent=True
                )
                if results and not results[0].empty:
                    identity_path = results[0].iloc[0]["identity"]
                    label = os.path.basename(os.path.dirname(identity_path))
                    print(f"[MATCH] Detected: {label}")
                else:
                    print("[INFO] No match found.")
            except Exception as e:
                print(f"[ERROR] DeepFace failed: {e}")

except KeyboardInterrupt:
    print("\n[INFO] Interrupted by user.")

finally:
    cap.release()
    # cv2.destroyAllWindows()
