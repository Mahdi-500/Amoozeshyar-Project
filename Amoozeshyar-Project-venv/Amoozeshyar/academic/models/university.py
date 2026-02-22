from django.db import models
from django_jalali.db import models as jmodels

class university(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام دانشگاه", blank=False)
    code = models.PositiveIntegerField(verbose_name="کد دانشگاه", unique=True, primary_key=True)
    address = models.TextField(blank=False, verbose_name="آدرس", default="تهران")
    created = jmodels.jDateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    modified = jmodels.jDateTimeField(auto_now=True, verbose_name="تاریخ تغییر")

    class Meta:
        indexes = [models.Index(
            fields=["code"]
        )]

    def __str__(self):
        return self.name