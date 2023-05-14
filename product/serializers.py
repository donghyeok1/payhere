from django.utils import timezone
from rest_framework import serializers
from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["category"] = CategorySerializer(instance.category).data
        return response

    def validate(self, data):
        if data.get("price") and data.get("cost"):
            if data["price"] < data["cost"]:
                raise serializers.ValidationError(
                    {"validation_error": "원가가 가격보다 높으면 안됩니다."}
                )
        else:
            if self.instance:
                product = self.instance
                if data.get("price"):
                    if data["price"] < product.cost:
                        raise serializers.ValidationError(
                            {"validation_error": "원가가 가격보다 높으면 안됩니다."}
                        )
                elif data.get("cost"):
                    if product.price < data["cost"]:
                        raise serializers.ValidationError(
                            {"validation_error": "원가가 가격보다 높으면 안됩니다."}
                        )

        return data

    def validate_expiration_date(self, value):
        if value < timezone.now().date():
            raise serializers.ValidationError("유통기한은 상품 등록 날짜보다 이전일 수 없습니다.")
        return value
