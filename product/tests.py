from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from product.models import Product, Category


class ProductCreateAPITest(APITestCase):
    User = get_user_model()
    """
    Product CRUD 중 Create 테스트
    """

    def setUp(self):
        """기본적인 유저 설정 및 상품 등록 url, 유저 토큰 인증 설정"""
        self.phone_number = "01055745810"
        self.password = "test123!"
        self.user = self.User.objects.create(
            phone_number=self.phone_number, password=make_password(self.password)
        )
        self.create_product_url = reverse("products-list")

        self.token = RefreshToken.for_user(self.user)
        self.refresh_token = str(self.token)
        self.access_token = str(self.token.access_token)

        self.client = APIClient()

    def tearDown(self):
        """상품 등록 초기 설정 데이터 초기화"""
        self.client = None
        self.phone_number = None
        self.password = None
        self.user = None

        self.token = None
        self.refresh_token = None
        self.access_token = None

        self.create_product_url = None

        self.User.objects.all().delete()
        OutstandingToken.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()

    def test_create_product_success(self):
        """상품 등록 성공 및 카테고리 생성 성공"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        data = {
            "category": "test_category",
            "price": 10000,
            "cost": 8000,
            "name": "슈크림",
            "description": "test_description",
            "barcode": "test_barcode",
            "expiration_date": "2023-05-30",
            "size": "s",
        }
        response = self.client.post(self.create_product_url, data=data, format="json")
        result = response.data["data"]

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            {"code": 201, "message": "ok"},
            response.json()["meta"],
        )
        self.assertEqual(result["category"]["name"], "test_category")
        self.assertEqual(result["price"], 10000)
        self.assertEqual(result["cost"], 8000)
        self.assertEqual(result["name"], "슈크림")
        self.assertEqual(result["name_initial"], "ㅅㅋㄹ")
        self.assertEqual(result["description"], "test_description")
        self.assertEqual(result["barcode"], "test_barcode")
        self.assertEqual(result["expiration_date"], "2023-05-30")
        self.assertEqual(result["size"], "s")

    def test_create_product_authentication_fail(self):
        """인증 실패로 인한 상품 등록 실패"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token + '.'}")
        data = {
            "category": "test_category",
            "price": 10000,
            "cost": 8000,
            "name": "슈크림",
            "description": "test_description",
            "barcode": "test_barcode",
            "expiration_date": "2023-05-30",
            "size": "s",
        }
        response = self.client.post(self.create_product_url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            {"code": 401, "message": "해당 API를 사용할 권한이 없습니다."},
            response.json()["meta"],
        )
        self.assertEqual(response.data["data"], "null")

    def test_create_product_barcode_fail(self):
        """바코드 번호 중복으로 인한 상품 등록 실패"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        data = {
            "category": "test_category",
            "price": 10000,
            "cost": 8000,
            "name": "슈크림",
            "description": "test_description",
            "barcode": "test_barcode",
            "expiration_date": "2023-05-30",
            "size": "s",
        }
        response = self.client.post(self.create_product_url, data=data, format="json")
        response_duplicate = self.client.post(
            self.create_product_url, data=data, format="json"
        )
        message = response_duplicate.data["meta"]["message"]["barcode"]

        self.assertEqual(response_duplicate.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(
            {"code": 409, "message": {"barcode": ["product의 barcode은/는 이미 존재합니다."]}},
            response_duplicate.json()["meta"],
        )
        self.assertEqual(response_duplicate.data["data"], "null")

    def test_create_product_price_cost_fail(self):
        """상품 원가가 상품 가격보다 높을 때"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        data = {
            "category": "test_category",
            "price": 7000,
            "cost": 8000,
            "name": "슈크림",
            "description": "test_description",
            "barcode": "test_barcode",
            "expiration_date": "2023-05-30",
            "size": "s",
        }
        response = self.client.post(self.create_product_url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {"code": 400, "message": {"validation_error": ["원가가 가격보다 높으면 안됩니다."]}},
            response.json()["meta"],
        )
        self.assertEqual(response.data["data"], "null")

    def test_create_product_expiration_data_fail(self):
        """상품 유통 기한이 상품 등록 날짜보다 이전일때"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        data = {
            "category": "test_category",
            "price": 10000,
            "cost": 8000,
            "name": "슈크림",
            "description": "test_description",
            "barcode": "test_barcode",
            "expiration_date": "2022-05-30",
            "size": "s",
        }
        response = self.client.post(self.create_product_url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {
                "code": 400,
                "message": {"expiration_date": ["유통기한은 상품 등록 날짜보다 이전일 수 없습니다."]},
            },
            response.json()["meta"],
        )
        self.assertEqual(response.data["data"], "null")


class ProductPartialUpdateAPITest(APITestCase):
    User = get_user_model()
    """
    Product CRUD 중 Update(partial) 테스트
    """

    def setUp(self):
        """기본적인 유저 설정 및 상품 등록"""
        self.phone_number = "01055745810"
        self.password = "test123!"
        self.user = self.User.objects.create(
            phone_number=self.phone_number, password=make_password(self.password)
        )
        self.create_product_url = reverse("products-list")

        self.token = RefreshToken.for_user(self.user)
        self.refresh_token = str(self.token)
        self.access_token = str(self.token.access_token)

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        data = {
            "category": "test_category",
            "price": 10000,
            "cost": 8000,
            "name": "슈크림",
            "description": "test_description",
            "barcode": "test_barcode",
            "expiration_date": "2023-05-30",
            "size": "s",
        }
        response = self.client.post(self.create_product_url, data=data, format="json")
        self.update_product_url = (
            self.create_product_url + str(response.data["data"]["id"]) + "/"
        )

    def tearDown(self):
        """상품 수정 초기 설정 데이터 초기화"""
        self.client = None
        self.phone_number = None
        self.password = None
        self.user = None

        self.token = None
        self.refresh_token = None
        self.access_token = None

        self.create_product_url = None
        self.update_product_url = None

        self.User.objects.all().delete()
        OutstandingToken.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()

    def test_update_partial_product_success(self):
        """상품의 각 필드별 부분 업데이트 성공"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        data = {
            "category": "edit_category",
        }
        response = self.client.patch(self.update_product_url, data=data, format="json")
        result = response.data["data"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {"code": 200, "message": "ok"},
            response.json()["meta"],
        )
        self.assertEqual(result["category"]["name"], "edit_category")
        self.assertEqual(result["price"], 10000)
        self.assertEqual(result["cost"], 8000)
        self.assertEqual(result["name"], "슈크림")
        self.assertEqual(result["name_initial"], "ㅅㅋㄹ")
        self.assertEqual(result["description"], "test_description")
        self.assertEqual(result["barcode"], "test_barcode")
        self.assertEqual(result["expiration_date"], "2023-05-30")
        self.assertEqual(result["size"], "s")

        data = {
            "price": 11000,
        }
        response = self.client.patch(self.update_product_url, data=data, format="json")
        result = response.data["data"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {"code": 200, "message": "ok"},
            response.json()["meta"],
        )
        self.assertEqual(result["category"]["name"], "edit_category")
        self.assertEqual(result["price"], 11000)
        self.assertEqual(result["cost"], 8000)
        self.assertEqual(result["name"], "슈크림")
        self.assertEqual(result["name_initial"], "ㅅㅋㄹ")
        self.assertEqual(result["description"], "test_description")
        self.assertEqual(result["barcode"], "test_barcode")
        self.assertEqual(result["expiration_date"], "2023-05-30")
        self.assertEqual(result["size"], "s")

        data = {
            "cost": 6000,
        }
        response = self.client.patch(self.update_product_url, data=data, format="json")
        result = response.data["data"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {"code": 200, "message": "ok"},
            response.json()["meta"],
        )
        self.assertEqual(result["category"]["name"], "edit_category")
        self.assertEqual(result["price"], 11000)
        self.assertEqual(result["cost"], 6000)
        self.assertEqual(result["name"], "슈크림")
        self.assertEqual(result["name_initial"], "ㅅㅋㄹ")
        self.assertEqual(result["description"], "test_description")
        self.assertEqual(result["barcode"], "test_barcode")
        self.assertEqual(result["expiration_date"], "2023-05-30")
        self.assertEqual(result["size"], "s")

        data = {
            "name": "수정 슈크림 라떼",
        }
        response = self.client.patch(self.update_product_url, data=data, format="json")
        result = response.data["data"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {"code": 200, "message": "ok"},
            response.json()["meta"],
        )
        self.assertEqual(result["category"]["name"], "edit_category")
        self.assertEqual(result["price"], 11000)
        self.assertEqual(result["cost"], 6000)
        self.assertEqual(result["name"], "수정 슈크림 라떼")
        self.assertEqual(result["name_initial"], "ㅅㅈㅅㅋㄹㄹㄸ")
        self.assertEqual(result["description"], "test_description")
        self.assertEqual(result["barcode"], "test_barcode")
        self.assertEqual(result["expiration_date"], "2023-05-30")
        self.assertEqual(result["size"], "s")

        data = {
            "description": "edit_description",
        }
        response = self.client.patch(self.update_product_url, data=data, format="json")
        result = response.data["data"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {"code": 200, "message": "ok"},
            response.json()["meta"],
        )
        self.assertEqual(result["category"]["name"], "edit_category")
        self.assertEqual(result["price"], 11000)
        self.assertEqual(result["cost"], 6000)
        self.assertEqual(result["name"], "수정 슈크림 라떼")
        self.assertEqual(result["name_initial"], "ㅅㅈㅅㅋㄹㄹㄸ")
        self.assertEqual(result["description"], "edit_description")
        self.assertEqual(result["barcode"], "test_barcode")
        self.assertEqual(result["expiration_date"], "2023-05-30")
        self.assertEqual(result["size"], "s")

        data = {
            "barcode": "edit_barcode",
        }
        response = self.client.patch(self.update_product_url, data=data, format="json")
        result = response.data["data"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {"code": 200, "message": "ok"},
            response.json()["meta"],
        )
        self.assertEqual(result["category"]["name"], "edit_category")
        self.assertEqual(result["price"], 11000)
        self.assertEqual(result["cost"], 6000)
        self.assertEqual(result["name"], "수정 슈크림 라떼")
        self.assertEqual(result["name_initial"], "ㅅㅈㅅㅋㄹㄹㄸ")
        self.assertEqual(result["description"], "edit_description")
        self.assertEqual(result["barcode"], "edit_barcode")
        self.assertEqual(result["expiration_date"], "2023-05-30")
        self.assertEqual(result["size"], "s")

        data = {
            "expiration_date": "2023-06-18",
        }
        response = self.client.patch(self.update_product_url, data=data, format="json")
        result = response.data["data"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {"code": 200, "message": "ok"},
            response.json()["meta"],
        )
        self.assertEqual(result["category"]["name"], "edit_category")
        self.assertEqual(result["price"], 11000)
        self.assertEqual(result["cost"], 6000)
        self.assertEqual(result["name"], "수정 슈크림 라떼")
        self.assertEqual(result["name_initial"], "ㅅㅈㅅㅋㄹㄹㄸ")
        self.assertEqual(result["description"], "edit_description")
        self.assertEqual(result["barcode"], "edit_barcode")
        self.assertEqual(result["expiration_date"], "2023-06-18")
        self.assertEqual(result["size"], "s")

        data = {
            "size": "l",
        }
        response = self.client.patch(self.update_product_url, data=data, format="json")
        result = response.data["data"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {"code": 200, "message": "ok"},
            response.json()["meta"],
        )
        self.assertEqual(result["category"]["name"], "edit_category")
        self.assertEqual(result["price"], 11000)
        self.assertEqual(result["cost"], 6000)
        self.assertEqual(result["name"], "수정 슈크림 라떼")
        self.assertEqual(result["name_initial"], "ㅅㅈㅅㅋㄹㄹㄸ")
        self.assertEqual(result["description"], "edit_description")
        self.assertEqual(result["barcode"], "edit_barcode")
        self.assertEqual(result["expiration_date"], "2023-06-18")
        self.assertEqual(result["size"], "l")

    def test_update_partial_product_authentication_fail(self):
        """인증되지 않은 사용자 상품 수정 실패"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token + '.'}")
        data = {
            "barcode": "edit barcode",
        }
        response = self.client.patch(self.update_product_url, data=data, format="json")
        result = response.data["data"]

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            {"code": 401, "message": "해당 API를 사용할 권한이 없습니다."},
            response.json()["meta"],
        )
        self.assertEqual(result, "null")

    def test_update_partial_product_price_cost_fail(self):
        """원가가 정가보다 높은 경우 상품 수정 실패"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        data = {
            "price": 7000,
        }
        response = self.client.patch(self.update_product_url, data=data, format="json")
        result = response.data["data"]

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {"code": 400, "message": {"validation_error": ["원가가 가격보다 높으면 안됩니다."]}},
            response.json()["meta"],
        )
        self.assertEqual(result, "null")

        data = {
            "cost": 11000,
        }
        response = self.client.patch(self.update_product_url, data=data, format="json")
        result = response.data["data"]

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {"code": 400, "message": {"validation_error": ["원가가 가격보다 높으면 안됩니다."]}},
            response.json()["meta"],
        )
        self.assertEqual(result, "null")

    def test_update_partial_product_expiration_data_fail(self):
        """수정 날짜보다 유통기한이 이전인 경우 실패"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        data = {
            "expiration_date": "2022-05-20",
        }
        response = self.client.patch(self.update_product_url, data=data, format="json")
        result = response.data["data"]

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {
                "code": 400,
                "message": {"expiration_date": ["유통기한은 상품 등록 날짜보다 이전일 수 없습니다."]},
            },
            response.json()["meta"],
        )
        self.assertEqual(result, "null")

    def test_update_partial_product_barcode_fail(self):
        """이미 존재하는 바코드로 수정하는 경우 수정 실패"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        data = {
            "category": "test_category",
            "price": 10000,
            "cost": 8000,
            "name": "슈크림",
            "description": "test_description",
            "barcode": "test_barcode1",
            "expiration_date": "2023-05-30",
            "size": "s",
        }
        response = self.client.post(self.create_product_url, data=data, format="json")
        data = {
            "barcode": "test_barcode1",
        }
        response = self.client.patch(self.update_product_url, data=data, format="json")
        result = response.data["data"]

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(
            {"code": 409, "message": {"barcode": ["product의 barcode은/는 이미 존재합니다."]}},
            response.json()["meta"],
        )
        self.assertEqual(result, "null")


