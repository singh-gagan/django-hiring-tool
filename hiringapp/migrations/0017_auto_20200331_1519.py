# Generated by Django 2.0.7 on 2020-03-31 09:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('hiringapp', '0016_auto_20200331_1516'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='activity_uuid_link',
            field=models.UUIDField(default=uuid.UUID('a27cf9b8-ea46-4fc8-a076-4aef560ad460'), primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='submission',
            name='invitation_creation_dateandtime',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='submission',
            name='invitation_host',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]