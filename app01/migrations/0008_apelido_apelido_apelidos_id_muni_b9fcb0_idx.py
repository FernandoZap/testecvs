# Generated by Django 4.0.1 on 2022-11-20 19:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0007_delete_apelido'),
    ]

    operations = [
        migrations.CreateModel(
            name='Apelido',
            fields=[
                ('id_descricao', models.AutoField(primary_key=True, serialize=False)),
                ('id_municipio', models.IntegerField()),
                ('descricao', models.CharField(max_length=120)),
                ('descricao_out', models.CharField(max_length=120)),
                ('id_descricao_out', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'apelidos',
            },
        ),
        migrations.AddIndex(
            model_name='apelido',
            index=models.Index(fields=['id_municipio', 'descricao'], name='apelidos_id_muni_b9fcb0_idx'),
        ),
    ]
