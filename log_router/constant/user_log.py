import os

EVENT_NAME = ["login", "logout"]
DATA_DUMP_INTERVAL = 30  # 30 Second
DATA_DUMP_FILE_SIZE_THRESHOLD = 10 * 1024 * 1024  # 10MB
CHUNK_SIZE = 2000

def get_local_dump_path(nested=False):
    current_path = os.getcwd()
    if nested:
        current_path = os.path.dirname(current_path)
        current_path = os.path.dirname(current_path)

    return f"{current_path}/local_dump/"


LOG_FILE = f"user_log.json"
ALTERNATE_LOG_FILE = f"temp_user_log.json"
FAILED_INSERTION_LOG_FILE = f"failed_insert_user_log.json"
