# Generated by Django 2.0.5 on 2018-06-08 23:08

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('landing', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscribe',
            name='timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='subscribe',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
    ]
