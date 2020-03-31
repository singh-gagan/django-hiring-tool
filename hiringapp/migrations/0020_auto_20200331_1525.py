# Generated by Django 2.0.7 on 2020-03-31 09:55

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('hiringapp', '0019_auto_20200331_1524'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mailmodel',
            name='mail_subject',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='submission',
            name='activity_uuid_link',
            field=models.UUIDField(default=uuid.UUID('568f9e6e-74ea-46cf-a438-5b5bd2c34a99'), primary_key=True, serialize=False),
        ),
    ]
