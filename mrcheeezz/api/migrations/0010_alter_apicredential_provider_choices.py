from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0009_apicredential_provider_config_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="apicredential",
            name="provider",
            field=models.CharField(
                choices=[
                    ("spotify", "Spotify"),
                    ("twitch", "Twitch"),
                    ("roblox", "Roblox"),
                    ("discord", "Discord"),
                    ("steam", "Steam"),
                ],
                max_length=32,
                unique=True,
            ),
        ),
    ]
