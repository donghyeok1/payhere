from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from account.validators import phone_number_regex, password_regex
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("phone_number", "password")
        extra_kwargs = {"password": {"write_only": True}}

    def validate_phone_number(self, value):
        if not phone_number_regex.match(value):
            raise serializers.ValidationError("핸드폰 번호 형식이 올바르지 않습니다.")
        return value

    def validate_password(self, value):
        if not password_regex.match(value):
            raise serializers.ValidationError("비밀번호는 8글자 이상이며 특수문자, 숫자를 포함해야 합니다.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(max_length=20)
    password = serializers.CharField(max_length=30, write_only=True)

    class Meta:
        model = User
        fields = ["phone_number", "password"]

    def validate(self, data):
        phone_number = data.get("phone_number", None)
        password = data.get("password", None)
        if phone_number and password:
            user = authenticate(phone_number=phone_number, password=password)
            if user:
                token = TokenObtainPairSerializer.get_token(user)
                refresh_token = str(token)
                access_token = str(token.access_token)
            else:
                raise serializers.ValidationError(
                    {
                        "validation_error": "핸드폰 번호 또는 비밀번호를 잘못 입력했습니다. 입력하신 내용을 다시 확인해주세요."
                    }
                )

        results = {
            "phone_number": phone_number,
            "refresh_token": refresh_token,
            "access_token": access_token,
        }

        return results

    def validate_phone_number(self, value):
        if not phone_number_regex.match(value):
            raise serializers.ValidationError("핸드폰 번호 형식이 올바르지 않습니다.")
        return value
