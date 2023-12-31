# Generated by Django 4.0.1 on 2022-11-19 11:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0004_delete_apelido'),
    ]

    operations = [
        migrations.CreateModel(
            name='Apelido',
            fields=[
                ('id_secretaria', models.AutoField(primary_key=True, serialize=False)),
                ('id_municipio', models.IntegerField()),
                ('secretaria', models.CharField(max_length=30)),
                ('secretaria_out', models.CharField(max_length=150)),
                ('id_secretaria_out', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'apelidos',
            },
        ),
        migrations.AddIndex(
            model_name='apelido',
            index=models.Index(fields=['id_municipio', 'secretaria'], name='apelidos_id_muni_a3d444_idx'),
        ),
    ]
