# Generated by Django 4.0.1 on 2022-12-06 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0010_alter_complemento_salario_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CaraterSalario',
            fields=[
                ('id_seq', models.AutoField(primary_key=True, serialize=False)),
                ('id_municipio', models.IntegerField(null=True)),
                ('anomes', models.IntegerField(null=True)),
                ('cod_servidor', models.IntegerField(null=True)),
            ],
            options={
                'db_table': 'caratersalarios',
            },
        ),
        migrations.CreateModel(
            name='Posgraduation',
            fields=[
                ('id_seq', models.AutoField(primary_key=True, serialize=False)),
                ('id_municipio', models.IntegerField(null=True)),
                ('anomes', models.IntegerField(null=True)),
                ('cod_servidor', models.IntegerField(null=True)),
            ],
            options={
                'db_table': 'posgraduations',
            },
        ),
        migrations.DeleteModel(
            name='Apelido',
        ),
        migrations.AddField(
            model_name='evento',
            name='carater_salario',
            field=models.CharField(blank=True, default='N', max_length=1, null=True),
        ),
        migrations.AddField(
            model_name='evento',
            name='posgraduacao',
            field=models.CharField(blank=True, default='N', max_length=1, null=True),
        ),
        migrations.AddField(
            model_name='folhames',
            name='carater_salario',
            field=models.CharField(default='N', max_length=1, null=True),
        ),
        migrations.AddField(
            model_name='folhames',
            name='posgraduacao',
            field=models.CharField(default='N', max_length=1, null=True),
        ),
        migrations.AddIndex(
            model_name='posgraduation',
            index=models.Index(fields=['id_municipio', 'anomes', 'cod_servidor'], name='posgraduati_id_muni_b18ba6_idx'),
        ),
        migrations.AddIndex(
            model_name='caratersalario',
            index=models.Index(fields=['id_municipio', 'anomes', 'cod_servidor'], name='caratersala_id_muni_ed9c25_idx'),
        ),
    ]
