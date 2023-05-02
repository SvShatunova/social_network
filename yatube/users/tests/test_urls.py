from django.test import TestCase, Client

from posts.models import User
from http import HTTPStatus


class UsersUrlsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(
            username='Test_name',
            email='test@gmail.com',
            password='password',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        self.urls_names_guest = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/<uidb64>/<token>/':
                'users/password_reset_confirm.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
            '/auth/logout/': 'users/logged_out.html',
        }
        self.urls_names_authorized = {
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
        }
        self.merged_dict = {
            **self.urls_names_guest,
            **self.urls_names_authorized,
        }

    def test_urls_exists_guest(self):
        """Доступность страниц любому пользователю."""
        for address in self.urls_names_guest:
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_urls_exists_authorized(self):
        """Недоступность страниц любому пользователю."""
        for address in self.urls_names_authorized:
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.FOUND.value)

    def test_urls_exists_redirect(self):
        """Доступность страниц авторизованному пользователю."""
        for address in self.urls_names_authorized:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_urls_correct_template(self):
        """Соответствие шаблонов не авторизованному пользователю."""
        for address, template in self.urls_names_guest.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_correct_template(self):
        """Соответствие шаблонов авторизованному пользователю."""
        for address, template in self.urls_names_authorized.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
