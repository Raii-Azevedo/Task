from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import AuthorizedEmail


class AuthenticationFlowTests(TestCase):
	def setUp(self):
		self.email = "nome.sobrenome@artefact.com"

	def test_dashboard_requires_login(self):
		response = self.client.get(reverse("dashboard"))

		self.assertRedirects(response, f"{reverse('login')}?next={reverse('dashboard')}")

	def test_authorized_email_can_login(self):
		AuthorizedEmail.objects.create(email=self.email)

		response = self.client.post(
			reverse("login"),
			{"email": self.email},
		)

		self.assertRedirects(response, reverse("dashboard"))
		user = get_user_model().objects.get(username=self.email)
		self.assertEqual(user.email, self.email)
		self.assertFalse(user.has_usable_password())

	def test_login_requires_authorized_email(self):
		response = self.client.post(
			reverse("login"),
			{"email": self.email},
		)

		self.assertContains(response, "Este email ainda nao esta autorizado no admin.")

	def test_login_rejects_non_corporate_email(self):
		external_email = "pessoa@gmail.com"
		AuthorizedEmail.objects.create(email=external_email)

		response = self.client.post(
			reverse("login"),
			{"email": external_email},
		)

		self.assertContains(response, "Use um email corporativo @artefact.com.")

	def test_existing_user_can_login_without_password(self):
		get_user_model().objects.create_user(username=self.email, email="")
		AuthorizedEmail.objects.create(email=self.email)

		response = self.client.post(reverse("login"), {"email": self.email})

		self.assertRedirects(response, reverse("dashboard"))
		self.assertEqual(get_user_model().objects.get(username=self.email).email, self.email)
