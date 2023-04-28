from django import forms
from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile

from ..forms import PostForm
from ..models import Group, Post, User, Follow

import shutil
import tempfile


class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.author = User.objects.create_user(
            username='Test_name',
            email='test@gmail.com',
        )
        cls.group = Group.objects.create(
            title='Первая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.group2 = Group.objects.create(
            title='Вторая группа',
            slug='test_slug_two',
            description='Описание второй группы'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text="Тестовый пост",
            group=cls.group,
            image=uploaded,
        )
        cls.post_create_urls = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:profile', kwargs={'username': cls.author.username}):
                    'posts/profile.html',
            reverse(
                'posts:group_list', kwargs={'slug': cls.group.slug}):
                    'posts/group_list.html',
        }
        cls.template_page_name = {
            reverse(
                'posts:post_detail', kwargs={'post_id': cls.post.pk}):
                    'posts/post_detail.html',
            reverse(
                'posts:post_create'): 'posts/post_create.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': cls.post.pk}):
                    'posts/post_create.html',
            **cls.post_create_urls,
        }
        cls.form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_pages_uses_correct_template(self):
        """Проверка шаблонов."""
        for reverse_name, template in self.template_page_name.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def assert_post(self, post):
        """Функция проверки контекста"""
        with self.subTest(post=post):
            self.assertEqual(
                post.text, self.post.text)
            self.assertEqual(
                post.author, self.post.author)
            self.assertEqual(
                post.group, self.post.group)

    def test_index_page_show_correct_context(self):
        """Проверка index с правильным ли context."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assert_post(response.context['page_obj'][0])
        post_image = Post.objects.first().image
        self.assertEqual(post_image, 'posts/small.gif')

    def test_group_list_page_show_correct_context(self):
        """Проверка group_list с правильным ли context."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            )
        )
        self.assertEqual(response.context['group'], self.group)
        self.assert_post(response.context['page_obj'][0])
        post_image = Post.objects.first().image
        self.assertEqual(post_image, 'posts/small.gif')

    def test_profile_page_show_correct_context(self):
        """Проверка profile с правильным ли context."""
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.author}
            )
        )
        self.assertEqual(response.context['author'], self.author)
        self.assert_post(response.context['page_obj'][0])
        post_image = Post.objects.first().image
        self.assertEqual(post_image, 'posts/small.gif')

    def test_detail_page_show_correct_context(self):
        """Проверка post_detail с правильниым ли context."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            )
        )
        self.assert_post(response.context['post'])
        post_image = Post.objects.first().image
        self.assertEqual(post_image, 'posts/small.gif')

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form = response.context.get('form')
        self.assertIsInstance(form, PostForm)
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = form.fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.pk}))
        form = response.context.get('form')
        self.assertIsInstance(form, PostForm)
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = form.fields.get(value)
                self.assertIsInstance(form_field, expected)
                self.assertTrue(response.context.get('is_edit'))

    def test_new_post_is_shown(self):
        """Проверьте, что если при создании поста указать группу,
        то этот пост появляется:
        -- на главной странице сайта,
        -- на странице выбранной группы,
        -- в профайле пользователя.
        """
        for url in self.post_create_urls:
            with self.subTest(value=url):
                response = self.client.get(url)
                self.assertIn(self.post, response.context['page_obj'])

    def test_new_post_for_your_group(self):
        """Проверка, что этот пост не попал в группу,
        для которой не был предназначен."""
        response = self.client.get(
            reverse('posts:group_list', kwargs={'slug': self.group2.slug})
        )
        self.assertNotIn(self.post, response.context['page_obj'])

    def test_cache_index(self):
        """Кэширования главной страницы."""
        first = self.authorized_client.get(reverse('posts:index'))
        post = Post.objects.get(pk=1)
        post.text = 'Измененный текст'
        post.save()
        second = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(first.content, second.content)
        cache.clear()
        third = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(first.content, third.content)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(
            username='auth',
        )
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test_slug',
            description='Тестовое описание группы',
        )
        cls.posts_on_first_page = settings.NUMBER_POSTS
        cls.posts_on_second_page = 3
        for i in range(cls.posts_on_second_page + cls.posts_on_first_page):
            Post.objects.create(
                text=f'Пост №{i}',
                author=cls.author,
                group=cls.group
            )

    def test_paginator_on_pages(self):
        """Проверка пагинации на страницах."""
        url_pages = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile',
                    kwargs={'username': self.author.username}),
        ]
        for reverse_page in url_pages:
            with self.subTest(reverse_page=reverse_page):
                self.assertEqual(len(self.client.get(
                    reverse_page).context.get('page_obj')),
                    self.posts_on_first_page
                )
                self.assertEqual(len(self.client.get(
                    reverse_page + '?page=2').context.get('page_obj')),
                    self.posts_on_second_page
                )


class FollowTests(TestCase):
    def setUp(self):
        self.client_auth_follower = Client()
        self.client_auth_following = Client()
        self.user_follower = User.objects.create(username='follower')
        self.user_following = User.objects.create(username='following')
        self.post = Post.objects.create(
            author=self.user_following,
            text='Тестовая запись для тестирования ленты'
        )
        self.client_auth_follower.force_login(self.user_follower)
        self.client_auth_following.force_login(self.user_following)

    def test_follow(self):
        self.client_auth_follower.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.user_following.username}
            )
        )
        self.assertEqual(Follow.objects.all().count(), 1)

    def test_unfollow(self):
        self.client_auth_follower.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.user_following.username},
            )
        )
        self.client_auth_follower.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.user_following.username},
            )
        )
        self.assertEqual(Follow.objects.all().count(), 0)

    def test_subscription(self):
        """Запись появляется в ленте подписчиков."""
        Follow.objects.create(
            user=self.user_follower,
            author=self.user_following
        )
        response = self.client_auth_follower.get('/follow/')
        self.assertEqual(
            response.context['page_obj'][0].text,
            'Тестовая запись для тестирования ленты',
        )
        self.assertNotEqual(
            self.client_auth_following.get('/follow/'),
            'Тестовая запись для тестирования ленты',
        )

    def test_add_comment(self):
        """Проверка добавления комментария."""
        self.client_auth_following.post(
            f'/posts/{self.post.pk}/comment/',
            {'text': 'тестовый комментарий'},
            follow=True
        )
        self.assertContains(
            self.client_auth_following.get(f'/posts/{self.post.pk}/'),
            'тестовый комментарий',
        )
        self.client_auth_following.logout()
        self.client_auth_following.post(
            f'/posts/{self.post.pk}/comment/',
            {'text': 'комментарий от гостя'},
            follow=True)
        self.assertNotContains(
            self.client_auth_following.get(f'/posts/{self.post.pk}/'),
            'комментарий от гостя',
        )
