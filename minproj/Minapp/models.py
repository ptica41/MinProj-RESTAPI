import uuid

from django.db import models
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

from rest_framework.authtoken.models import Token

from phonenumber_field.modelfields import PhoneNumberField


def get_file_id(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return filename


class UserManager(BaseUserManager):
    def create_user(self, phone, name, surname, password=None, commit=True, **kwargs):
        """
        Creates and saves a User with the given phone, name, surname and password.
        """
        if not phone:
            raise ValueError('Users must have a phone')
        if not name:
            raise ValueError('Users must have a first name')
        if not surname:
            raise ValueError('Users must have a surname')

        user = self.model(phone=phone, name=name, surname=surname, **kwargs)

        user.set_password(password)
        if commit:
            user.save(using=self._db)
        return user

    def create_superuser(self, phone, name, surname, password):
        """
        Creates and saves a superuser with the given phone, name, surname and password.
        """
        user = self.create_user(phone, name, surname, password, commit=False)
        user.is_superuser = True
        user.staff = 'AD'
        user.save(using=self._db)
        return user


class Department(models.Model):
    name = models.CharField(verbose_name='Название', unique=True, max_length=255,
                            help_text='Введите название ведомства',
                            error_messages={'required': 'Обязательное поле',
                                            'unique': 'Ведомство с таким названием уже существует'})

    class Meta:
        db_table = "Departments"
        verbose_name_plural = "Ведомства"
        ordering = ["-id"]

    def __str__(self):
        return self.name


class Group(models.Model):
    name = models.CharField(verbose_name='Название', unique=True, max_length=255,
                            error_messages={'required': 'Обязательное поле',
                                            'unique': 'Группа с таким названием уже существует'})
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "Groups"
        verbose_name_plural = "Группы"
        ordering = ["-id"]

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    CHOICES = [
        ('AD', 'Администратор'),
        ('CO', 'Координатор'),
        ('OP', 'Оператор'),
        ('RE', 'Получатель')
    ]

    objects = UserManager()

    phone = PhoneNumberField(verbose_name='Телефон', unique=True)
    name = models.CharField(verbose_name='Имя', max_length=255)
    surname = models.CharField(verbose_name='Фамилия', max_length=255)
    middle_name = models.CharField(verbose_name='Отчество', max_length=255, blank=True, null=True)
    staff = models.CharField(verbose_name='Должность', max_length=2, choices=CHOICES)
    email = models.EmailField(verbose_name='Эл. почта', blank=True)
    photo = models.CharField(verbose_name='Фотография', blank=True, null=True)
    date_joined = models.DateTimeField('Дата создания', default=timezone.now)
    is_check = models.BooleanField(verbose_name='Проверка', default=False)
    is_active = models.BooleanField(verbose_name='Активный пользователь?', default=True)
    groups = models.ManyToManyField(Group, through="UserGroups")
    department_id = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='Ведомство', blank=True,
                                      null=True, help_text='Только для операторов')

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['name', 'surname']

    class Meta:
        db_table = "Users"
        verbose_name_plural = "Пользователи"
        ordering = ["-id"]

    def __str__(self):
        return f'{self.surname} {self.get_staff_display()}'


class UserGroups(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    class Meta:
        ordering = ["-id"]


class Location(models.Model):
    name = models.CharField(verbose_name="Название", unique=True, max_length=255,
                            error_messages={'required': 'Обязательное поле',
                                            'unique': 'Учреждение с таким названием уже существует'})
    address = models.CharField(verbose_name="Адрес", max_length=255)
    lat = models.DecimalField(verbose_name="Широта", blank=True, null=True, max_digits=8, decimal_places=6)
    lon = models.DecimalField(verbose_name="Долгота", blank=True, null=True, max_digits=9, decimal_places=6)
    phone = PhoneNumberField(verbose_name='Телефон', unique=True)
    email = models.EmailField(verbose_name="Эл. почта", blank=True)
    photo = models.CharField(verbose_name='Фотография', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    department_id = models.ForeignKey(Department, on_delete=models.CASCADE,
                                      error_messages={'required': 'Обязательное поле'})

    class Meta:
        db_table = "Locations"
        verbose_name_plural = "Учреждения"
        ordering = ["-id"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('location', args=[str(self.id)])


class Event(models.Model):
    name = models.CharField(verbose_name="Название", max_length=255)
    description = models.CharField(verbose_name="Описание", max_length=255, blank=True)
    datetime = models.DateTimeField(verbose_name="Дата/время", blank=True, null=True)
    start = models.DateTimeField(verbose_name="Начало ", blank=True, null=True)
    end = models.DateTimeField(verbose_name="Конец", blank=True, null=True)
    is_check = models.BooleanField(verbose_name="Согласовано", default=True)
    is_finished = models.BooleanField(verbose_name="Выполнено", default=False)
    photo = ArrayField(base_field=models.CharField(verbose_name='Фотография'), blank=True, null=True)
    location_id = models.ForeignKey(Location, on_delete=models.CASCADE, verbose_name="Учреждение")
    recipient_id = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Получатель", blank=True, null=True)
    group_id = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name="Группа", blank=True, null=True)

    class Meta:
        db_table = "Events"
        verbose_name_plural = "Мероприятия"
        ordering = ["-id"]

    def __str__(self):
        return self.name


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_signal(sender, instance, created, **kwargs):
    if created:
        Token.objects.create(user=instance)
