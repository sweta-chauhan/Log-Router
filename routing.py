from fastapi import APIRouter

from log_router.controller.user_log import UserLog

app_router = APIRouter(prefix="/user")

app_router.add_api_route("/log", UserLog.post, methods=["POST"])
# app_router.add_api_route("/log", UserLog.get, methods=["GET"])
