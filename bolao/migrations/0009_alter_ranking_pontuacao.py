# Generated by Django 4.2.10 on 2024-02-15 02:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bolao', '0008_ranking'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ranking',
            name='pontuacao',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]
