# Generated by Django 4.1.1 on 2022-10-03 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('route', '0002_review'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='review_rate',
            field=models.IntegerField(),
        ),
    ]