# Generated by Django 5.1.4 on 2025-01-12 13:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='myuser',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='avatar/', verbose_name='Аватар'),
        ),
    ]
