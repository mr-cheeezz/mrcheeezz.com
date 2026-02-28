from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("settings", "0010_alter_sitesetting_pfp_aura"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesetting",
            name="game_links_enabled",
            field=models.BooleanField(default=True),
        ),
    ]

