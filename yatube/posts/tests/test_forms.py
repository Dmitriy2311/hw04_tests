from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User
from posts.tests.test_urls import POST_CREATE, EDIT, SLUG

NEW_USER = 'Новый пользователь'
TEST_NAME_GROUP = 'Тестовое название группы'
TEST_DESCRIP_GROUP = 'Тестовое описание группы'
TEXT_POST = 'Тестовый пост'
TEXT_POST_FORM = 'Тестовый пост формы'
NEW_TEXT_POST = 'Новый текст поста'
DETAIL = 'posts:post_detail'


class PostsFormsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username=NEW_USER)
        cls.group = Group.objects.create(
            title=TEST_NAME_GROUP,
            slug=SLUG,
            description=TEST_DESCRIP_GROUP,
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text=TEXT_POST,
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_posts_forms_create_post(self):
        """Проверка, создает ли форма пост в базе."""
        post_count = Post.objects.count()
        form_data = {
            'text': TEXT_POST_FORM,
            'group': self.group.id,
        }
        self.authorized_client.post(
            reverse(POST_CREATE),
            data=form_data,
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(Post.objects.filter(
            text=TEXT_POST_FORM,
            group=self.group.id,
        ).exists())

    def test_posts_forms_edit_post(self):
        """Проверка, редактируется ли пост."""
        form_data = {
            'text': NEW_TEXT_POST,
            'group': self.group.id,
        }
        self.authorized_client.post(reverse(
            EDIT,
            kwargs={'post_id': self.post.id},
        ), data=form_data)
        response = self.authorized_client.get(reverse(
            DETAIL,
            kwargs={'post_id': self.post.id},
        ))
        self.assertEqual(response.context['post'].text, NEW_TEXT_POST)
        self.assertTrue(Post.objects.filter(
            text=NEW_TEXT_POST,
            group=self.group.id,
        ).exists())
