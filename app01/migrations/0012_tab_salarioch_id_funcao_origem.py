# Generated by Django 4.0.1 on 2023-01-15 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0011_caratersalario_posgraduation_delete_apelido_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tab_salarioch',
            name='id_funcao_origem',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]