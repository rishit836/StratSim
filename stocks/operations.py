import os
import time

def delete_if_outdated(filepath, max_age_seconds=60*60*24):
    if os.path.exists(filepath):
        last_modified_time = os.path.getmtime(filepath)
        
        current_time = time.time()
        if current_time - last_modified_time > max_age_seconds:
            os.remove(filepath)
            print(f"Deleted {filepath} (outdated)")
        else:
            print(f"{filepath} is still valid")
    else:
        print(f"{filepath} does not exist")