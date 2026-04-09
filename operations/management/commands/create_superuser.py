from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Cria superuser se não existir'

    def handle(self, *args, **kwargs):
        User = get_user_model()

        if not User.objects.filter(username='raissa').exists():
            User.objects.create_superuser(
                username='raissa',
                email='raissa.azevedo@artefact.com',
                password='R@issinha92'
            )
            self.stdout.write(self.style.SUCCESS('Superuser criado!'))
        else:
            self.stdout.write('Superuser já existe')