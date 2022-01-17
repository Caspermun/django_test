# Generated by Django 4.0.1 on 2022-01-17 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_remove_author_posts'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ad',
            options={'ordering': ['-created_at'], 'verbose_name': 'Advertisement', 'verbose_name_plural': 'Advertisements'},
        ),
        migrations.AddField(
            model_name='customuser',
            name='is_email_verified',
            field=models.BooleanField(default=True),
        ),
    ]
