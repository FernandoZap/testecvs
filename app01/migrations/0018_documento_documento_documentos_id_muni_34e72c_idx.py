# Generated by Django 4.0.1 on 2023-03-20 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0017_folhames_carga_horaria_origem_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Documento',
            fields=[
                ('id_documento', models.AutoField(primary_key=True, serialize=False)),
                ('id_municipio', models.IntegerField()),
                ('anomes', models.IntegerField()),
                ('nome_do_arquivo', models.CharField(max_length=150)),
                ('tipo', models.CharField(max_length=30)),
            ],
            options={
                'db_table': 'documentos',
            },
        ),
        migrations.AddIndex(
            model_name='documento',
            index=models.Index(fields=['id_municipio', 'anomes'], name='documentos_id_muni_34e72c_idx'),
        ),
    ]
