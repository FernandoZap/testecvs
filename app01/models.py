from __future__ import unicode_literals
from django.db import connection
from django.db import models
from . import choices



#SET FOREIGN_KEY_CHECKS = 0;
#heroku run python manage.py shell --app civitas-plataforma

# TUTORIAL How to Reset Migrations
#https://simpleisbetterthancomplex.com/tutorial/2016/07/26/how-to-reset-migrations.html

    #Restaurar o auto-increment no pgadmin
#http://blog.abraseucodigo.com.br/problemas-com-postgres-django-sequences.html
'''
neste exemplo estamos corrigindo o problema na tabela eventos_cv
SELECT c.relname FROM pg_class c WHERE c.relkind = 'S';
select * from eventos_cv_id_evento_cv_seq
select count(*) from eventos_cv
SELECT setval('eventos_cv_id_evento_cv_seq', 137);

observacao: o valor 137 é o resultado do select  count(*).
from app01.models import Folhames,Folhaevento,Refeventos,Evento
Folhames.objects.filter(id_municipio=85).delete()

'''

# lista = [f.name for f in User._meta.get_fields()]

#https://www.sankalpjonna.com/learn-django/running-a-bulk-update-with-django


class Municipio(models.Model):
    id_municipio = models.AutoField(primary_key=True)
    municipio = models.CharField(max_length=100)
    empresa = models.CharField(max_length=100,default='')
    entidade = models.CharField(max_length=100,default='')

    def __str__(self):
        return self.municipio

    class Meta:
            db_table = "municipios"

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE {}'.format(cls._meta.db_table))

class Servidor(models.Model):
    id_servidor = models.AutoField(primary_key=True)
    id_municipio = models.IntegerField()
    nome = models.CharField(max_length=100)
    cod_servidor = models.IntegerField()
    cpf = models.CharField(max_length=20,default='')
    data_admissao = models.DateField(null=True)
    ativo = models.IntegerField(default=1)

    def __str__(self):
        return self.nome

    class Meta:
        db_table = 'servidores'
        constraints = [
            models.UniqueConstraint(fields=['id_municipio', 'cod_servidor'], name='servidor_unique')
        ]
        indexes = [
            models.Index(fields=['id_municipio'])
        ]

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE {}'.format(cls._meta.db_table))

class Secretaria(models.Model):
    id_secretaria = models.AutoField(primary_key=True)
    id_municipio = models.IntegerField(null=False)
    id_secretaria_out = models.IntegerField(default=0)
    secretaria = models.CharField(max_length=100)
    secretaria_out = models.CharField(max_length=100,null=True,default='')
    fundeb = models.CharField(max_length=1,default='N')
    tipo = models.IntegerField(null=False,default=1)

    def __str__(self):
        return self.secretaria

    class Meta:
        db_table = "secretarias"
        constraints = [
            models.UniqueConstraint(fields=['id_municipio','secretaria'], name='unique_secretaria')
        ]

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE {}'.format(cls._meta.db_table))

class Setor(models.Model):
    id_setor = models.AutoField(primary_key=True)
    id_municipio = models.IntegerField(null=False)
    id_setor_out = models.IntegerField(default=0)
    setor = models.CharField(max_length=100)
    setor_out = models.CharField(max_length=100,null=True,blank=True)
    fundeb = models.CharField(max_length=1,default='N')
    tipo = models.IntegerField(null=False,default=1)

    def __str__(self):
        return self.setor


    class Meta:
        db_table = 'setores'
        constraints = [
            models.UniqueConstraint(fields=['id_municipio','setor'], name='unique_setor')
        ]

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE {}'.format(cls._meta.db_table))


class Funcao(models.Model):
    id_funcao = models.AutoField(primary_key=True)
    id_municipio = models.IntegerField(null=False)
    id_funcao_out = models.IntegerField(default=0,null=False)
    funcao = models.CharField(max_length=100)
    funcao_out = models.CharField(max_length=100,blank=True,null=True)
    professor = models.CharField(max_length=1,blank=False,null=False,default='N')
    cancelado = models.CharField(max_length=1,default='N')
    tipo = models.IntegerField(null=False,default=1)

    def __str__(self):
        return self.funcao

    class Meta:
        db_table = 'funcoes'
        constraints = [
            models.UniqueConstraint(fields=['id_municipio','funcao'], name='unique_funcao')
        ]


    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE {}'.format(cls._meta.db_table))

