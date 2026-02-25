from django.db import models
from django_jalali.db import models as jmodels
from django.db.models import UniqueConstraint
from django.db.models.signals import pre_save
from django.dispatch import receiver
from academic.models import major, university, group
from StudentsApp.forms import semester
import logging

# Create your models here.
class lesson(models.Model):

    class unit_type_choices(models.TextChoices):
        NAZARI = "نظری", ("نظری")
        NAZARI_AMALI = "نظری-عملی", ("نظری - عملی")
        AMALI = "عملی", ("عملی")
        AZMAYESHGAHI = "آز", ("آزمایشگاهی")
        CARAMOOZI = "کارآموزی", ("کارآموزی")


    class lesson_type_choices(models.TextChoices):
        ASLI = "اصلی", ("اصلی")
        PAYE = "پایه", ("پایه")
        OMOMI = "عمومی", ("عمومی")
        TAKHASOSI = "تخصصی", ("تخصصی")
        EKHTIARI = "اختیاری", ("اختیاری")

    
    name = models.CharField(max_length=255, blank=False, verbose_name="نام درس")
    code = models.CharField(max_length=10, primary_key=True, blank=False, verbose_name="کد درس", default="1111111111")     # ? autocomplete - primary key
    unit = models.PositiveSmallIntegerField(blank= False, default=0, verbose_name="تعداد واحد")
    unit_type = models.CharField(max_length=11, choices=unit_type_choices, default=unit_type_choices.NAZARI, blank=True, verbose_name="نوع واحد")
    lesson_type = models.CharField(max_length=9, choices=lesson_type_choices, default=lesson_type_choices.ASLI, blank=True, verbose_name="نوع درس")
    pishniaz = models.ManyToManyField('self', blank=True, verbose_name="پیش نیاز")
    hamniaz = models.ManyToManyField('self', blank=True, verbose_name="هم نیاز")
    lesson_major = models.ManyToManyField(major, blank=False, verbose_name="رشته")
    created = jmodels.jDateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    modified = jmodels.jDateTimeField(auto_now=True, verbose_name="تاریخ تغییر")

    class Meta:
        indexes = [
            models.Index(
                fields=["code"]
            )
        ]

    
    def __str__(self):
        return self.name + f'({self.code})'



class lesson_class(models.Model):

    class lesson_day_choices(models.TextChoices):
        SATURDAY = "شنبه", "شنبه"
        SUNDAY = "یک شنبه", "یکشنبه"
        MONDAY = "دوشنبه", "دوشنبه"
        TUESDAY = "سه شنبه", "سه شنبه"
        WEDNESDAY = "چهارشنبه", "چهارشنبه"
        THURSDAY = "پنج شنبه", "پنج شنبه"

    class lesson_dgree_choices(models.TextChoices):
        BACHELOR = "کارشناسی", "کارشناسی"
        MASTER = "ارشد", "کارشناسی ارشد"
        PHD = "دکتری", "دکتری"

    class degree_type_choices(models.TextChoices):
        PEYVASTE = "پیوسته", "پیوسته"
        NA_PAYVASTE = "ناپیوسته", "ناپیوسته"

    # ? connected models    
    lesson_code = models.ForeignKey(lesson, on_delete=models.CASCADE, verbose_name="نام درس",related_name="classes", blank=False)
    professor_name = models.ForeignKey("ProfessorsApp.professor", on_delete=models.CASCADE, verbose_name="نام استاد", related_name="classes", blank=False)
    university_location = models.ForeignKey(university, on_delete=models.CASCADE, related_name="classes", verbose_name="مکان برگزاری", blank=False)
    group_name = models.ForeignKey(group, on_delete=models.CASCADE, related_name="classes", blank=False, verbose_name="نام گروه")

    # ? date and time
    class_day = models.CharField(max_length=10, choices=lesson_day_choices, default=lesson_day_choices.SATURDAY, blank=True, verbose_name="روز برگزاری کلاس")
    class_start_time = models.TimeField(max_length=5, blank=False, verbose_name="ساعت شروع کلاس")
    class_end_time = models.TimeField(max_length=5, blank=False, verbose_name="ساعت پایان کلاس")
    exam_date_time = jmodels.jDateTimeField(verbose_name="زمان و تاریخ امتحان")

    # ? class info
    degree = models.CharField(max_length=8, choices=lesson_dgree_choices, default=lesson_dgree_choices.BACHELOR, blank=True, verbose_name="مقطع")
    degree_type = models.CharField(max_length=8, choices=degree_type_choices, default=degree_type_choices.PEYVASTE, blank=True, verbose_name="نوع مقطع")
    capacity = models.PositiveSmallIntegerField(blank=False, verbose_name="ظرفیت")
    class_code = models.PositiveSmallIntegerField(blank=False, verbose_name="کد ارائه")
    class_number = models.PositiveSmallIntegerField(blank=False, verbose_name="شماره کلاس")
    semester = models.PositiveSmallIntegerField(blank=True, verbose_name="نیمسال", default=int(semester()))

    created = jmodels.jDateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    modified = jmodels.jDateTimeField(auto_now=True, verbose_name="تاریخ تغییر")

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["class_code", "semester"],
                name="unique_ClassCode_semester",
            )
        ]

        indexes = [models.Index(fields=[
            "class_code", "semester"
        ])
        ]


    def __str__(self):
        return f'کلاس {self.lesson_code} با استاد {self.professor_name} با کد ارائه {self.class_code}'


log = logging.getLogger(__name__)

# todo - lesson model functions

@receiver(pre_save, sender=lesson)
def set_lesson_code(sender, instance, **kwrage):
    if hasattr(instance, "code") and instance.code == "1111111111":
        part_1 = '491'
        part_2 = '052'
        part_3 = str(instance.unit)

        last_code = lesson.objects.all().order_by("-code")
        if last_code:
            part_4 = str(int(last_code[0].code[7:]) + 1)
        else:
            part_4 = '100'


        instance.code = part_1 + part_2 + part_3 + part_4
    else:
        log.info(msg="set_lesson_code; this is an update")



# todo - lesson_class functions
@receiver(pre_save, sender=lesson_class)
def set_semester(sender, instance, **kwargs):
    if  instance.semester == "1111":
        today_date_month = jmodels.jdatetime.date.today().month
        today_date_year = str(jmodels.jdatetime.date.today().year)
        
        if 11 <= today_date_month <= 12:
            today_date_year[1:] += '2'
            
        elif 1 <= today_date_month <= 3:
            year = str(int(today_date_year) - 1)[1:]
            today_date_year = year + "2"

        elif 6 <= today_date_month <= 10:
            today_date_year[1:] + "1"
        
        elif today_date_month == 4 or today_date_month == 5:
            year = str(int(today_date_year) - 1)
            today_date_year = year + "3"
            
        instance.semester = int(today_date_year[1:])
    else:
        log.info(msg="set_semester; this is an update")