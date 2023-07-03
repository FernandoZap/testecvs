from django.db import connection
from . import funcoes
from .models import Evento

def listagemParticipacao(id_municipio,ano,mes):
    cursor = connection.cursor()
    anomes=ano+str(int(mes)+100)[-2:]
    cursor.execute("select fm.cod_servidor,fu.funcao,fu.id_funcao,fm.suporte,fm.vinculo,fm.carga_horaria_origem,fm.carga_horaria,fm.salario,\
    fm.salario_100H,fm.vencimento_base,fm.participacao \
    from folhames fm,funcoes fu \
    where fm.id_funcao=fu.id_funcao and fm.fundeb='S' \
    and fm.id_municipio=%s and fm.anomes=%s order by fm.suporte,fm.vinculo,fu.funcao",[id_municipio,anomes])
    return funcoes.dictfetchall(cursor)


def listagemAmpliacao(id_municipio,ano,mes):
    lista_eventos=tuple([k.id_evento for k in Evento.objects.filter(id_municipio=id_municipio,ampliacao_ch='S')])
    cursor = connection.cursor()
    anomes=ano+str(int(mes)+100)[-2:]
    if lista_eventos:
        cursor.execute("select fm.cod_servidor,fu.funcao,fu.id_funcao,fm.suporte,fm.vinculo,fm.carga_horaria_origem,fm.carga_horaria,fm.salario,\
        fm.salario_100H,fm.vencimento_base,fm.participacao,fe.valor,(fe.valor/fm.salario_100H) as ampliacao \
        from folhames fm,funcoes fu,folhaeventos fe \
        where fm.id_funcao=fu.id_funcao and fm.fundeb='S' \
        and fm.id_municipio=fe.id_municipio and fm.anomes=fe.anomes and fm.cod_servidor=fe.cod_servidor \
        and fm.id_municipio=%s and fm.anomes=%s and fe.id_evento in %s \
        order by fm.suporte,fm.vinculo,fu.funcao",[id_municipio,anomes,lista_eventos])
        return funcoes.dictfetchall(cursor)
    return None

def listagemCargaHoraria(id_municipio,ano,mes):
    cursor = connection.cursor()
    anomes=ano+str(int(mes)+100)[-2:]
    cursor.execute("select fm.carga_horaria_origem,fm.carga_horaria,fu.funcao,fu.id_funcao,CAST(fm.salario_100H AS DECIMAL(0)) as salario_100H_int,min(salario_100H) AS salario_100H \
    from folhames fm,funcoes fu where fm.id_municipio=%s and fm.anomes=%s and fu.id_funcao=fm.id_funcao AND salario_100H is not null \
    and fm.fundeb='S' group by fm.carga_horaria_origem,fm.carga_horaria,fu.funcao,fu.id_funcao,CAST(fm.salario_100H AS DECIMAL(0)) \
    order by fu.funcao,fu.id_funcao,carga_horaria_origem,carga_horaria,salario_100H_int",[id_municipio,anomes])
    return funcoes.dictfetchall(cursor)