class Evento(models.Model):
    id_evento = models.AutoField(primary_key=True)
    id_municipio = models.IntegerField(null=False)
    id_evento_out = models.IntegerField(default=0)
    evento = models.CharField(max_length=100)
    evento_out = models.CharField(max_length=100,null=True,blank=True)
    ampliacao_ch = models.CharField(max_length=1,default='N')
    suporte = models.CharField(max_length=1,default='N',blank=True,null=True)
    cancelado = models.CharField(max_length=1,default='N')
    posgraduacao = models.CharField(max_length=1,default='N',blank=True,null=True)
    carater_salario = models.CharField(max_length=1,default='N',blank=True,null=True)
    tipo = models.IntegerField(null=False,default=1)

    def __str__(self):
        return self.evento

    class Meta:
        db_table = 'eventos'

class Vinculo(models.Model):
    id_vinculo = models.AutoField(primary_key=True)
    id_municipio = models.IntegerField(null=False)
    vinculo = models.CharField(max_length=100)
    grupo = models.CharField(max_length=1,null=True,default='N')

    def __str__(self):
        return self.vinculo

    class Meta:
        db_table = 'vinculos'
        constraints = [
            models.UniqueConstraint(fields=['id_municipio','vinculo'], name='unique_vinculo')
        ]


    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE {}'.format(cls._meta.db_table))


class Folhames(models.Model):
    id_folha = models.AutoField(primary_key=True)
    id_municipio = models.IntegerField(null=True)
    anomes = models.IntegerField()
    cod_servidor = models.IntegerField()
    cpf = models.CharField(max_length=11, null=True)
    id_secretaria = models.IntegerField(null=True)
    id_setor = models.IntegerField(null=True)
    id_funcao = models.IntegerField(null=True)
    id_vinculo = models.IntegerField(null=True)
    previdencia = models.CharField(max_length=6, null=True)
    num_dias = models.IntegerField(null=True)
    salario = models.DecimalField(max_digits=9, decimal_places=3,null=True)
    salario_100H = models.DecimalField(max_digits=9, decimal_places=3,null=True)
    vencimento_base = models.DecimalField(max_digits=9, decimal_places=2,null=True)
    participacao = models.DecimalField(max_digits=9, decimal_places=6,null=True)
    fundeb = models.CharField(max_length=1, null=True,default='N')
    carga_horaria = models.IntegerField(null=True)
    data_criacao = models.DateTimeField(null=True)
    ampliacao_ch = models.CharField(max_length=1, null=True,default='N')
    suporte = models.CharField(max_length=1, null=True,default='N')
    posgraduacao = models.CharField(max_length=1, null=True,default='N')
    carater_salario = models.CharField(max_length=1, null=True,default='N')
    id_secretaria_origem = models.IntegerField(null=True)
    id_setor_origem = models.IntegerField(null=True)
    id_funcao_origem = models.IntegerField(null=True)
    vinculo = models.CharField(max_length=2, null=False,default='N')
    carga_horaria_origem = models.IntegerField(null=True)
    grupo = models.CharField(max_length=2, null=False,default='N')

    def __str__(self):
        return self.cod_servidor

    class Meta:
        db_table = 'folhames'
        indexes = [
            models.Index(fields=['id_municipio','anomes'])
        ]

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE {}'.format(cls._meta.db_table))

class Folhaevento(models.Model):
    id_folhaevento = models.AutoField(primary_key=True)
    id_municipio = models.IntegerField(null=True)
    anomes = models.IntegerField()
    cod_servidor = models.IntegerField()
    previdencia = models.CharField(max_length=6, null=True)
    cl_orcamentaria = models.CharField(max_length=6, null=True)
    id_evento = models.IntegerField(null=True)
    tabela = models.IntegerField(null=True)
    valor = models.DecimalField(max_digits=9, decimal_places=2, default=0)

    def __str__(self):
        return self.cod_servidor

    class Meta:
        db_table = 'folhaeventos'
        indexes = [
            models.Index(fields=['id_municipio','anomes'])
        ]

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE {}'.format(cls._meta.db_table))



