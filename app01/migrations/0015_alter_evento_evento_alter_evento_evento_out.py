# Generated by Django 4.0.1 on 2023-02-02 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0014_folhames_vinculo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evento',
            name='evento',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='evento',
            name='evento_out',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]