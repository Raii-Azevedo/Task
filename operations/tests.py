from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import AuthorizedEmail


class AuthenticationFlowTests(TestCase):
	def setUp(self):
		self.password = "SecurePass123!"
		self.email = "nome.sobrenome@artefact.com"
		self.user = get_user_model().objects.create_user(
			username=self.email,
			email=self.email,
			password=self.password,
		)

	def test_dashboard_requires_login(self):
		response = self.client.get(reverse("dashboard"))

		self.assertRedirects(response, f"{reverse('login')}?next={reverse('dashboard')}")

	def test_authorized_email_can_login(self):
		AuthorizedEmail.objects.create(email=self.email)

		response = self.client.post(
			reverse("login"),
			{"username": self.email, "password": self.password},
		)

		self.assertRedirects(response, reverse("dashboard"))

	def test_login_requires_authorized_email(self):
		response = self.client.post(
			reverse("login"),
			{"username": self.email, "password": self.password},
		)

		self.assertContains(response, "Este email ainda nao esta autorizado no admin.")

	def test_login_rejects_non_corporate_email(self):
		external_email = "pessoa@gmail.com"
		get_user_model().objects.create_user(
			username=external_email,
			email=external_email,
			password=self.password,
		)
		AuthorizedEmail.objects.create(email=external_email)

		response = self.client.post(
			reverse("login"),
			{"username": external_email, "password": self.password},
		)

		self.assertContains(response, "Use um email corporativo @artefact.com.")
