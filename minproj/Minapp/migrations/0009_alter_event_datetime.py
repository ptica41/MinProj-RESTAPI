# Generated by Django 4.2.3 on 2023-08-21 13:33

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Minapp', '0008_alter_event_datetime'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='datetime',
            field=models.DateTimeField(default=datetime.datetime(2023, 8, 21, 16, 33, 40, 864674), verbose_name='Дата/время'),
        ),
    ]
