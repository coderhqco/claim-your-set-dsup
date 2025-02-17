# Generated by Django 4.0.4 on 2025-02-17 22:32

import api.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vote', '0047_alter_contactinfo_options_contactinfo_created_at_and_more'),
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SecDelModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.PositiveIntegerField(default=api.models.generate_unique_code, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('invitation_key', models.PositiveBigIntegerField(default=api.models.generate_unique_invitation_key, unique=True)),
                ('district', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vote.districts')),
            ],
        ),
        migrations.DeleteModel(
            name='TestingModel',
        ),
    ]
