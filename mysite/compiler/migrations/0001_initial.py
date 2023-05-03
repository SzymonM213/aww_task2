# Generated by Django 4.0.2 on 2023-05-01 18:43

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Element',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('date_created', models.DateTimeField(default=datetime.date.today)),
                ('accessibility', models.BooleanField(default=True)),
                ('last_accessibility_change', models.DateTimeField(default=None)),
                ('last_content_change', models.DateTimeField(default=None)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='elements', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
