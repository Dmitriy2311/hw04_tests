from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User
from posts.tests.test_constant import (
    INDEX, POST_CREATE, GROUP_LIST, PROFILE, TEST_POST, POST_ID,
    EDIT, AUTH, TEST_NAME, TEST_SLUG, TEST_DISCRIP, PAGE, POST,
    INDEX, POST_CREATE, GROUP_LIST, DETAIL, TEST_OF_POST, FORM,
    INDEX_HTML, CREATE_HTML, GROUP_LIST_HTML, SLUG, USER_NAME,
    PAGE_OBJ, AUTHOR, TEXT, GROUP
)


class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=AUTH)
        cls.group = Group.objects.create(
            title=TEST_NAME,
            slug=TEST_SLUG,
            description=TEST_DISCRIP,
        )

        cls.post = Post.objects.create(
            text=TEST_POST,
            author=cls.user,
            group=cls.group,
        )
        cls.templates_pages_names = {
            INDEX_HTML: reverse(INDEX),
            CREATE_HTML: reverse(POST_CREATE),
            GROUP_LIST_HTML: reverse(
                GROUP_LIST,
                kwargs={SLUG: TEST_SLUG },
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
        self.posts_check_all_fields(response.context[PAGE_OBJ][0])
        last_post = response.context[PAGE_OBJ][0]
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
                kwargs={SLUG: self.group.slug},
            )
        )
        test_group = response.context[GROUP]
        self.posts_check_all_fields(response.context[PAGE_OBJ][0])
        test_post = str(response.context[PAGE_OBJ][0])
        self.assertEqual(test_group, self.group)
        self.assertEqual(test_post, str(self.post))

    def test_posts_context_create_post_template(self):
        """
        Проверка, сформирован ли шаблон create_post с
        правильным контекстом.
        """
        response = self.authorized_client.get(reverse(POST_CREATE))

        form_fields = {
            GROUP: forms.fields.ChoiceField,
            TEXT: forms.fields.CharField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context[FORM].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_posts_context_post_edit_template(self):
        """
        Проверка, сформирован ли шаблон post_edit с
        правильным контекстом.
        """
        response = self.authorized_client.get(
            reverse(
                EDIT,
                kwargs={POST_ID: self.post.id},
            )
        )

        form_fields = {TEXT: forms.fields.CharField}

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get(FORM).fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_posts_context_profile_template(self):
        """
        Проверка, сформирован ли шаблон profile с
        правильным контекстом.
        """
        response = self.authorized_client.get(
            reverse(
                PROFILE,
                kwargs={USER_NAME: self.user.username},
            )
        )
        profile = {AUTHOR: self.post.author}

        for value, expected in profile.items():
            with self.subTest(value=value):
                context = response.context[value]
                self.assertEqual(context, expected)

        self.posts_check_all_fields(response.context[PAGE_OBJ][0])
        test_page = response.context[PAGE_OBJ][0]
        self.assertEqual(test_page, self.user.posts.all()[0])

    def test_posts_context_post_detail_template(self):
        """
        Проверка, сформирован ли шаблон post_detail с
        правильным контекстом.
        """
        response = self.authorized_client.get(
            reverse(
                DETAIL,
                kwargs={POST_ID: self.post.id},
            )
        )

        profile = {POST: self.post}

        for value, expected in profile.items():
            with self.subTest(value=value):
                context = response.context[value]
                self.assertEqual(context, expected)

    def test_posts_not_from_foreign_group(self):
        """
        Проверка, при указании группы поста, попадает
        ли он в другую группу.
        """
        response = self.authorized_client.get(reverse(INDEX))
        self.posts_check_all_fields(response.context[PAGE_OBJ][0])
        post = response.context[PAGE_OBJ][0]
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
            slug=TEST_SLUG,
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

        PAGE_ONE= 10
        PAGE_TWO = 3

        pages = (
                (1, PAGE_ONE),
                (2, PAGE_TWO)
        )
        url_pages = [
            reverse(INDEX),
            reverse(GROUP_LIST, kwargs={SLUG: self.group.slug}),
            reverse(PROFILE, kwargs={USER_NAME: self.user.username}),
        ]
        for url in url_pages:
            for page, count in pages:
                response = self.client.get(url, {PAGE: page})
                self.assertEqual(
                    len(response.context[PAGE_OBJ]), count,
                )
