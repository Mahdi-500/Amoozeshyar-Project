from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from django_resized import ResizedImageField
from django_jalali.db import models as jmodels
from phonenumber_field.modelfields import PhoneNumberField
from StudentsApp.models import student
from LessonsApp.models import lesson_class
import logging, os, shutil

# Create your models here.
class professor(models.Model):

    def image_saving_location(instance, filename):
        return f'professor/{instance.last_name}/{filename}'
    
    class gender_choices(models.TextChoices):
        MALE = "مرد", ("مرد")
        FEMALE = "زن", ("زن")
    

    # ? general information
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="professor")
    first_name = models.CharField(max_length=70, blank=False, verbose_name="نام")
    last_name = models.CharField(max_length=100, blank=False, verbose_name="نام خانوادگی")
    date_of_birth = jmodels.jDateField(blank=False, verbose_name="تاریخ تولد")
    gender = models.CharField(max_length=3, blank=True, choices=gender_choices, default=gender_choices.MALE, verbose_name="جنسیت")
    address = models.TextField(blank=False, verbose_name="آدرس")
    marriage = models.BooleanField(default=False, verbose_name="وضعیت تاهل")
    professor_id = models.CharField(max_length=10, blank=False, unique=True, verbose_name="کد ملی")
    photo = ResizedImageField(upload_to=image_saving_location, blank=False, scale=0.75, force_format="PNG", verbose_name="عکس")
    major = models.CharField(max_length=255, blank=False, verbose_name="رشته تحصیلی")
    email = models.EmailField(blank=True, verbose_name="ایمیل")
    phone = PhoneNumberField(blank=False, region="IR", verbose_name="شماره موبایل")
    created = jmodels.jDateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    modified = jmodels.jDateTimeField(auto_now=True, verbose_name="تاریخ تغییر")

    # ? university related information
    code = models.CharField(max_length=10, primary_key=True, default="1111111111", verbose_name="کد استاد")    # ? autofill - primary key
    universities = models.ManyToManyField("academic.university", related_name="professor", blank=False, verbose_name="دانشگاه(های) مشغول به تدریس")
    role = models.CharField(max_length=10, default="professor")

    
    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        indexes = [models.Index(
            fields=["code", "professor_id"]
        )]


class Grade(models.Model):
    student_name = models.ForeignKey(student, verbose_name="دانشجو", on_delete=models.CASCADE, related_name="grade")
    lesson_name = models.ForeignKey(lesson_class, verbose_name="درس", on_delete=models.CASCADE, related_name="grade")
    score = models.DecimalField(max_digits=4, blank=False, decimal_places=2,verbose_name="نمره")
    modified = jmodels.jDateTimeField(auto_now=True, verbose_name="تاریخ تغییر")
    created = jmodels.jDateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")


log = logging.getLogger(__name__)

# todo - professor model functions

@receiver(pre_save, sender=professor)
def set_professor_code(sender, instance, created=False, **kwargs):
    if hasattr(instance, "code") and instance.code == "1111111111":
        part_1 = str(instance.date_of_birth)[:4]
        part_2 = str(instance.created)[1:4]

        last_user = professor.objects.all().order_by("-code")
        if last_user:
            part_3 = str(int(last_user[0].code[6:]) + 1)
        else:
            part_3 = "100"

        instance.code = part_1 + part_2 + part_3

    else:
        log.info(msg="set_professor_code; this is an update")


@receiver(post_delete, sender=professor)
def delete_image(sender, instance, **kwargs):
    if instance.photo:
        image_path = instance.photo.path
        folder_path = os.path.dirname(image_path)

        if os.path.isdir(folder_path):
            shutil.rmtree(folder_path)

        log.info(msg=f"{sender.__name__}; photo deleted")


@receiver(post_delete, sender=professor)
def delete_user(sender, instance, **kwargs):
    if instance.user:
        username = instance.user.username
        password = instance.user.password
        user = User.objects.get(username=username, password=password)
        user.delete()

        log.info(msg=f"{sender.__name__}; user deleted")