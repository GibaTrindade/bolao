# Generated by Django 4.2.10 on 2024-02-15 02:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bolao', '0009_alter_ranking_pontuacao'),
    ]

    operations = [
        migrations.AddField(
            model_name='bolao',
            name='imagem',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
        migrations.AddField(
            model_name='bolao',
            name='imagem_base64',
            field=models.TextField(blank=True, null=True),
        ),
    ]
