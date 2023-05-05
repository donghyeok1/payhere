from django.contrib.auth import get_user_model
from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from account.serializers import SignupSerializer

User = get_user_model()
class SignupView(CreateAPIView):
    model = User
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        response = super(SignupView, self).create(request, *args, **kwargs)
        data = {
            "meta": {
                "code": response.status_code,
                "message": "You have successfully created the account."
            },
            "data": response.data
        }

        response.data = data
        return response