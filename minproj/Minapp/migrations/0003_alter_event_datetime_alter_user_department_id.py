# Generated by Django 4.2.3 on 2023-09-05 07:40

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Minapp', '0002_alter_event_datetime_alter_user_middle_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='datetime',
            field=models.DateTimeField(default=datetime.datetime(2023, 9, 5, 10, 40, 24, 943310), verbose_name='Дата/время'),
        ),
        migrations.AlterField(
            model_name='user',
            name='department_id',
            field=models.ForeignKey(blank=True, help_text='Только для операторов', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='department_key', to='Minapp.department', verbose_name='Ведомство'),
        ),
    ]
