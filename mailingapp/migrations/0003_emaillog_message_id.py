# Generated by Django 2.0.7 on 2020-04-15 07:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mailingapp', '0002_auto_20200414_2106'),
    ]

    operations = [
        migrations.AddField(
            model_name='emaillog',
            name='message_id',
            field=models.CharField(max_length=200, null=True),
        ),
    ]