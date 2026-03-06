from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


# 成功响应
def success_response(message: str = "success", data=None):
    # 任何的fastapi、pydantic、orm对象类型都可正常响应
    content = {
        "code": 200,
        "message": message,
        "data": data
    }
    return JSONResponse(content=jsonable_encoder(content))


# 错误响应
def error_response(message: str = "error", data=None):
    content = {
        "code": 400,
        "message": message,
        "data": data
    }
    return JSONResponse(content=jsonable_encoder(content))
