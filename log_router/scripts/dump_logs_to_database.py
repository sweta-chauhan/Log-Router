import asyncio
import logging
import os
import time

from log_router.common.backend import Database
from log_router.common.file_handler import (
    acquire_file_lock,
    append_to_file,
    clear_log_file,
    read_log_data,
    release_file_lock,
)
from log_router.common.utils import chunks
from log_router.constant.user_log import (
    ALTERNATE_LOG_FILE,
    CHUNK_SIZE,
    DATA_DUMP_FILE_SIZE_THRESHOLD,
    DATA_DUMP_INTERVAL,
    FAILED_INSERTION_LOG_FILE,
    LOG_FILE,
    get_local_dump_path,
)
from log_router.models.user_log import UserLogModel
from log_router.serializor.user_log import UserLogSchema

# Configure the logger
logging.basicConfig(
    level=logging.INFO,  # Set the desired log level
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Set the log message format
)

# Create a logger instance
logger = logging.getLogger(__name__)
LOCAL_DUMP_FOLDER = get_local_dump_path(nested=False)
MAIN_LOG_FILE = f"{LOCAL_DUMP_FOLDER}{LOG_FILE}"
ALTERNATE_TEMP_LOG_FILE = f"{LOCAL_DUMP_FOLDER}{ALTERNATE_LOG_FILE}"
FAILED_INSERTION_LOG_FILE = f"{LOCAL_DUMP_FOLDER}{FAILED_INSERTION_LOG_FILE}"


async def prepare_data_for_dumping_into_database(
    log_dataset, fallback_bath, chunk_size=1000
):
    chunk_counter = 0
    logger.info("Length of log_dataset : {}".format(log_dataset))
    for log_data_chunk in chunks(log_dataset, chunk_size):
        user_log_data_list = []
        logger.info(
            f"Processing Data in chunk size: {chunk_size}, Batch no : {chunk_counter + 1}"
        )
        chunk_counter += 1
        for log_data in log_data_chunk:
            log_id = log_data.pop("id")
            user_id = log_data["user_id"]
            timestamp = log_data["unix_ts"]
            event_name = log_data["event_name"]
            user_log = {"uid": f"{user_id}|{timestamp}|{event_name}", "log_id": log_id}
            log_data.update(user_log)
            user_log_obj = UserLogModel(**log_data)
            user_log_data_list.append(user_log_obj)
        logger.info(
            f"Dumping data in chunk size: {chunk_size}, Batch no : {chunk_counter+1} into DB"
        )
        try:
            session = Database().get_session()
            session.bulk_save_objects(user_log_data_list)
            session.commit()
            session.close()
        except:
            # dump data with error info to handle fallback
            await dump_failed_batch_to_fallback_file(fallback_bath, user_log_data_list)
            pass


async def dump_failed_batch_to_fallback_file(fallback_bath, user_log_data_list):
    with open(fallback_bath, "a+") as file:
        data = "\n".join(
            [UserLogSchema().dumps(user_log) for user_log in user_log_data_list]
        )
        file.write(data)


async def dump_data_to_db_from_file(
    filename, alternate_file_name, fallback_bath, chunk_size=2000
):
    logger.info(f"Reading log from file: {filename}")
    data_for_dumping = read_log_data(filename)
    if data_for_dumping:
        await prepare_data_for_dumping_into_database(
            data_for_dumping, fallback_bath, chunk_size
        )
        logger.info(f"Passing Data for processing in chunk size: {chunk_size}")
        logger.info(f"Now acquiring lock on primary log file: {filename}")
        lock = await acquire_file_lock(filename)
        try:
            logger.info(f"Now Reading data on primary log file: {filename}")
            available_data_in_file = read_log_data(filename)
            logger.info(f"Now Removing data on primary log file: {filename}")
            new_data = available_data_in_file[len(data_for_dumping) :]
            data_str = " ".join(new_data)
            await append_to_file(filename, data_str, mode="w")
        finally:
            logger.info(f"Now Releasing lock on primary log file: {filename}")
            release_file_lock(lock)

        if os.path.exists(alternate_file_name):
            # 5. acquire lock on temp file
            lock = await acquire_file_lock(alternate_file_name)
            try:
                # 6. take all entry from temp_logger file and
                available_data_in_temp_file = read_log_data(alternate_file_name)
                # 3. remove dumped data from log file
                clear_log_file(alternate_file_name)
                # 7. append them into main_logger file
                data_str = " ".join(available_data_in_temp_file)
                await append_to_file(filename, data_str, mode="a")
            finally:
                # 8. release lock from temp file as well
                release_file_lock(lock)


def check_conditions(filename, last_time):
    logger.info(f"File name is {filename}")
    logger.info(f"{filename}")
    if os.path.exists(filename):
        threshold = abs(last_time - os.path.getmtime(filename))
        logger.info(f"File: {filename} created in {threshold} seconds earlier")

        if threshold >= DATA_DUMP_INTERVAL:
            return True  # Run the script after 30 seconds

        file_size = os.path.getsize(filename)
        logger.info(f"File: {filename} size is :=> {file_size} ")

        if file_size > DATA_DUMP_FILE_SIZE_THRESHOLD:  # 10 MB in bytes
            return True  # Run the script when file size exceeds 10 MB

    return False


async def data_dump():
    last_time = time.time()
    while True:
        log_file_flag = check_conditions(MAIN_LOG_FILE, last_time)
        logger.info(f"Can be dumped...from main log file? {log_file_flag}")

        if log_file_flag:
            await dump_data_to_db_from_file(
                MAIN_LOG_FILE,
                ALTERNATE_TEMP_LOG_FILE,
                FAILED_INSERTION_LOG_FILE,
                chunk_size=CHUNK_SIZE,
            )

        temp_log_file_flag = check_conditions(ALTERNATE_TEMP_LOG_FILE, last_time)
        logger.info(f"Can be dumped...from temp log file? {temp_log_file_flag}")

        if temp_log_file_flag:
            await dump_data_to_db_from_file(
                ALTERNATE_TEMP_LOG_FILE,
                MAIN_LOG_FILE,
                FAILED_INSERTION_LOG_FILE,
                chunk_size=CHUNK_SIZE,
            )
            break
        last_time = time.time()
        time.sleep(30)


asyncio.run(data_dump())
