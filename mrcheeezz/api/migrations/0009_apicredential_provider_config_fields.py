from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0008_alter_apicredential_provider"),
    ]

    operations = [
        migrations.AddField(
            model_name="apicredential",
            name="client_id",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="apicredential",
            name="client_secret",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="apicredential",
            name="redirect_uri",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="apicredential",
            name="config",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
