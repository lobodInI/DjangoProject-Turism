# Generated by Django 4.1.1 on 2022-10-03 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('route', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('route_id', models.IntegerField()),
                ('review_text', models.TextField()),
                ('review_rate', models.DateField()),
            ],
        ),
    ]
