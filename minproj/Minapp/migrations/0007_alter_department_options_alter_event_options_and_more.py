# Generated by Django 4.2.3 on 2023-10-03 13:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Minapp', '0006_alter_user_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='department',
            options={'ordering': ['-id'], 'verbose_name_plural': 'Ведомства'},
        ),
        migrations.AlterModelOptions(
            name='event',
            options={'ordering': ['id'], 'verbose_name_plural': 'Мероприятия'},
        ),
        migrations.AlterModelOptions(
            name='group',
            options={'ordering': ['-id'], 'verbose_name_plural': 'Группы'},
        ),
        migrations.AlterModelOptions(
            name='location',
            options={'ordering': ['-id'], 'verbose_name_plural': 'Учреждения'},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ['-id'], 'verbose_name_plural': 'Пользователи'},
        ),
    ]
