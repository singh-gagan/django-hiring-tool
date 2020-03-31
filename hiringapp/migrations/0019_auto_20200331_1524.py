# Generated by Django 2.0.7 on 2020-03-31 09:54

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('hiringapp', '0018_auto_20200331_1523'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mailmodel',
            name='mail_subject',
            field=models.CharField(editable=False, max_length=100),
        ),
        migrations.AlterField(
            model_name='submission',
            name='activity_uuid_link',
            field=models.UUIDField(default=uuid.UUID('5f7563a6-0312-4298-83dd-0210acd580c1'), primary_key=True, serialize=False),
        ),
    ]
