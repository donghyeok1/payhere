from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db import connection
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)


class SignupAPITest(APITestCase):
    """
    유저 회원가입 테스트
    """

    User = get_user_model()

    # setUpTestData는 한번만 실행되기 때문에 로그인 테스트를 할 때에는 각 함수들이 실행될 때마다 실행되는 setUp을 씀.
    def setUp(self):
        """회원가입 url 초기 설정"""
        self.signup_url = reverse("user-signup")
        self.client = APIClient()

    def tearDown(self):
        """회원가입 초기 설정 데이터 초기화"""
        self.signup_url = None
        self.User.objects.all().delete()
        self.client = None

    def test_signup_success(self):
        """회원 가입 성공"""

        data = {"phone_number": "01055745810", "password": "test123!"}

        response = self.client.post(self.signup_url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_signup_fail_not_email_form(self):
        """회원 가입 실패 : 번호 형식이 아님."""

        data = {"email": "test2", "password": "test!123"}

        response = self.client.post(self.signup_url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_fail_password_length_short_not_include_special(self):
        """회원 가입 실패 : 비밀번호 길이가 8자 미만, 특수 문자 포함 x"""

        data = {"phone_number": "01055745810", "password": "test12"}

        response = self.client.post(self.signup_url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_fail_password_not_include_special(self):
        """회원 가입 실패 : 비밀번호가 길이, 숫자는 만족하나, 특수문자 포함 x"""

        data = {
            "phone_number": "01055745810",
            "password": "test123121",
        }

        response = self.client.post(self.signup_url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_fail_password_legth_short(self):
        """회원 가입 실패 : 비밀번호가 특수 문자, 숫자 포함하지만, 길이 만족 x"""

        data = {
            "phone_number": "01055745810",
            "password": "test!12",
        }

        response = self.client.post(self.signup_url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_fail_password_not_num(self):
        """회원 가입 실패 : 비밀번호가 특수 문자 포함, 길이 만족하지만 숫자 x"""

        data = {
            "phone_number": "01055745810",
            "password": "test!@#$",
        }

        response = self.client.post(self.signup_url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LogInAPITest(APITestCase):
    """
    유저 로그인 테스트
    """

    User = get_user_model()

    # setUpTestData는 한번만 실행되기 때문에 로그인 테스트를 할 때에는 각 함수들이 실행될 때마다 실행되는 setUp을 씀.
    def setUp(self):
        """기본적인 유저 설정 및 로그인 url 설정"""
        self.phone_number = "01055745810"
        self.password = "test123!"
        self.user = self.User.objects.create(
            phone_number=self.phone_number, password=make_password(self.password)
        )
        self.login_url = reverse("user-login")
        self.client = APIClient()

    def tearDown(self):
        """로그인 초기 설정 데이터 초기화"""
        self.client = None
        self.phone_number = None
        self.password = None
        self.user = None
        self.login_url = None
        self.User.objects.all().delete()
        OutstandingToken.objects.all().delete()

    def test_login_success(self):
        """로그인 성공"""

        login_data = {
            "phone_number": self.phone_number,
            "password": self.password,
        }

        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("access_token" in response.content.decode("utf-8"))
        self.assertTrue("refresh_token" in response.content.decode("utf-8"))

    def test_login_fail_wrong_password(self):
        """로그인 실패 : 잘못된 비밀번호"""

        data = {
            "phone_number": self.phone_number,
            "password": self.password + ".",
        }

        response = self.client.post(self.login_url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_fail_wrong_phone_number(self):
        """로그인 실패 : 잘못된 휴대폰 번호"""

        data = {
            "phone_number": self.phone_number + ".",
            "password": self.password,
        }

        response = self.client.post(self.login_url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_fail_wrong_phone_number_password(self):
        """로그인 실패 : 잘못된 이메일 + 잘못된 비밀번호"""

        data = {
            "phone_number": self.phone_number + ".",
            "password": self.password + ".",
        }

        response = self.client.post(self.login_url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LogOutAPITest(APITestCase):
    User = get_user_model()
    """
    유저 로그아웃 테스트
    """

    def setUp(self):
        """기본적인 유저 설정 및 로그아웃 url, 유저 토큰 인증 설정"""
        self.phone_number = "01055745810"
        self.password = "test123!"
        self.user = self.User.objects.create(
            phone_number=self.phone_number, password=make_password(self.password)
        )
        self.logout_url = reverse("user-logout")
        self.token = TokenObtainPairSerializer.get_token(self.user)
        self.refresh_token = str(self.token)
        self.access_token = str(self.token.access_token)
        self.client = APIClient()

    def tearDown(self):
        """로그아웃 초기 설정 데이터 초기화"""
        self.client = None
        self.phone_number = None
        self.password = None
        self.user = None
        self.logout_url = None
        self.token = None
        self.refresh_token = None
        self.access_token = None
        self.User.objects.all().delete()
        OutstandingToken.objects.all().delete()
        BlacklistedToken.objects.all().delete()

    def test_logout_success(self):
        """로그아웃 성공"""

        data = {"refresh_token": self.refresh_token, "phone_number": self.phone_number}

        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)
        response = self.client.post(self.logout_url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_fail_wrong_refresh_token(self):
        """로그아웃 실패 : 엑세스 토큰은 맞는데, 리프레시 토큰 x"""

        data = {
            "refresh_token": self.refresh_token + "d",
            "phone_number": self.phone_number,
        }
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)
        response = self.client.post(self.logout_url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_fail_wrong_access_token(self):
        """로그아웃 실패 : 리프레시 토큰은 맞는데, 엑세스 토큰 x"""

        data = {"refresh_token": self.refresh_token}
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token + "d")
        response = self.client.post(self.logout_url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
