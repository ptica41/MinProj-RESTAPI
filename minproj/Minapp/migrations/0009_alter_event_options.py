# Generated by Django 4.2.3 on 2023-10-05 11:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Minapp', '0008_alter_usergroups_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='event',
            options={'ordering': ['-id'], 'verbose_name_plural': 'Мероприятия'},
        ),
    ]
