# Generated by Django 4.2.5 on 2025-05-25 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0005_usercard_created_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usercard',
            name='notes',
            field=models.TextField(blank=True, default='', null=True),
        ),
    ]
