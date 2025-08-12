from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ("pa", "0010_templates_automations_menus"),
    ]

    operations = [
        migrations.CreateModel(
            name="AssistantWeights",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("delay", models.IntegerField(default=2)),
                ("priority", models.IntegerField(default=1)),
                ("status", models.IntegerField(default=1)),
                ("pdca", models.IntegerField(default=1)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