class Funcionario(models.Model):
    id_funcionario = models.AutoField(primary_key=True)
    id_municipio = models.IntegerField(null=True)
    anomes = models.IntegerField(null=True)
    codigo = models.IntegerField(null=True)
    nome_servidor = models.CharField(max_length=100, null=True)
    carga_horaria = models.IntegerField(null=True)
    tipo_admissao = models.CharField(max_length=100,null=True)
    data_admissao = models.CharField(max_length=10,null=True)
    previdencia = models.CharField(max_length=100, null=True)
    id_funcao = models.IntegerField(null=True)
    id_setor = models.IntegerField(null=True)
    id_secretaria = models.IntegerField(null=True)
    id_secretaria_origem = models.IntegerField(null=True)
    id_setor_origem = models.IntegerField(null=True)
    id_funcao_origem = models.IntegerField(null=True)
    fundeb = models.CharField(max_length=1,null=False,default='N')
    carga_horaria_origem = models.IntegerField(null=True)

    def __str__(self):
        return self.nome_servidor

    class Meta:
        db_table = 'funcionarios'
        indexes = [
            models.Index(fields=['id_municipio','anomes','codigo'])
        ]

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE {}'.format(cls._meta.db_table))

class Provento(models.Model):
    id_provento = models.AutoField(primary_key=True)
    id_municipio = models.IntegerField(null=True)
    anomes = models.IntegerField(null=True)
    codigo = models.IntegerField(null=True)
    previdencia = models.CharField(max_length=100, null=True,default='')
    tipo = models.IntegerField(null=True)
    id_evento = models.IntegerField(null=True)
    id_evento_origem = models.IntegerField(null=True)
    tabela  = models.IntegerField(null=True)
    valor_evento = models.DecimalField(max_digits=9, decimal_places=2,null=True)
    classificacao = models.CharField(max_length=15, null=True)
    grupamento = models.CharField(max_length=1, null=True,default='S')
    lixo = models.IntegerField(null=True,default=0)

    def __str__(self):
        return self.codigo

    class Meta:
        db_table = 'proventos'
        indexes = [
            models.Index(fields=['id_municipio','anomes','codigo'])
        ]

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE {}'.format(cls._meta.db_table))


class Complemento(models.Model):
    id_complemento = models.AutoField(primary_key=True)
    id_municipio = models.IntegerField(null=True)
    anomes = models.IntegerField(null=True)
    codigo = models.IntegerField(null=True)
    salario = models.DecimalField(max_digits=9, decimal_places=3,null=True)
    salario_100H = models.DecimalField(max_digits=9, decimal_places=3,null=True)
    num_dias = models.IntegerField(null=True)
    participacao = models.DecimalField(max_digits=9, decimal_places=6,null=True)
    vencimento_base = models.DecimalField(max_digits=9, decimal_places=2,null=True)
    fundeb = models.CharField(max_length=1, null=True,default='N')

    def __str__(self):
        return self.codigo

    class Meta:
        db_table = 'complementos'
        indexes = [
            models.Index(fields=['id_municipio','anomes','codigo'])
        ]

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE {}'.format(cls._meta.db_table))


class Ampliacao_ch(models.Model):
    id_seq = models.AutoField(primary_key=True)
    id_municipio = models.IntegerField(null=True)
    anomes = models.IntegerField(null=True)
    cod_servidor = models.IntegerField(null=True)

    def __str__(self):
        return self.cod_servidor

    class Meta:
        db_table = 'ampliacao_ch'
        indexes = [
            models.Index(fields=['id_municipio','anomes','cod_servidor'])
        ]

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE {}'.format(cls._meta.db_table))

