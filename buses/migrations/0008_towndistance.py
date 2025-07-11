# Generated by Django 5.1.6 on 2025-06-20 16:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("buses", "0007_populate_busses"),
    ]

    operations = [
        migrations.CreateModel(
            name="TownDistance",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("distance_km", models.FloatField()),
                ("duration_minutes", models.IntegerField()),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "from_town",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="distances_from",
                        to="buses.town",
                    ),
                ),
                (
                    "to_town",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="distances_to",
                        to="buses.town",
                    ),
                ),
            ],
            options={
                "unique_together": {("from_town", "to_town")},
            },
        ),
    ]
