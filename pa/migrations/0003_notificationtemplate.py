from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pa", "0002_remove_action_date_debut_remove_action_date_fin_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="NotificationTemplate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("subject", models.CharField(max_length=255)),
                ("body_html", models.TextField(blank=True)),
                ("body_text", models.TextField(blank=True)),
                ("is_default", models.BooleanField(default=False)),
            ],
        ),
    ]
