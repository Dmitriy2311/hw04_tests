from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Group, Post, User
from posts.tests.test_models import TEST_DESCRIPT, TEST_POST, TEST_GROUP, AUTH

POST_CREATE = 'posts:post_create'
INDEX = 'posts:index'
PROFILE = 'posts:profile'
GROUP_LIST = 'posts:group_list'
EDIT = 'posts:post_edit'
SLUG = 'slug'
NO_AUTH = 'Не авторизованый пользователь'


class PostsUrlsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title=TEST_GROUP,
            slug=SLUG,
            description=TEST_DESCRIPT, 
        )
        cls.author = User.objects.create_user(username=AUTH)
        cls.no_author = User.objects.create_user(
            username = NO_AUTH
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text=TEST_POST,
        )
        cls.templates_url_names_public = {
            'posts/index.html': reverse(INDEX),
            'posts/group_list.html': reverse(
                GROUP_LIST,
                kwargs={'slug': cls.group.slug},
            ),
            'posts/profile.html': reverse(
                PROFILE,
                kwargs={'username': cls.author.username},
            ),
        }

        cls.templates_url_names_private = {
            'posts/create_post.html': reverse(POST_CREATE)
        }

        cls.templates_url_names = {
            'posts/index.html': reverse(INDEX),
            'posts/group_list.html': reverse(
                GROUP_LIST,
                kwargs={'slug': cls.group.slug},
            ),
            'posts/profile.html': reverse(
                PROFILE,
                kwargs={'username': cls.author.username},
            ),
            'posts/create_post.html': reverse(POST_CREATE),
        }

    def setUp(self):
        self.guest_client = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

        self.no_author_client = Client()
        self.no_author_client.force_login(self.no_author)

    def test_urls_guest_user_private(self):
        """
        Проверка на доступнотсь ссылок гостевому пользователю и редирект
        недоступных страниц.
        """
        for template, reverse_name in self.templates_url_names_private.items():
            with self.subTest(template=template):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)
        response = self.guest_client.get(
            reverse(
                EDIT,
                kwargs={'post_id': self.post.id},
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_guest_user_public(self):
        """
        Проверка на доступнотсь ссылок гостевому пользователю и редирект
        доступных страниц.
        """
        for template, reverse_name in self.templates_url_names_public.items():
            with self.subTest(template=template):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_authorized_user(self):
        """Проверка ссылок авторизованному пользователю - автору поста."""
        for template, reverse_name in self.templates_url_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_no_authorized_user(self):
        """Проверка ссылок авторизованному пользователю - не автору поста."""
        for template, reverse_name in self.templates_url_names.items():
            with self.subTest(template=template):
                if reverse_name == reverse(
                    EDIT,
                    kwargs={'post_id': self.post.id},
                ):
                    response = self.no_author_client.get(reverse_name)
                    self.assertEqual(response.status_code, HTTPStatus.FOUND)
                else:
                    response = self.no_author_client.get(reverse_name)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_use_correct_template(self):
        """Проверка на то что URL-адрес использует подходящий шаблон."""
        for template, reverse_name in self.templates_url_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
