# Generated by Django 5.0.6 on 2024-08-17 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pong', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='tour_match_round',
            field=models.IntegerField(default=0),
        ),
    ]
