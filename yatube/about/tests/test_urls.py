from http import HTTPStatus

from django.test import TestCase, Client


class AboutUrlsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.urls_names_template = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html'
        }

    def testing_urls_exists(self):
        """Тестируем URL-адреса существуют ли в нужном месте."""
        for urls_address in self.urls_names_template:
            with self.subTest(urls_address):
                response = self.guest_client.get(urls_address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def testing_urls_correct_templates(self):
        """Тестируем URL-адреса используется ли правильные шаблоны."""
        for url, template in self.urls_names_template.items():
            with self.subTest(template=template):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