class Suporte(models.Model):
    id_seq = models.AutoField(primary_key=True)
    id_municipio = models.IntegerField(null=True)
    anomes = models.IntegerField(null=True)
    cod_servidor = models.IntegerField(null=True)

    def __str__(self):
        return self.cod_servidor

    class Meta:
        db_table = 'suportes'
        indexes = [
            models.Index(fields=['id_municipio','anomes','cod_servidor'])
        ]

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE {}'.format(cls._meta.db_table))

class Tab_salario(models.Model):
    id = models.AutoField(primary_key=True)
    id_municipio = models.IntegerField()
    id_funcao = models.IntegerField()
    carga_horaria = models.IntegerField(null=True)
    valor = models.DecimalField(max_digits=9, decimal_places=2,null=True)

    class Meta:
        db_table = 'tab_salarios'

class Tab_salarioch(models.Model):
    id = models.AutoField(primary_key=True)
    id_municipio = models.IntegerField()
    id_funcao_origem = models.IntegerField()
    valor = models.DecimalField(max_digits=9, decimal_places=2,null=True)
    carga_horaria_errada = models.IntegerField(null=True)
    carga_horaria_certa = models.IntegerField(null=True)

    class Meta:
        db_table = 'tab_salariosch'


class LogErro(models.Model):
    id_logerro = models.AutoField(primary_key=True)
    id_municipio = models.IntegerField()
    anomes = models.IntegerField(default=0)
    numero_linha = models.IntegerField(null=True)
    codigo = models.CharField(max_length=100, null=True)
    observacao = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.codigo

    class Meta:
        db_table = 'logerro'


    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE {}'.format(cls._meta.db_table))


class Setor_fundeb(models.Model):
    id_municipio = models.IntegerField(null=True)
    id_setor = models.IntegerField(null=True)

    class Meta:
        db_table = 'setor_fundeb'
        constraints = [
            models.UniqueConstraint(fields=['id_municipio','id_setor' ], name='unique_setorfundebs')
        ]

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE {}'.format(cls._meta.db_table))


class Situacao(models.Model):
    id_municipio = models.IntegerField()
    anomes = models.IntegerField()
    nome = models.CharField(max_length=100)
    cod_servidor = models.IntegerField()
    data_admissao = models.DateField(null=True)
    natureza = models.IntegerField()
    id_secretaria = models.IntegerField()
    id_setor = models.IntegerField()
    id_funcao = models.IntegerField()
    id_evento = models.IntegerField()
    id_secretaria_origem = models.IntegerField()
    id_setor_origem = models.IntegerField()
    id_funcao_origem = models.IntegerField()
    id_evento_origem = models.IntegerField()
    suporte = models.CharField(max_length=1, null=False, default='N')

    def __str__(self):
        return self.nome

    class Meta:
        db_table = "situacoes"

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE {}'.format(cls._meta.db_table))


class Salario(models.Model):
    id_municipio = models.IntegerField()
    anomes = models.IntegerField()
    cod_servidor = models.IntegerField()
    vencimento_base = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    carga_horaria = models.IntegerField()
    num_dias = models.IntegerField()
    carga_horaria_origem=models.IntegerField()
    num_dias_origem=models.CharField(max_length=50, null=True)
    salario_100h = models.DecimalField(max_digits=9, decimal_places=2,null=False,default=0)
    participacao = models.DecimalField(max_digits=5, decimal_places=2,null=False,default=0)

    class Meta:
        db_table = "salarios"

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE {}'.format(cls._meta.db_table))


class SemCadastro(models.Model):
    id = models.AutoField(primary_key=True)
    id_municipio = models.IntegerField()
    tabela = models.CharField(max_length=50, null=False)
    descricao = models.CharField(max_length=100, null=False)

    class Meta:
        db_table = 'semcadastros'

    def __str__(self):
        return self.descricao

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE {}'.format(cls._meta.db_table))


class Tabela_salario(models.Model):
    id = models.AutoField(primary_key=True)
    id_municipio = models.IntegerField()
    id_funcao_origem = models.IntegerField()
    salario_100h_int = models.IntegerField(null=False,default=0)
    salario_100h_dec = models.DecimalField(max_digits=9, decimal_places=2,null=True)

    class Meta:
        db_table = 'tabela_salarios'

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE {}'.format(cls._meta.db_table))

