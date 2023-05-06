import rest_framework_simplejwt
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from rest_framework import status
from django.db import IntegrityError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from account.serializers import SignupSerializer, LoginSerializer

User = get_user_model()
result = {"meta": {"code": "", "message": ""}, "data": ""}


class SignupView(APIView):
    queryset = User.objects.all()
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        global result

        if serializer.is_valid():
            user = serializer.save()
            result["meta"]["code"] = status.HTTP_201_CREATED
            result["meta"]["message"] = "ok"
            result["data"] = serializer.data
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            if "phone_number" in serializer.errors:
                if (
                    "형식" in serializer.errors["phone_number"][0]
                    or "필수" in serializer.errors["phone_number"][0]
                ):
                    result["meta"]["code"] = status.HTTP_400_BAD_REQUEST
                    result["meta"]["message"] = serializer.errors
                    result["data"] = "null"
                    return Response(result, status=status.HTTP_400_BAD_REQUEST)
                else:
                    result["meta"]["code"] = status.HTTP_409_CONFLICT
                    result["meta"]["message"] = "이미 존재하는 번호입니다."
                    result["data"] = "null"
                    return Response(result, status=status.HTTP_409_CONFLICT)
            else:
                result["meta"]["code"] = status.HTTP_400_BAD_REQUEST
                result["meta"]["message"] = serializer.errors
                result["data"] = "null"
                return Response(result, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    queryset = User.objects.all()
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        global result

        if serializer.is_valid():
            result["meta"]["code"] = status.HTTP_200_OK
            result["meta"]["message"] = "ok"
            result["data"] = serializer.validated_data
            return Response(result, status=status.HTTP_200_OK)
        else:
            result["meta"]["code"] = status.HTTP_401_UNAUTHORIZED
            result["meta"]["message"] = serializer.errors
            result["data"] = "null"
            return Response(result, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data["refresh_token"]
        phone_number = request.data["phone_number"]
        global result

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            result["meta"]["code"] = status.HTTP_200_OK
            result["meta"]["message"] = "ok"
            result["data"] = phone_number
            return Response(result, status=status.HTTP_200_OK)

        except rest_framework_simplejwt.exceptions.TokenError:
            result["meta"]["code"] = status.HTTP_401_UNAUTHORIZED
            result["meta"]["message"] = "refresh_token이 유효하지 않거나 만료되었습니다."
            result["data"] = "null"
            return Response(result, status=status.HTTP_401_UNAUTHORIZED)
