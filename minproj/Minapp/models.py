from django.db import models
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.utils import timezone
# from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

import jwt
from phonenumber_field.modelfields import PhoneNumberField

from datetime import datetime, timedelta


class UserManager(BaseUserManager):
    def create_user(self, username, name, surname, password=None, commit=True, **kwargs):
        """
        Creates and saves a User with the given email, first name, last name
        and password.
        """
        if not username:
            raise ValueError('Users must have an login')
        if not name:
            raise ValueError('Users must have a first name')
        if not surname:
            raise ValueError('Users must have a surname')

        user = self.model(username=username, name=name, surname=surname, **kwargs)

        user.set_password(password)
        if commit:
            user.save(using=self._db)
        return user

    def create_superuser(self, username, name, surname, password):
        """
        Creates and saves a superuser with the given username, name,
        surname and password.
        """
        user = self.create_user(username, name, surname, password, commit=False)
        user.is_staff = True
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

    username = models.CharField(verbose_name='Логин', max_length=50, unique=True, db_index=True)
    name = models.CharField(verbose_name='Имя', max_length=255)
    surname = models.CharField(verbose_name='Фамилия', max_length=255)
    middle_name = models.CharField(verbose_name='Отчество', max_length=255, blank=True)
    staff = models.CharField(verbose_name='Должность', max_length=2, choices=CHOICES)
    phone = PhoneNumberField(verbose_name='Телефон', unique=True)
    email = models.EmailField(verbose_name='Эл. почта', blank=True)
    photo = models.ImageField(verbose_name='Фотография', blank=True, upload_to='users/')
    date_joined = models.DateTimeField('Дата создания', default=timezone.now)
    is_staff = models.BooleanField(
        'staff status',
        default=False,
        help_text='Designates whether the user can log into this admin site.')
    department_id = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='Ведомство', blank=True, null=True, help_text='Только для операторов')

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['name', 'surname']

    class Meta:
        db_table = "Users"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f'{self.surname} {self.get_staff_display()}'

    # def get_absolute_url(self):
    #     return reverse('recipient_detail', args=[str(self.id)])

    @property
    def token(self):
        """
        Позволяет получить токен пользователя путем вызова user.token, вместо
        user._generate_jwt_token(). Декоратор @property выше делает это
        возможным. token называется "динамическим свойством".
        """
        return self._generate_jwt_token()

    def _generate_jwt_token(self):
        """
        Генерирует веб-токен JSON, в котором хранится идентификатор этого
        пользователя, срок действия токена составляет 1 день от создания
        """
        dt = datetime.now() + timedelta(days=30)

        token = jwt.encode({
            'id': self.pk,
            'exp': dt.utcfromtimestamp(dt.timestamp())
        }, settings.SECRET_KEY, algorithm='HS256')

        return token

class Operator(models.Model):
    user_id = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    department_id = models.ForeignKey(Department, on_delete=models.CASCADE, blank=True, null=True)
    is_check = models.BooleanField(verbose_name='Проверка', default=False)
    is_active = models.BooleanField(verbose_name='Активный пользователь?', default=True)

    class Meta:
        db_table = "Operators"
        verbose_name_plural = "Операторы"

    def __str__(self):
        return f'{self.user_id.surname} {self.user_id.name} | {self.department_id}'


class Coordinator(models.Model):
    user_id = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_check = models.BooleanField(verbose_name='Проверка', default=False)
    is_active = models.BooleanField(verbose_name='Активный пользователь?', default=True)

    class Meta:
        db_table = "Coordinators"
        verbose_name_plural = "Координаторы"

    def __str__(self):
        return f'{self.user_id.surname} {self.user_id.name}'


class Recipient(models.Model):
    user_id = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_check = models.BooleanField(verbose_name='Проверка', default=False)
    is_active = models.BooleanField(verbose_name='Активный пользователь?', default=True)

    class Meta:
        db_table = "Recipients"
        verbose_name_plural = "Получатели"

    def __str__(self):
        return f'{self.user_id.surname} {self.user_id.name}'


class Location(models.Model):
    name = models.CharField(verbose_name="Название", unique=True, max_length=255,
                            # help_text='Введите название учреждения',
                            error_messages={'required': 'Обязательное поле',
                                            'unique': 'Ведомство с таким названием уже существует'})
    address = models.CharField(verbose_name="Адрес", max_length=255)
    lat = models.DecimalField(verbose_name="Широта", blank=True, null=True, max_digits=8, decimal_places=6)
    lon = models.DecimalField(verbose_name="Долгота", blank=True, null=True, max_digits=9, decimal_places=6)
    phone = PhoneNumberField(verbose_name='Телефон', unique=True)
    email = models.EmailField(verbose_name="Эл. почта", blank=True)
    photo = models.ImageField(verbose_name="Фотография", blank=True, upload_to='locations/')
    is_active = models.BooleanField(default=True)
    department_id = models.ForeignKey(Department, on_delete=models.CASCADE,
                                      error_messages={'required': 'Обязательное поле'})

    class Meta:
        db_table = "Locations"
        verbose_name_plural = "Учреждения"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('location', args=[str(self.id)])


class Event(models.Model):
    name = models.CharField(verbose_name="Название", max_length=255)
    description = models.CharField(verbose_name="Описание", max_length=255, blank=True)
    datetime = models.DateTimeField(verbose_name="Дата/время", default=datetime.now())
    is_check = models.BooleanField(verbose_name="Согласовано", default=False)
    is_finished = models.BooleanField(verbose_name="Выполнено", default=False)
    photo = models.ImageField(verbose_name="Фотография", blank=True, upload_to='events/')
    location_id = models.ForeignKey(Location, on_delete=models.CASCADE, verbose_name="Учреждение")
    recipient_id = models.ForeignKey(Recipient, on_delete=models.CASCADE, verbose_name="Получатель")

    @property
    def is_future(self):
        return (self.datetime.timestamp() > datetime.now().timestamp())

    class Meta:
        db_table = "Events"
        verbose_name_plural = "Мероприятия"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('event', args=[str(self.id)])


@receiver(post_save, sender=User)
def create_user_signal(sender, instance, created, **kwargs):
    if created and instance.staff == 'RE':
        Recipient.objects.create(id=instance.id, user_id=instance)
        instance.recipient.save()
    if created and instance.staff == 'CO':
        Coordinator.objects.create(id=instance.id, user_id=instance)
        instance.coordinator.save()
    if created and instance.staff == 'OP':
        new = Operator.objects.create(id=instance.id, user_id=instance)
        new.department_id_id = instance.department_id
        instance.operator.save()
