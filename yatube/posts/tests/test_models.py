from django.test import TestCase

from posts.models import Group, Post, User

MAX_LIGHT_TEXT = 15
TEST_POST = 'Текст статьи'
TEST_GROUP = 'Группа статей'
TEST_SLUG ='Тестовый слаг'
TEST_DESCRIPT = 'Тестовое описание'
NAME_GROUP = 'Название группы'
SLUG = 'Ссылка на группу'
DESCRIPT = 'Описание группы'
AUTH = 'Автор статьи'


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=AUTH)
        cls.group = Group.objects.create(
            title=TEST_GROUP,
            slug=TEST_SLUG,
            description=TEST_DESCRIPT,
        )    

        cls.post = Post.objects.create(
            author=cls.user,
            text=TEST_POST,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей и моделей группы корректно работает __str__."""
        with self.subTest(str=str):
            self.assertEqual(self.post.text[:MAX_LIGHT_TEXT], str(self.post))
            self.assertEqual(self.group.title, str(self.group))

    def test_verbose_name(self):
        """verbose_name в полях модели совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'text': TEST_POST,
            'author': AUTH,
            'group': TEST_GROUP,
        }
        for field, expected in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected)
