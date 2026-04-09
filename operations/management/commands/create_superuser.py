from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        User = get_user_model()

        user, created = User.objects.get_or_create(username='raissa')

        user.email = 'raissa.azevedo@artefact.com'
        user.set_password('123456')  # senha simples pra teste
        user.is_staff = True
        user.is_superuser = True
        user.save()

        print("SUPERUSER RESETADO")