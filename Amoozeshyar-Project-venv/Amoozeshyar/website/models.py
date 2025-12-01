from django.db import models
from django.db.models import UniqueConstraint
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django_resized import ResizedImageField
from django_jalali.db import models as jmodels
from phonenumber_field.modelfields import PhoneNumberField
import os, shutil
import logging

# Create your models here.
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



class group(models.Model):
    name = models.CharField(max_length=100, blank=False, verbose_name="نام گروه")
    code = models.PositiveSmallIntegerField(blank=False, verbose_name="کد گروه", default=0)
    created = jmodels.jDateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    modified = jmodels.jDateTimeField(auto_now=True, verbose_name="تاریخ تغییر")

    def __str__(self):
        return f'{self.name}({self.code})'


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
    universities = models.ManyToManyField(university, related_name="professor", blank=False, verbose_name="دانشگاه(های) مشغول به تدریس")
    role = models.CharField(max_length=10, default="professor")

    class Meta:
        indexes = [models.Index(
            fields=["code", "professor_id"]
        )]

    def __str__(self):
        return f'{self.first_name} {self.last_name}'



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
    professor_name = models.ForeignKey(professor, on_delete=models.CASCADE, verbose_name="نام استاد", related_name="classes", blank=False)
    university_location = models.ForeignKey(university, on_delete=models.CASCADE, related_name="classes", verbose_name="مکان برگزاری", blank=False)
    group_name = models.ForeignKey(group, on_delete=models.CASCADE, related_name="classes", blank=False, verbose_name="نام گروه")

    # ? date and time
    class_day = models.CharField(max_length=10, choices=lesson_day_choices, default=lesson_day_choices.SATURDAY, blank=True, verbose_name="روز برگزاری کلاس")
    class_start_time = models.TimeField(max_length=5, blank=False, verbose_name="ساعت شروع کلاس")
    class_end_time = models.TimeField(max_length=5, blank=False, verbose_name="ساعت پایان کلاس")

    # ? class info
    degree = models.CharField(max_length=8, choices=lesson_dgree_choices, default=lesson_dgree_choices.BACHELOR, blank=True, verbose_name="مقطع")
    degree_type = models.CharField(max_length=8, choices=degree_type_choices, default=degree_type_choices.PEYVASTE, blank=True, verbose_name="نوع مقطع")
    capacity = models.PositiveSmallIntegerField(blank=False, verbose_name="ظرفیت")
    class_code = models.PositiveSmallIntegerField(blank=False, verbose_name="کد ارائه")
    class_number = models.PositiveSmallIntegerField(blank=False, verbose_name="شماره کلاس")
    semester = models.PositiveSmallIntegerField(blank=True, verbose_name="نیمسال", default="1111")

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
    


class Grade(models.Model):
    student_name = models.ForeignKey(student, verbose_name="دانشجو", on_delete=models.CASCADE, related_name="grade")
    lesson_name = models.ForeignKey(lesson_class, verbose_name="درس", on_delete=models.CASCADE, related_name="grade")
    score = models.DecimalField(max_digits=4, blank=False, decimal_places=2,verbose_name="نمره")
    modified = jmodels.jDateTimeField(auto_now=True, verbose_name="تاریخ تغییر")
    created = jmodels.jDateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")


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
    


# @receiver(pre_save, sender=professor)
# def set_created(sender, instance, created=False, **kwargs):
#     if created:
#         if not instance.created:
#             instance.created = jmodels.jdatetime.datetime.now()



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



def delete_image(sender, instance, **kwargs):
    if instance.photo:
        image_path = instance.photo.path
        folder_path = os.path.dirname(image_path)

        if os.path.isdir(folder_path):
            shutil.rmtree(folder_path)

        log.info(msg=f"{sender.__name__}; photo deleted")


def delete_user(sender, instance, **kwargs):
    if instance.user:
        username = instance.user.username
        password = instance.user.password
        user = User.objects.get(username=username, password=password)
        user.delete()

        log.info(msg=f"{sender.__name__}; user deleted")

models_to_handle = [professor, student]

# ? Register the signal for each model
for model in models_to_handle:
    @receiver(post_delete, sender=model)
    def handle_post_delete(sender, instance, **kwargs):
        delete_image(sender, instance, **kwargs)

    @receiver(post_delete, sender=model)
    def handle_user_delete(sender, instance, **kwargs):
        delete_user(sender, instance, **kwargs)
