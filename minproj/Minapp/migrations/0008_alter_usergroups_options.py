# Generated by Django 4.2.3 on 2023-10-04 09:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Minapp', '0007_alter_department_options_alter_event_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='usergroups',
            options={'ordering': ['-id']},
        ),
    ]
