# Generated by Django 4.0.4 on 2022-08-24 07:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vote', '0020_alter_podmember_put_farward_recipient_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='pod',
            name='FDel_election',
            field=models.BooleanField(default=False),
        ),
    ]
