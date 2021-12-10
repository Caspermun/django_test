from django.db import models

# Create your models here.
class Category(models.Model):
    title = models.CharField(max_length=255, verbose_name='Title')

    def __str__(self):
        return self.title

class Post(models.Model):
    title = models.CharField(max_length=255, verbose_name='Title')
    text = models.TextField(verbose_name='Text')
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(to='Category', on_delete=models.CASCADE, verbose_name='Category')
    author = models.ForeignKey(to='Author', on_delete=models.CASCADE, verbose_name='Author')

    def __str__(self):
        return self.title


class Author(models.Model):
    name = models.CharField(max_length=255, verbose_name='Name')
    surname = models.CharField(max_length=255, verbose_name='Surname')
    posts = models.ForeignKey(to='Post', on_delete=models.CASCADE, related_name='Posts')

    def __str__(self):
        return f'{self.name} {self.surname}'