class ProductDestroyAPITest(APITestCase):
    User = get_user_model()
    """
    Product CRUD 중 Delete 테스트
    """

    def setUp(self):
        """기본적인 유저 설정 및 상품 등록"""
        self.phone_number = "01055745810"
        self.password = "test123!"
        self.user = self.User.objects.create(
            phone_number=self.phone_number, password=make_password(self.password)
        )
        self.create_product_url = reverse("products-list")

        self.token = RefreshToken.for_user(self.user)
        self.refresh_token = str(self.token)
        self.access_token = str(self.token.access_token)

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        data = {
            "category": "test_category",
            "price": 10000,
            "cost": 8000,
            "name": "슈크림",
            "description": "test_description",
            "barcode": "test_barcode",
            "expiration_date": "2023-05-30",
            "size": "s",
        }
        response = self.client.post(self.create_product_url, data=data, format="json")
        self.delete_product_url = (
            self.create_product_url + str(response.data["data"]["id"]) + "/"
        )

    def tearDown(self):
        """상품 삭제 초기 설정 데이터 초기화"""
        self.client = None
        self.phone_number = None
        self.password = None
        self.user = None

        self.token = None
        self.refresh_token = None
        self.access_token = None

        self.create_product_url = None
        self.delete_product_url = None

        self.User.objects.all().delete()
        OutstandingToken.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()

    def test_delete_product_success(self):
        """상품 삭제 성공"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.delete(self.delete_product_url, format="json")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_product_authentication_fail(self):
        """인증 오류로 상품 삭제 실패"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token + '.'}")
        response = self.client.delete(self.delete_product_url, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            {"code": 401, "message": "해당 API를 사용할 권한이 없습니다."},
            response.json()["meta"],
        )
        self.assertEqual(response.data["data"], "null")


