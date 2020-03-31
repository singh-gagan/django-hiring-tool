# Generated by Django 2.0.7 on 2020-03-31 09:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('hiringapp', '0017_auto_20200331_1519'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='activity_uuid_link',
            field=models.UUIDField(default=uuid.UUID('e81281ac-ec9c-464c-affc-ecb0cb62e2ce'), primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='submission',
            name='invitation_creation_dateandtime',
            field=models.DateTimeField(blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='submission',
            name='invitation_host',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
