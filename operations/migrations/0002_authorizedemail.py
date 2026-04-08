from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("operations", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AuthorizedEmail",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("is_active", models.BooleanField(default=True)),
                ("notes", models.CharField(blank=True, max_length=255)),
            ],
            options={
                "verbose_name": "Authorized email",
                "verbose_name_plural": "Authorized emails",
                "ordering": ["email"],
            },
        ),
    ]