from rest_framework import status
from rest_framework.exceptions import NotAuthenticated
from rest_framework.views import exception_handler
from rest_framework.response import Response

result = {"meta": {"code": "", "message": ""}, "data": ""}


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    global result
    if response != None:
        if response.status_code == 401:
            result["meta"]["code"] = status.HTTP_401_UNAUTHORIZED
            result["meta"]["message"] = "해당 API를 사용할 권한이 없습니다."
            result["data"] = "null"
            return Response(
                result,
                status=status.HTTP_401_UNAUTHORIZED,
            )
        else:
            result["meta"]["code"] = status.HTTP_400_BAD_REQUEST
            result["meta"]["message"] = "데이터 형식에 맞게 채워주세요."
            result["data"] = "null"
            return Response(
                result,
                status=status.HTTP_400_BAD_REQUEST,
            )
