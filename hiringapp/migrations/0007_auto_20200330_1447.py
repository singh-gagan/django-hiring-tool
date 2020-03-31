# Generated by Django 2.0.7 on 2020-03-30 09:17

from django.db import migrations, models
import hiringapp.utils
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('hiringapp', '0006_auto_20200326_1757'),
    ]

    operations = [
        migrations.CreateModel(
            name='MailModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mail_status', models.CharField(choices=[(hiringapp.utils.EmailType('invitation'), 'invitation'), (hiringapp.utils.EmailType('reminder'), 'reminder'), (hiringapp.utils.EmailType('feedback'), 'feedback')], max_length=100)),
                ('mail_subject', models.CharField(max_length=100)),
                ('mail_content', models.CharField(max_length=1000)),
            ],
        ),
        migrations.AlterField(
            model_name='submission',
            name='activity_invite_link',
            field=models.UUIDField(default=uuid.UUID('c9008b39-ca3e-48b4-877d-8aa3e494cfcf'), primary_key=True, serialize=False),
        ),
    ]