class Information(models.Model):
    id = models.AutoField(primary_key=True)
    id_municipio = models.IntegerField()
    anomes = models.IntegerField()
    codigo = models.IntegerField()
    nome = models.CharField(max_length=150, null=False)
    carga_horaria = models.IntegerField()
    secretaria = models.CharField(max_length=150, null=False)
    funcao = models.CharField(max_length=150, null=False)
    num_dias = models.IntegerField()
    valor_evento = models.DecimalField(max_digits=9, decimal_places=2,null=False,default=0)
    num_mes = models.IntegerField()
    cod_evento = models.IntegerField()
    data_admissao = models.DateTimeField(null=True)
    salario_base = models.DecimalField(max_digits=9, decimal_places=2,null=False,default=0)

    class Meta:
        db_table = 'informations'

    def __str__(self):
        return self.nome

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE {}'.format(cls._meta.db_table))


class XEvento (models.Model):
    id = models.AutoField(primary_key=True)
    id_municipio = models.IntegerField(null=False)
    tipo = models.CharField(max_length=100,null=False)
    id_evento = models.IntegerField(null=False)

    class Meta:
        db_table = 'xeventos'
        indexes = [
            models.Index(fields=['id_municipio','tipo'])
        ]
        constraints = [
            models.UniqueConstraint(fields=['id_municipio','tipo','id_evento'], name='unique_xevento')
        ]

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE {}'.format(cls._meta.db_table))


class Tabela (models.Model):
    id = models.AutoField(primary_key=True)
    id_municipio = models.IntegerField(null=False)
    grupo = models.CharField(max_length=30,null=False)
    descricao = models.CharField(max_length=150,null=False)

    class Meta:
        db_table = 'tabelas'
        indexes = [
            models.Index(fields=['id_municipio','grupo'])
        ]

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE {}'.format(cls._meta.db_table))


class Posgraduation(models.Model):
    id_seq = models.AutoField(primary_key=True)
    id_municipio = models.IntegerField(null=True)
    anomes = models.IntegerField(null=True)
    cod_servidor = models.IntegerField(null=True)

    def __str__(self):
        return self.cod_servidor

    class Meta:
        db_table = 'posgraduations'
        indexes = [
            models.Index(fields=['id_municipio','anomes','cod_servidor'])
        ]

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE {}'.format(cls._meta.db_table))



class CaraterSalario(models.Model):
    id_seq = models.AutoField(primary_key=True)
    id_municipio = models.IntegerField(null=True)
    anomes = models.IntegerField(null=True)
    cod_servidor = models.IntegerField(null=True)

    def __str__(self):
        return self.cod_servidor

    class Meta:
        db_table = 'caratersalarios'
        indexes = [
            models.Index(fields=['id_municipio','anomes','cod_servidor'])
        ]

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE {}'.format(cls._meta.db_table))



class CargaHoraria(models.Model):
    id_cargahoraria = models.AutoField(primary_key=True)
    id_municipio = models.IntegerField(null=False)
    cargah_origem = models.IntegerField(null=False)
    cargah_convertida = models.IntegerField(null=False)

    def __str__(self):
        return self.id_cargahoraria

    class Meta:
        db_table = 'cargahorarias'
        indexes = [
            models.Index(fields=['id_municipio','cargah_origem'])      ]

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE {}'.format(cls._meta.db_table))



class Documento(models.Model):
    id_documento = models.AutoField(primary_key=True)
    id_municipio = models.IntegerField(null=False)
    anomes = models.IntegerField(null=False)
    ano = models.IntegerField(null=False,default=2000)
    nome_do_arquivo = models.CharField(max_length=150, null=False)
    tipo = models.CharField(max_length=30, null=False)
    id_user = models.IntegerField(null=False,default=0)
    created_at = models.DateTimeField(auto_now_add=True,null=True)

    def __str__(self):
        return self.nome_do_arquivo

    class Meta:
        db_table = 'documentos'
        indexes = [
            models.Index(fields=['id_municipio','anomes'])      ]

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE {}'.format(cls._meta.db_table))


