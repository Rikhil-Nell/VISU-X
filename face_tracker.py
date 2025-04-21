import asyncio
import cv2
from deepface import DeepFace
import os
import time # Optional: for performance timing

# ----------- Config ----------- #
# Using parameters similar to your standalone script
DB_PATH = "db"  # Ensure this path is correct relative to where main.py runs
MODEL = "VGG-Face"
DETECTOR = "opencv" # opencv, ssd, dlib, mtcnn, retinaface, mediapipe
NORMALIZATION = "base"
DISTANCE_METRIC = "cosine" # cosine, euclidean, euclidean_l2
FRAME_INTERVAL = 5  # Process one frame every N frames captured. Adjust as needed.
YIELD_SLEEP = 0.01 # Small sleep to prevent hogging CPU and allow event loop to run
# ------------------------------ #

current_user_id = "unknown_user"
processing_active = False # Flag to prevent concurrent processing runs if needed

async def face_loop():
    """
    Continuously captures frames, identifies users asynchronously every N frames,
    and updates the global current_user_id.
    """
    global current_user_id, processing_active
    cap = None # Initialize cap outside try
    frame_count = 0
    print(f"[INFO] Face Tracker: Initializing camera and starting loop (Processing every {FRAME_INTERVAL} frames)...")

    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("[ERROR] Face Tracker: Cannot open camera.")
            return # Exit if camera cannot be opened

        while True:
            ret, frame = cap.read()
            if not ret:
                print("[WARN] Face Tracker: Failed to grab frame. Retrying...")
                await asyncio.sleep(0.5) # Wait a bit before retrying
                continue

            frame_count += 1

            # Only process every Nth frame AND ensure previous processing isn't still running (optional safety)
            if frame_count % FRAME_INTERVAL == 0 and not processing_active:
                processing_active = True # Set flag
                # start_time = time.time() # Optional: for timing
                try:
                     # Run blocking DeepFace call in a separate thread
                    user_id = await asyncio.to_thread(identify_user, frame)
                    # end_time = time.time() # Optional: for timing
                    # print(f"[DEBUG] Face Tracker: Identify took {end_time - start_time:.2f}s. Result: {user_id}") # Optional

                    # Update global only if different to avoid unnecessary prints/updates downstream
                    if current_user_id != user_id:
                         print(f"[INFO] Face Tracker: Active user changed to: {user_id}")
                         current_user_id = user_id

                except Exception as e:
                    # Catch exceptions during the identify_user call itself
                    print(f"[ERROR] Face Tracker: Exception during identify_user execution: {e}")
                    current_user_id = "error_state" # Indicate an error occurred
                finally:
                    processing_active = False # Reset flag regardless of outcome


            # Yield control to the asyncio event loop briefly in *every* iteration
            # This prevents this loop from starving other async tasks.
            await asyncio.sleep(YIELD_SLEEP)

    except asyncio.CancelledError:
        print("[INFO] Face Tracker: Loop cancelled.")
    except Exception as e:
        print(f"[ERROR] Face Tracker: An unexpected error occurred in face_loop: {e}")
    finally:
        print("[INFO] Face Tracker: Releasing camera.")
        if cap:
            cap.release()

def identify_user(frame):
    """
    Synchronous function to run DeepFace.find.
    Designed to be called via asyncio.to_thread.
    """
    # Note: Parameters are now taken from the Config section above
    global current_user_id # Access global to return current if analysis fails badly
    try:
        results = DeepFace.find(
            img_path=frame,             # Pass the captured frame directly
            db_path=DB_PATH,
            model_name=MODEL,
            distance_metric=DISTANCE_METRIC,
            detector_backend=DETECTOR,
            normalization=NORMALIZATION,
            enforce_detection=False,    # Don't error if no face detected initially
            silent=True                 # Suppress DeepFace's internal console output
        )
        # DeepFace.find returns a list of dataframes, one per face found in img_path
        # We focus on the first dataframe (results[0]) assuming one primary user
        if results and not results[0].empty:
            # Get the path of the identified image in the database
            identity_path = results[0].iloc[0]['identity']
            # Extract the user ID (directory name) from the path
            user_id = os.path.basename(os.path.dirname(identity_path))
            return user_id
        else:
            # No face matched in the database
            return "unknown_user"
    except ValueError as ve:
         # Often indicates no face was detected *at all* in the frame by the detector backend
         # print(f"[DEBUG] DeepFace ValueError (likely no face detected): {ve}") # Optional Debug
         return current_user_id # Return the *last known* user instead of "unknown" if no face is visible momentarily
    except Exception as e:
        print(f"[ERROR] Face Tracker: DeepFace.find error: {e}")
        return "error_user" # Indicate a more severe error during analysis

def get_current_user():
    """Returns the latest identified user ID."""
    return current_user_id

# Example of how to run this standalone for testing (optional)
async def main_test():
    print("Starting face tracker test...")
    task = asyncio.create_task(face_loop())
    try:
        await asyncio.sleep(60) # Run for 60 seconds
    finally:
        print("Stopping face tracker test...")
        task.cancel()
        await task

if __name__ == "__main__":
     asyncio.run(main_test())