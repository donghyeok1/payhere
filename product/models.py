from django.db import models


def initial_sound(string):
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


class Category(models.Model):
    name = models.CharField(max_length=30, unique=True, db_collation="utf8_general_ci")

    def __str__(self):
        return self.name


class Product(models.Model):
    SIZE_CHOICES = (("s", "small"), ("l", "large"))

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.IntegerField()
    cost = models.IntegerField()
    name = models.CharField(max_length=30, db_index=True)
    name_initial = models.CharField(max_length=30, blank=True, db_index=True)
    description = models.TextField(blank=True)
    barcode = models.CharField(max_length=30, unique=True)
    expiration_date = models.DateField()
    size = models.CharField(choices=SIZE_CHOICES, default="s", max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name_initial = initial_sound(self.name)
        super().save(*args, **kwargs)
