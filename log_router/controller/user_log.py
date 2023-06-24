from fastapi.responses import JSONResponse
from marshmallow import ValidationError
from pydantic import BaseModel

from log_router.common.file_handler import add_log_data_to_file, read_log_data
from log_router.common.utils import generate_error_list
from log_router.constant.user_log import (
    ALTERNATE_LOG_FILE,
    LOG_FILE,
    get_local_dump_path,
)
from log_router.serializor.user_log import UserLogRequestSchema


class LogPayload(BaseModel):
    id: int
    unix_ts: int
    user_id: int
    event_name: str


LOCAL_DUMP_FOLDER = get_local_dump_path()
LOG_FILE = f"{LOCAL_DUMP_FOLDER}{LOG_FILE}"
ALTERNATE_LOG_FILE = f"{LOCAL_DUMP_FOLDER}{ALTERNATE_LOG_FILE}"


class UserLog:
    @staticmethod
    async def post(request: LogPayload):
        try:
            request_body = request.json()
            UserLogRequestSchema().loads(request_body)
            # logic to write data in file buffer or in event stream

            await add_log_data_to_file(LOG_FILE, ALTERNATE_LOG_FILE, request_body)
            return JSONResponse(
                {"message": "User log created successfully"}, status_code=201
            )

        except ValidationError as excp:
            error = generate_error_list(excp.messages)
            return JSONResponse({"error": error}, status_code=400)

    @staticmethod
    async def get():
        data = read_log_data(LOG_FILE)
        return JSONResponse({"message": "success", "data": data}, status_code=200)