class ProductListAPITest(APITestCase):
    User = get_user_model()
    """
    Product CRUD 중 Read 테스트
    """

    def setUp(self):
        """기본적인 유저 설정 및 상품 등록"""
        self.phone_number = "01055745810"
        self.password = "test123!"
        self.user = self.User.objects.create(
            phone_number=self.phone_number, password=make_password(self.password)
        )
        self.read_product_url = reverse("products-list")
        self.search_product_url = self.read_product_url + "?name="

        self.token = RefreshToken.for_user(self.user)
        self.refresh_token = str(self.token)
        self.access_token = str(self.token.access_token)

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        data = {
            "category": "test_category",
            "price": 10000,
            "cost": 8000,
            "name": "슈크림",
            "description": "test_description",
            "barcode": "test_barcode",
            "expiration_date": "2023-05-30",
            "size": "s",
        }

        for i in range(1, 24):
            data["barcode"] = f"barcode{i}"
            self.client.post(self.read_product_url, data=data, format="json")

    def tearDown(self):
        """상품 읽기 초기 설정 데이터 초기화"""
        self.client = None
        self.phone_number = None
        self.password = None
        self.user = None

        self.token = None
        self.refresh_token = None
        self.access_token = None

        self.read_product_url = None
        self.search_product_url = None

        self.User.objects.all().delete()
        OutstandingToken.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()

    def test_list_pagination_product_success(self):
        """상품 읽기(pagination) 성공"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.get(self.read_product_url, format="json")
        result = response.data
        first_to_second_page_url = result["data"]["next"]
        self.assertEqual(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)
        self.assertEqual(
            {"code": 301, "message": "OK"},
            response.json()["meta"],
        )
        self.assertEqual(len(result["data"]["products"]), 10)

        response = self.client.get(first_to_second_page_url, format="json")
        result = response.data
        second_to_third_page_url = result["data"]["next"]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {"code": 200, "message": "OK"},
            response.json()["meta"],
        )
        self.assertEqual(len(result["data"]["products"]), 10)

        response = self.client.get(second_to_third_page_url, format="json")
        result = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {"code": 200, "message": "OK"},
            response.json()["meta"],
        )
        self.assertEqual(len(result["data"]["products"]), 3)

    def test_list_search_product_success(self):
        """상품 초성, like 검색 성공"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.get(self.search_product_url + "ㅅ", format="json")
        result = response.data
        self.assertEqual(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)
        self.assertEqual(
            {"code": 301, "message": "OK"},
            response.json()["meta"],
        )
        self.assertEqual(len(result["data"]["products"]), 10)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.get(self.search_product_url + "ㅅㅋ", format="json")
        result = response.data
        self.assertEqual(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)
        self.assertEqual(
            {"code": 301, "message": "OK"},
            response.json()["meta"],
        )
        self.assertEqual(len(result["data"]["products"]), 10)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.get(self.search_product_url + "ㅅㅋㄹ", format="json")
        result = response.data
        self.assertEqual(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)
        self.assertEqual(
            {"code": 301, "message": "OK"},
            response.json()["meta"],
        )
        self.assertEqual(len(result["data"]["products"]), 10)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.get(self.search_product_url + "ㅅㅋㄹㄹ", format="json")
        result = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {"code": 200, "message": "검색한 결과가 없습니다."},
            response.json()["meta"],
        )
        self.assertEqual(result["data"], "null")

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.get(self.search_product_url + "슈크림", format="json")
        result = response.data
        self.assertEqual(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)
        self.assertEqual(
            {"code": 301, "message": "OK"},
            response.json()["meta"],
        )
        self.assertEqual(len(result["data"]["products"]), 10)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.get(self.search_product_url + "슈", format="json")
        result = response.data
        self.assertEqual(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)
        self.assertEqual(
            {"code": 301, "message": "OK"},
            response.json()["meta"],
        )
        self.assertEqual(len(result["data"]["products"]), 10)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.get(self.search_product_url + "크림", format="json")
        result = response.data
        self.assertEqual(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)
        self.assertEqual(
            {"code": 301, "message": "OK"},
            response.json()["meta"],
        )
        self.assertEqual(len(result["data"]["products"]), 10)

