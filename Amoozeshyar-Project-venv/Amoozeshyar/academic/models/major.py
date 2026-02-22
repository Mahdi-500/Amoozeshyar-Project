from django.db import models
from django_jalali.db import models as jmodels

class major(models.Model):
    name = models.CharField(max_length=255, blank=False, verbose_name="نام رشته")
    code = models.PositiveIntegerField(verbose_name="کد رشته", primary_key=True, blank=False, unique=True)
    capacity = models.PositiveSmallIntegerField(verbose_name="ظرفیت", blank=False)
    created = jmodels.jDateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    modified = jmodels.jDateTimeField(auto_now=True, verbose_name="تاریخ تغییر")

    class Meta:
        indexes = [models.Index(
            fields=["code"]
        )]

    def __str__(self):
        return self.name