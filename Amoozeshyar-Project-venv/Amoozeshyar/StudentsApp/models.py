from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django_resized import ResizedImageField
from django_jalali.db import models as jmodels
from phonenumber_field.modelfields import PhoneNumberField
from academic.models import major, university
from LessonsApp.models import lesson_class
import logging, os, shutil

# Create your models here.
class student(models.Model):

    def image_saving_location(instance, filename):
        return f'student/{instance.student_id}/{filename}'
    
    
    class gender_choices(models.TextChoices):
        MALE = "مرد", ("مرد")
        FEMALE = "زن", ("زن")

    class status_choices(models.TextChoices):
        FINISHED = "فارغ", ("فارغ التحصیل")
        STUDYING = "مشغول", ("مشغول به تحصیل")
        OFF = "مرخصی", ("مرخصی")


    # ? student's general information
    user = models.OneToOneField(User,on_delete=models.CASCADE, related_name="student")
    first_name = models.CharField(max_length=100, blank=False, verbose_name="نام")
    last_name = models.CharField(max_length=150, blank=False, verbose_name="نام خانوادگی")
    date_of_birth = jmodels.jDateField(blank=False, verbose_name="تاریخ تولد")
    student_id = models.CharField(max_length=10, blank=False, unique=True, verbose_name="کد ملی")
    photo = ResizedImageField(blank=False, upload_to=image_saving_location, scale=0.75, force_format="PNG", verbose_name="عکس")
    marriage = models.BooleanField(default=False, verbose_name="وضعیت تاهل")
    mobile = PhoneNumberField(blank=False, region="IR", verbose_name="موبایل")
    address = models.TextField(blank=False, verbose_name="آدرس")
    gender = models.CharField(max_length=3, blank=True, choices=gender_choices, default=gender_choices.MALE, verbose_name="جنسیت")
    modified = jmodels.jDateTimeField(auto_now=True, verbose_name="تاریخ تغییر")
    created = jmodels.jDateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

    # ? student's educational information
    student_number = models.CharField(max_length=12, primary_key=True, default="111111111111", verbose_name="شماره دانشجویی")     # ? autofill - primary key
    entrance_year = jmodels.jDateField(auto_now_add=True, verbose_name="سال ورودی")
    last_year = models.PositiveSmallIntegerField(verbose_name="آخرین سال تحصیل", null=True, blank=True)     # ? autofill - entrance year + 5
    major = models.ForeignKey(major,on_delete=models.DO_NOTHING, related_name="student", default=None, verbose_name="رشته", blank=False)  
    # credit =  # ! auto calculate
    # average_score =   # ! auto calculate
    role = models.CharField(max_length=10, default="student")
    university = models.ForeignKey(university,on_delete=models.DO_NOTHING, related_name="student", default=None, verbose_name="دانشگاه", blank=False)
    status = models.CharField(max_length=5, blank=True, choices=status_choices, default=status_choices.STUDYING, verbose_name="وضعیت تحصیل")


    class Meta:
        indexes = [models.Index(
            fields=["student_number", "student_id"]
        )]

    
    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class student_choosing_lesson(models.Model):
    student_name = models.ForeignKey(student, on_delete=models.CASCADE, verbose_name="دانشجو", related_name="lessons")
    chosen_class = models.ForeignKey(lesson_class,on_delete=models.CASCADE, verbose_name="درس", related_name="students")
    semester = models.SmallIntegerField(blank=False, default=0, verbose_name="نیمسال")
    created = jmodels.jDateTimeField(auto_now_add=True, verbose_name="تاریخ انتخاب")
    modified = jmodels.jDateTimeField(auto_now=True, verbose_name="تاریخ تغییر")


log = logging.getLogger(__name__)

# todo - student model functions

@receiver(post_save, sender=student)
def set_last_year(sender, instance, created, **kwargs):
    if created:
        if not instance.last_year and hasattr(instance, 'entrance_year'):
            temp = int(str(instance.entrance_year)[:4])
            instance.last_year = temp + 5
    else:
        log.info(msg="set_last_year; this is an update")



@receiver(pre_save, sender=student)
def set_student_number(sender, instance, **kwargs):
    if instance.student_number == "111111111111":
        if hasattr(instance, 'student_number'):
            part_1 = str(instance.entrance_year)[1:4]
            part_2 = str(instance.university.code)
            part_3 = str(instance.major.code)
            
            last_user = student.objects.all().order_by("-student_number")
            if last_user:
                part_4 = str(int(last_user[0].student_number[9:12]) + 1)
            else:
                part_4 = '100'

            instance.student_number = part_1 + part_2 + part_3 + part_4
    else:
        log.info(msg="set_student_number; this is an update")



@receiver(pre_save, sender=student)
def set_entrance_year(sender, instance, **kwargs):
    if not instance.entrance_year:
        if hasattr(instance, "entrance_year") and not instance.entrance_year:
            instance.entrance_year = jmodels.jdatetime.date.today()
    else:
        log.info(msg="set_entrance_year; this is an update")


@receiver(post_delete, sender=student)
def delete_image(sender, instance, **kwargs):
    if instance.photo:
        image_path = instance.photo.path
        folder_path = os.path.dirname(image_path)

        if os.path.isdir(folder_path):
            shutil.rmtree(folder_path)

        log.info(msg=f"{sender.__name__}; photo deleted")


@receiver(post_delete, sender=student)
def delete_user(sender, instance, **kwargs):
    if instance.user:
        username = instance.user.username
        password = instance.user.password
        user = User.objects.get(username=username, password=password)
        user.delete()

        log.info(msg=f"{sender.__name__}; user deleted")