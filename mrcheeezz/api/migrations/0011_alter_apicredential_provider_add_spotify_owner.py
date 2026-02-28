from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0010_alter_apicredential_provider_choices"),
    ]

    operations = [
        migrations.AlterField(
            model_name="apicredential",
            name="provider",
            field=models.CharField(
                choices=[
                    ("spotify", "Spotify"),
                    ("spotify_owner", "Spotify (Owner)"),
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
