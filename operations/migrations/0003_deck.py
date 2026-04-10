from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("operations", "0002_authorizedemail"),
    ]

    operations = [
        migrations.CreateModel(
            name="Deck",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("name", models.CharField(max_length=255)),
                ("document_link", models.URLField()),
                ("category", models.CharField(choices=[("pitch", "Pitch"), ("proposal", "Proposal"), ("report", "Report"), ("reference", "Reference"), ("other", "Other")], default="pitch", max_length=100)),
                ("source_name", models.CharField(blank=True, max_length=255)),
                ("tags", models.CharField(blank=True, max_length=255)),
                ("notes", models.TextField(blank=True)),
            ],
            options={
                "db_table": "decks",
                "ordering": ["name"],
            },
        ),
    ]