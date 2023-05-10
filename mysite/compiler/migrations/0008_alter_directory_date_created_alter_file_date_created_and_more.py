# Generated by Django 4.0.2 on 2023-05-09 21:45

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compiler', '0007_rename_accessibility_directory_access_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='directory',
            name='date_created',
            field=models.DateTimeField(default=datetime.datetime(2023, 5, 9, 21, 45, 54, 11639)),
        ),
        migrations.AlterField(
            model_name='file',
            name='date_created',
            field=models.DateTimeField(default=datetime.datetime(2023, 5, 9, 21, 45, 54, 12316)),
        ),
        migrations.AlterField(
            model_name='section',
            name='date_created',
            field=models.DateTimeField(default=datetime.datetime(2023, 5, 9, 21, 45, 54, 11963)),
        ),
        migrations.AlterField(
            model_name='section',
            name='status',
            field=models.CharField(default='no warnings', max_length=200, null=True),
        ),
    ]