class ProductDetailAPITest(APITestCase):
    User = get_user_model()
    """
    Product CRUD 중 Read(detail) 테스트
    """

    def setUp(self):
        """기본적인 유저 설정 및 상품 등록"""
        self.phone_number = "01055745810"
        self.password = "test123!"
        self.user = self.User.objects.create(
            phone_number=self.phone_number, password=make_password(self.password)
        )
        self.read_product_url = reverse("products-list")

        self.token = RefreshToken.for_user(self.user)
        self.refresh_token = str(self.token)
        self.access_token = str(self.token.access_token)

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        data = {
            "category": "test_category",
            "price": 10000,
            "cost": 8000,
            "name": "슈크림",
            "description": "test_description",
            "barcode": "test_barcode",
            "expiration_date": "2023-05-30",
            "size": "s",
        }

        response = self.client.post(self.read_product_url, data=data, format="json")

        product_id = response.data["data"]["id"]
        self.detail_product_url = self.read_product_url + f"{product_id}/"

    def tearDown(self):
        """상품 상세 조회 초기 설정 데이터 초기화"""
        self.client = None
        self.phone_number = None
        self.password = None
        self.user = None

        self.token = None
        self.refresh_token = None
        self.access_token = None

        self.read_product_url = None
        self.detail_product_url = None

        self.User.objects.all().delete()
        OutstandingToken.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()

    def test_list_detail_product_success(self):
        """상품 상세 조회 성공"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.get(self.detail_product_url, format="json")
        result = response.data["data"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {"code": 200, "message": "ok"},
            response.json()["meta"],
        )
        self.assertEqual(result["category"]["name"], "test_category")
        self.assertEqual(result["price"], 10000)
        self.assertEqual(result["cost"], 8000)
        self.assertEqual(result["name"], "슈크림")
        self.assertEqual(result["name_initial"], "ㅅㅋㄹ")
        self.assertEqual(result["description"], "test_description")
        self.assertEqual(result["barcode"], "test_barcode")
        self.assertEqual(result["expiration_date"], "2023-05-30")
        self.assertEqual(result["size"], "s")

    def test_list_detail_product_fail(self):
        """자신이 작성하지 않았거나, 존재하지 않는 상품 상세 조회 실패"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.get(self.read_product_url + "1000/", format="json")
        result = response.data

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            {"code": 404, "message": "해당 상품이 없습니다."},
            response.json()["meta"],
        )
        self.assertEqual(result["data"], "null")