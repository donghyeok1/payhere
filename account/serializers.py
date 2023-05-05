from rest_framework import serializers
from django.contrib.auth import get_user_model
from account.validators import phone_number_regex, password_regex

User = get_user_model()
class PhoneNumberValidator:
    def __call__(self, value):
        if not bool(phone_number_regex.match(value)):
            raise serializers.ValidationError('핸드폰 번호 형식이 올바르지 않습니다.')

class PasswordValidator:
    def __call__(self, value):
        if not bool(password_regex.match(value)):
            raise serializers.ValidationError('비밀번호는 8글자 이상이며 특수문자, 숫자를 포함해야 합니다.')
class SignupSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(validators=[PhoneNumberValidator()])
    password = serializers.CharField(validators=[PasswordValidator()], write_only=True)
    class Meta:
        model = User
        fields = ('phone_number', 'password')

    def create(self, validated_data):
        phone_number = validated_data['phone_number']
        user_exists = User.objects.filter(phone_number=phone_number).exists()
        if not user_exists:
            user = User.objects.create_user(**validated_data)
            user.save()
            return user
        else:
            raise serializers.ValidationError('이미 존재하는 회원의 휴대폰 번호 입니다.')