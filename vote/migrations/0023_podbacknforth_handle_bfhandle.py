# Generated by Django 4.0.4 on 2023-10-23 02:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('vote', '0022_podbacknforth'),
    ]

    operations = [
        migrations.AddField(
            model_name='podbacknforth',
            name='handle',
            field=models.CharField(default='ducal', max_length=20),
        ),
        migrations.CreateModel(
            name='BFhandle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hndl', models.CharField(default='ducal', max_length=20)),
                ('pod', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vote.pod', to_field='code')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='username')),
            ],
        ),
    ]
