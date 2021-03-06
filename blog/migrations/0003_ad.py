# Generated by Django 4.0 on 2022-01-08 14:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_customuser_is_premium'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('description', models.TextField()),
                ('image', models.ImageField(upload_to='ads/', verbose_name='Main image')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('moderated', models.BooleanField(default=False)),
                ('is_activ', models.BooleanField(default=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blog.customuser', verbose_name='User')),
            ],
        ),
    ]
