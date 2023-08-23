# Generated by Django 4.2.3 on 2023-08-01 12:24

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Minapp', '0004_alter_event_datetime'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='datetime',
            field=models.DateTimeField(default=datetime.datetime(2023, 8, 1, 15, 24, 37, 670118), verbose_name='Дата/время'),
        ),
        migrations.AlterField(
            model_name='user',
            name='department_id',
            field=models.ForeignKey(blank=True, help_text='Только для операторов', null=True, on_delete=django.db.models.deletion.CASCADE, to='Minapp.department', verbose_name='Ведомство'),
        ),
    ]
