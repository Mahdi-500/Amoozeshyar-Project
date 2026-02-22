
from django.db import models
from django_jalali.db import models as jmodels

class group(models.Model):
    name = models.CharField(max_length=100, blank=False, verbose_name="نام گروه")
    code = models.PositiveSmallIntegerField(blank=False, verbose_name="کد گروه", default=0)
    created = jmodels.jDateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    modified = jmodels.jDateTimeField(auto_now=True, verbose_name="تاریخ تغییر")

    def __str__(self):
        return f'{self.name}({self.code})'