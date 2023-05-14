from rest_framework import status, viewsets, pagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer

result = {"meta": {"code": "", "message": ""}, "data": ""}


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


class ProductPagination(pagination.CursorPagination):
    page_size = 10
    ordering = "-created_at"
    cursor_query_param = "cursor"

    def get_paginated_response(self, data):
        if self.get_previous_link() is None:
            return Response(
                {
                    "meta": {"code": 301, "message": "OK"},
                    "data": {
                        "next": self.get_next_link(),
                        "previous": self.get_previous_link(),
                        "products": data,
                    },
                },
                status=status.HTTP_301_MOVED_PERMANENTLY,
            )

        else:
            return Response(
                {
                    "meta": {"code": 200, "message": "OK"},
                    "data": {
                        "next": self.get_next_link(),
                        "previous": self.get_previous_link(),
                        "products": data,
                    },
                },
                status=status.HTTP_200_OK,
            )


def get_initial_sound_list(string):
    """
    한글 초성 리스트를 반환하는 함수입니다.
    """

    CHOSUNG_LIST = [
        "ㄱ",
        "ㄲ",
        "ㄴ",
        "ㄷ",
        "ㄸ",
        "ㄹ",
        "ㅁ",
        "ㅂ",
        "ㅃ",
        "ㅅ",
        "ㅆ",
        "ㅇ",
        "ㅈ",
        "ㅉ",
        "ㅊ",
        "ㅋ",
        "ㅌ",
        "ㅍ",
        "ㅎ",
    ]

    result = ""

    for s in string:
        if s != " ":
            if "가" <= s <= "힣":
                chosung = CHOSUNG_LIST[(ord(s) - ord("가")) // 588]
                result += chosung
            else:
                result += s
    return result


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().select_related('user', 'category')
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ProductPagination

    def get_serializer_context(self):
        context = super().get_serializer_context()

        if self.action in ["create", "update", "partial_update"]:
            context["category"] = Category.objects.all()
        return context

    def create(self, request, *args, **kwargs):
        request.data["user"] = request.user.pk
        category, is_created = Category.objects.get_or_create(
            name=request.data["category"]
        )
        request.data["category"] = category.pk
        serializer = self.get_serializer(data=request.data)
        global result

        try:
            serializer.is_valid()
            serializer.save()
            result["meta"]["code"] = status.HTTP_201_CREATED
            result["meta"]["message"] = "ok"
            result["data"] = serializer.data

        except:
            if "barcode" in serializer.errors:
                result["meta"]["code"] = status.HTTP_409_CONFLICT
                result["meta"]["message"] = serializer.errors
                result["data"] = "null"
                return Response(result, status=status.HTTP_409_CONFLICT)

            else:
                result["meta"]["code"] = status.HTTP_400_BAD_REQUEST
                result["meta"]["message"] = serializer.errors
                result["data"] = "null"
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

        return Response(result, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        global result
        try:
            instance = self.queryset.get(id=kwargs["pk"])

            if instance.user_id != request.user.pk:
                result["meta"]["code"] = status.HTTP_401_UNAUTHORIZED
                result["meta"]["message"] = "해당 API를 사용할 권한이 없습니다."
                result["data"] = "null"
                return Response(result, status=status.HTTP_401_UNAUTHORIZED)

            request.data["user"] = request.user.pk

            if "category" in request.data:
                category, is_created = Category.objects.get_or_create(
                    name=request.data["category"]
                )
                request.data["category"] = category.pk

            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)

            try:
                serializer.is_valid(raise_exception=True)
                serializer.save()
                result["meta"]["code"] = status.HTTP_200_OK
                result["meta"]["message"] = "ok"
                result["data"] = serializer.data

            except:
                if "barcode" in serializer.errors:
                    result["meta"]["code"] = status.HTTP_409_CONFLICT
                    result["meta"]["message"] = serializer.errors
                    result["data"] = "null"
                    return Response(result, status=status.HTTP_409_CONFLICT)

                else:
                    result["meta"]["code"] = status.HTTP_400_BAD_REQUEST
                    result["meta"]["message"] = serializer.errors
                    result["data"] = "null"
                    return Response(result, status=status.HTTP_400_BAD_REQUEST)

            return Response(result, status=status.HTTP_200_OK)

        except self.queryset.model.DoesNotExist:
            result["meta"]["code"] = status.HTTP_404_NOT_FOUND
            result["meta"]["message"] = "존재하지 않는 게시글입니다."
            result["data"] = "null"
            return Response(result, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, *args, **kwargs):
        global result

        try:
            instance = self.queryset.get(pk=kwargs["pk"])
            if instance.user_id != request.user.pk:
                result["meta"]["code"] = status.HTTP_401_UNAUTHORIZED
                result["meta"]["message"] = "해당 API를 사용할 권한이 없습니다."
                result["data"] = "null"
                return Response(result, status=status.HTTP_401_UNAUTHORIZED)

        except self.queryset.model.DoesNotExist:
            result["meta"]["code"] = status.HTTP_404_NOT_FOUND
            result["meta"]["message"] = "존재하지 않는 게시글입니다."
            result["data"] = "null"
            return Response(result, status=status.HTTP_404_NOT_FOUND)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs):
        name = self.request.query_params.get("name", None)
        global result
        if name and name != "":
            initial_sound_str = get_initial_sound_list(name)
            self.queryset = self.queryset.filter(name_initial__icontains=initial_sound_str, user_id=request.user.pk)

        elif name == "":
            self.queryset = self.queryset.filter(name="", user_id=request.user.pk)

        else:
            self.queryset = self.queryset.filter(user_id=request.user.pk)

        page = self.paginate_queryset(self.queryset)

        if len(self.queryset) > 10:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        elif len(self.queryset) == 0:
            result["meta"]["code"] = status.HTTP_200_OK
            result["meta"]["message"] = "검색한 결과가 없습니다."
            result["data"] = "null"
            return Response(result, status=status.HTTP_200_OK)

        else:
            serializer = self.get_serializer(self.queryset, many=True)
            result["meta"]["code"] = status.HTTP_200_OK
            result["meta"]["message"] = "ok"
            result["data"] = serializer.data
            return Response(result, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        global result
        try:
            instance = self.queryset.get(pk=kwargs["pk"])

            if instance.user_id == request.user.pk:
                serializer = self.get_serializer(instance)

                result["meta"]["code"] = status.HTTP_200_OK
                result["meta"]["message"] = "ok"
                result["data"] = serializer.data
                return Response(result, status=status.HTTP_200_OK)

            else:
                result["meta"]["code"] = status.HTTP_401_UNAUTHORIZED
                result["meta"]["message"] = "해당 API를 사용할 권한이 없습니다."
                result["data"] = "null"
                return Response(result, status=status.HTTP_401_UNAUTHORIZED)

        except self.queryset.model.DoesNotExist:
            result["meta"]["code"] = status.HTTP_404_NOT_FOUND
            result["meta"]["message"] = "해당 상품이 없습니다."
            result["data"] = "null"
            return Response(result, status=status.HTTP_404_NOT_FOUND)
