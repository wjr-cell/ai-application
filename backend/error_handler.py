from fastapi import Request
from fastapi.responses import JSONResponse

from logger import logger


async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"请求处理失败：{request.method} {request.url.path}")

    return JSONResponse(
        status_code=500,
        content={
            "error": "服务器内部错误",
            "message": "服务器处理请求时发生错误，请查看日志。",
        },
    )
