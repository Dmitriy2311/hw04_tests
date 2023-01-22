from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

MAX_LENGTH = 200


class Group(models.Model):
    title = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name='Название группы'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Ссылка на группу'
    )
    description = models.TextField(verbose_name='Описание группы')

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name='Текст статьи')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор статьи'
    )

    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Группа статей'
    )

    class Meta:
        ordering = ['-pub_date']
        default_related_name = 'posts'

    def __str__(self):
        return self.text[:15]
