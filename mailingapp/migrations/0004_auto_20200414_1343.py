# Generated by Django 2.0.7 on 2020-04-14 08:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mailingapp', '0003_auto_20200413_1249'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mailsummary',
            name='mail_status',
            field=models.CharField(choices=[('SENT', 'sent'), ('NOTSENT', 'notsent')], default='NOTSENT', max_length=7),
        ),
    ]
