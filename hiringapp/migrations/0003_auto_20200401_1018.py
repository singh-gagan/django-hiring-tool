# Generated by Django 2.0.7 on 2020-04-01 04:48

from django.db import migrations, models
import hiringapp.utils
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('hiringapp', '0002_auto_20200331_1828'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='activity_time',
            field=models.DurationField(null=True),
        ),
        migrations.AlterField(
            model_name='submission',
            name='activity_status',
            field=models.CharField(choices=[('started', 'Started'), ('submitted', 'Submitted'), ('not_yet_started', 'Not_Yet_Started'), ('expired', 'Expired')], default=hiringapp.utils.ActivityStatus('not_yet_started'), max_length=500),
        ),
        migrations.AlterField(
            model_name='submission',
            name='activity_uuid',
            field=models.UUIDField(default=uuid.UUID('56f8bc52-bc0a-4150-9130-51723e82be85'), primary_key=True, serialize=False),
        ),
    ]