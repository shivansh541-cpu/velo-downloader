import os
import time


def clean_old_files(folder, max_age_seconds=3600):
    try:
        now = time.time()
        for filename in os.listdir(folder):
            filepath = os.path.join(folder, filename)
            if os.path.isfile(filepath):
                file_age = now - os.path.getmtime(filepath)
                if file_age > max_age_seconds:
                    os.remove(filepath)
    except Exception as e:
        print(f"Cleaner error: {e}")


def delete_file_after_delay(filepath, delay=60):
    time.sleep(delay)
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        print(f"Delete error: {e}")