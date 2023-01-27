from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User
from posts.tests.test_urls import INDEX, POST_CREATE, GROUP_LIST, PROFILE, EDIT

TEST_OF_POST: int = 13
AUTH = 'Тестовый пользователь'
TEST_NAME = 'Тестовое название'
TEST_SLAG = 'test-slug'
TEST_DISCRIP = 'Тестовое описание'
DETAIL = 'posts:post_detail'


class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=AUTH)
        cls.group = Group.objects.create(
            title=TEST_NAME,
            slug=TEST_SLAG,
            description=TEST_DISCRIP,
        )

        cls.post = Post.objects.create(
            text='Привет!',
            author=cls.user,
            group=cls.group,
        )
        cls.templates_pages_names = {
            'posts/index.html': reverse(INDEX),
            'posts/create_post.html': reverse(POST_CREATE),
            'posts/group_list.html': reverse(
                GROUP_LIST,
                kwargs={'slug': 'test-slug'},
            )
        }

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def posts_check_all_fields(self, post):
        """Метод, проверяющий поля поста."""
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group.id, self.post.group.id)

    def test_posts_pages_use_correct_template(self):
        """Проверка, использует ли адрес URL соответствующий шаблон."""
        for template, reverse_name in self.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_posts_context_index_template(self):
        """
        Проверка, сформирован ли шаблон group_list с
        правильным контекстом.
        Появляется ли пост, при создании на главной странице.
        """
        response = self.authorized_client.get(reverse(INDEX))
        self.posts_check_all_fields(response.context['page_obj'][0])
        last_post = response.context['page_obj'][0]
        self.assertEqual(last_post, self.post)

    def test_posts_context_group_list_template(self):
        """
        Проверка, сформирован ли шаблон group_list с
        правильным контекстом.
        Появляется ли пост, при создании на странице его группы.
        """
        response = self.authorized_client.get(
            reverse(
                GROUP_LIST,
                kwargs={'slug': self.group.slug},
            )
        )
        test_group = response.context['group']
        self.posts_check_all_fields(response.context['page_obj'][0])
        test_post = str(response.context['page_obj'][0])
        self.assertEqual(test_group, self.group)
        self.assertEqual(test_post, str(self.post))

    def test_posts_context_create_post_template(self):
        """
        Проверка, сформирован ли шаблон create_post с
        правильным контекстом.
        """
        response = self.authorized_client.get(reverse(POST_CREATE))

        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_posts_context_post_edit_template(self):
        """
        Проверка, сформирован ли шаблон post_edit с
        правильным контекстом.
        """
        response = self.authorized_client.get(
            reverse(
                EDIT,
                kwargs={'post_id': self.post.id},
            )
        )

        form_fields = {'text': forms.fields.CharField}

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_posts_context_profile_template(self):
        """
        Проверка, сформирован ли шаблон profile с
        правильным контекстом.
        """
        response = self.authorized_client.get(
            reverse(
                PROFILE,
                kwargs={'username': self.user.username},
            )
        )
        profile = {'author': self.post.author}

        for value, expected in profile.items():
            with self.subTest(value=value):
                context = response.context[value]
                self.assertEqual(context, expected)

        self.posts_check_all_fields(response.context['page_obj'][0])
        test_page = response.context['page_obj'][0]
        self.assertEqual(test_page, self.user.posts.all()[0])

    def test_posts_context_post_detail_template(self):
        """
        Проверка, сформирован ли шаблон post_detail с
        правильным контекстом.
        """
        response = self.authorized_client.get(
            reverse(
                DETAIL,
                kwargs={'post_id': self.post.id},
            )
        )

        profile = {'post': self.post}

        for value, expected in profile.items():
            with self.subTest(value=value):
                context = response.context[value]
                self.assertEqual(context, expected)

    def test_posts_not_from_foreign_group(self):
        """
        Проверка, при указании группы поста, попадает
        ли он в другую группу.
        """
        response = self.authorized_client.get(reverse('posts:index'))
        self.posts_check_all_fields(response.context['page_obj'][0])
        post = response.context['page_obj'][0]
        group = post.group
        self.assertEqual(group, self.group)


class PostsPaginatorViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=AUTH)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title=TEST_NAME,
            slug=TEST_SLAG,
            description=TEST_DISCRIP,
        )
        bilk_post: list = []
        for count in range(TEST_OF_POST):
            bilk_post.append(Post(text=f'Тестовый текст {count}',
                                  group=cls.group,
                                  author=cls.user))
        Post.objects.bulk_create(bilk_post)

    def test_paginator_on_pages(self):
        """Проверка пагинации на страницах."""
        posts_first_page = 10
        posts_second_page = 3
        url_pages = [
            reverse(INDEX),
            reverse(GROUP_LIST, kwargs={'slug': self.group.slug}),
            reverse(PROFILE, kwargs={'username': self.user.username}),
        ]
        for reverse_ in url_pages:
            with self.subTest(reverse_=reverse_):
                self.assertEqual(len(self.authorized_client.get(
                    reverse_).context.get('page_obj')),
                    posts_first_page
                )
                self.assertEqual(len(self.authorized_client.get(
                    reverse_ + '?page=2').context.get('page_obj')),
                    posts_second_page
                )
