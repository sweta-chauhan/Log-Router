import asyncio
import fcntl
import json
import os.path


def is_file_locked(file_path):
    try:
        file = open(file_path, "r")
        fcntl.lockf(file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        print(f"Lock check .....{file_path}")
        file.close()
    except IOError as e:
        return True

    return False


async def add_log_data_to_file(filename, alternate_filename, data):
    if os.path.exists(filename):
        print("Main LOG file is locked....", is_file_locked(filename))
        print("Temp LOG file is locked...", is_file_locked(alternate_filename))
        if not is_file_locked(filename):
            await data_dump(filename, data)
        else:
            await data_dump(alternate_filename, data)
    else:
        await data_dump(filename, data)


async def data_dump(filename, data):
    lock = await acquire_file_lock(filename)
    try:
        await append_to_file(filename, data, "a+")
    finally:
        release_file_lock(lock)


async def acquire_file_lock(filename):
    directory = os.path.dirname(filename)
    os.makedirs(directory, exist_ok=True)
    file = await asyncio.to_thread(open, filename, "a")
    try:
        fcntl.lockf(file, fcntl.LOCK_EX)
        return file
    except IOError:
        file.close()
        raise


def release_file_lock(file):
    fcntl.lockf(file, fcntl.LOCK_UN)  # Release the lock
    file.close()


async def append_to_file(filename, data, mode="a+"):
    with open(filename, mode) as file:
        file.write(data + "\n")


def read_log_data(filename):
    json_data = []
    with open(filename, "r") as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip()
            if line:
                try:
                    json_obj = json.loads(line)
                    json_data.append(json_obj)
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")

    return json_data


def clear_log_file(filename):
    with open(filename, "w") as file:
        file.truncate(0)
