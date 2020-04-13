# Generated by Django 2.0.7 on 2020-04-13 07:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mailingapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mailsummary',
            name='mail_status',
            field=models.CharField(choices=[('SENT', 'Sent'), ('NOTSENT', 'NotSent')], default='SENT', max_length=7),
        ),
    ]