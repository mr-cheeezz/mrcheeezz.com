from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("settings", "0009_remove_sitesetting_blur_dropdown_sitesetting_theme_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sitesetting",
            name="pfp_aura",
            field=models.CharField(default="auto", max_length=16),
        ),
    ]
