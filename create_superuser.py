import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def main():
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='raissa.azevedo@artefact.com',
            password='R@issinha92'
        )
        print("Superuser 'admin' criado!")
        return

    print("Superuser já existe!")


if __name__ == '__main__':
    main()