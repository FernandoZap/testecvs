# -*- coding: utf-8 -*-
import openpyxl, pprint
import os
import sys
from datetime import datetime
from django.db.models import Count,Sum
import unicodedata
#from openpyxl.styles import NamedStyle
from .models import Secretaria,Setor,Servidor,Folhames,Folhaevento,LogErro,Funcao,Evento,Funcionario,Provento,Complemento,Vinculo,Posgraduation,CaraterSalario,Ampliacao_ch

from . import listagens
from django.db import connection


def dictfetchall(cursor):
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]

def importarServidores(id_municipio,anomes,empresa):

    erro=0
    objetos=[]
    lista=[]
    lista_servidores=listagens.listagemServidores(id_municipio)
    lista_servidores_verificados=[]

    lista_incluidos=[]
    lista_cpf=[]
    codigo_folha=int(str(anomes)[4:6])


    queryP = Funcionario.objects.values(
        'codigo',
        'nome_servidor',
        'data_admissao').annotate(Count('codigo')).filter(id_municipio=id_municipio,anomes=anomes)

    for qp in range(len(queryP)):



        codigo = queryP[qp]['codigo']
        nome_servidor = queryP[qp]['nome_servidor']
        data_admissao = queryP[qp]['data_admissao']
        dt_admissao = datetime.strptime(data_admissao, '%Y-%m-%d').date()


        nome_servidor=nome_servidor.strip()
        nome_servidor=remover_acentuacao(nome_servidor)
        nome_servidor=nome_servidor.upper()

        if codigo not in lista_servidores_verificados:
            if str(codigo) not in lista_servidores:
                if codigo not in lista_incluidos:
                    objeto = Servidor(
                        id_municipio=id_municipio,
                        cod_servidor=codigo,
                        nome = nome_servidor,
                        data_admissao = dt_admissao
                        )
                    objetos.append(objeto)
                    lista_incluidos.append(codigo)
            lista_servidores_verificados.append(codigo)


    Servidor.objects.bulk_create(objetos)
    return 1





def importarFolhaPasso1(id_municipio,anomes,empresa):

    lista_erro_setor=[]
    lista_erro_secretaria=[]
    lista_erro_funcao=[]

    dict_vinculos=listagens.criarDictVinculos(id_municipio,'id')
    dict_vinculosGrupo=listagens.criarDictVinculos(id_municipio,'grupo')
    lista_vinculos = listagens.listagemVinculos(id_municipio)


    listagem_folhames=listagens.listagemFolhames(id_municipio,anomes)

    lista=[]

    objetos=[]
    feventos=[]
    lista_incluidos=[]

    lista_ref_eventos=[]
    obj_ref_ev=[]
    carga_erro=[]
    carga_folhaeventos=[]
    carga_folhames=[]
    carga_refeventos=[]

    carga_erro_secretaria=[]
    carga_erro_setor=[]
    carga_erro_funcao=[]

    codigo_folha=int(str(anomes)[4:6])

    cursor = connection.cursor()
    '''
    cursor.execute("select f.*,c.num_dias,c.salario,c.salario_100H,c.participacao,c.vencimento_base,ch.cod_servidor as ampliacao,s.cod_servidor as suporte, \
        pg.cod_servidor as posgraduacao,cs.cod_servidor as caratersalario \
        from funcionarios f left join complementos c on c.id_municipio=f.id_municipio and c.anomes=f.anomes and c.codigo=f.codigo \
        left join ampliacao_ch ch on ch.cod_servidor=f.codigo and ch.anomes=f.anomes and ch.id_municipio=f.id_municipio \
        left join suportes s on s.cod_servidor=f.codigo and s.id_municipio=f.id_municipio and s.anomes=f.anomes \
        left join posgraduations pg on pg.cod_servidor=f.codigo and pg.id_municipio=f.id_municipio and pg.anomes=f.anomes \
        left join caratersalarios cs on cs.cod_servidor=f.codigo and cs.id_municipio=f.id_municipio and cs.anomes=f.anomes \
        where f.id_municipio=%s and f.anomes=%s",[id_municipio, anomes])
    '''
    cursor.execute("select f.*,c.num_dias,c.salario,c.salario_100H,c.participacao,c.vencimento_base,s.cod_servidor as suporte, \
        pg.cod_servidor as posgraduacao,cs.cod_servidor as caratersalario \
        from funcionarios f left join complementos c on c.id_municipio=f.id_municipio and c.anomes=f.anomes and c.codigo=f.codigo \
        left join suportes s on s.cod_servidor=f.codigo and s.id_municipio=f.id_municipio and s.anomes=f.anomes \
        left join posgraduations pg on pg.cod_servidor=f.codigo and pg.id_municipio=f.id_municipio and pg.anomes=f.anomes \
        left join caratersalarios cs on cs.cod_servidor=f.codigo and cs.id_municipio=f.id_municipio and cs.anomes=f.anomes \
        where f.id_municipio=%s and f.anomes=%s",[id_municipio, anomes])



    queryP = dictfetchall(cursor)
    data_criacao=datetime.today()

    lista_sv_ampliacao = [k.cod_servidor  for k in Ampliacao_ch.objects.filter(id_municipio=id_municipio,anomes=anomes)]


    for qp in queryP:

        cod_servidor = qp['codigo']
        id_secretaria = qp['id_secretaria']
        id_setor = qp['id_setor']
        id_funcao = qp['id_funcao']
        id_funcao_origem = qp['id_funcao_origem']
        vinculo =qp['tipo_admissao']
        previdencia = qp['previdencia']
        carga_horaria = qp['carga_horaria']
        carga_horaria_origem = qp['carga_horaria_origem']
        num_dias = qp['num_dias']
        salario = qp['salario']
        salario_100H = qp['salario_100H']
        fundeb = qp['fundeb']
        vencimento_base = qp['vencimento_base']
        participacao = qp['participacao']
        suporte = qp['suporte']
        posgraduacao = qp['posgraduacao']
        caratersalario = qp['caratersalario']

        if cod_servidor in lista_sv_ampliacao:
            ampliacao_ch='S'
        else:
            ampliacao_ch='N'


        if fundeb is None:
            fundeb='N'

        if suporte is not None:
            suporte='S'
        else:
            suporte='N'

        if posgraduacao is None:
            posgraduacao='N'
        else:
            posgraduacao='S'

        if caratersalario is None:
            caratersalario='N'
        else:
           caratersalario='S'


        vinculo=vinculo.strip()
        previdencia=previdencia.strip()

        vinculo=vinculo.upper()
        previdencia=previdencia.upper()

        vinculo=remover_acentuacao(vinculo)

        if vinculo in lista_vinculos:
            id_vinculo = dict_vinculos[vinculo]
            vinculo = dict_vinculosGrupo[vinculo]
        else:
            id_vinculo=0
            vinculo='N'
        if vinculo=='E':
            grupo='E'
        elif vinculo in ['T','C']:
            grupo='T'
        else:
            grupo=vinculo


        if salario is None:
            salario=0

        if cod_servidor not in lista_incluidos:
            if str(cod_servidor)+'-'+str(anomes) not in listagem_folhames:
                objeto_folhames = Folhames(
                    anomes=anomes,
                    id_municipio=id_municipio,
                    cod_servidor=cod_servidor,
                    id_secretaria=id_secretaria,
                    id_setor=id_setor,
                    id_funcao=id_funcao,
                    id_funcao_origem=id_funcao_origem,
                    id_vinculo=id_vinculo,
                    vinculo=vinculo,
                    previdencia=previdencia,
                    num_dias = num_dias,
                    salario = salario,
                    salario_100H = salario_100H,
                    vencimento_base=vencimento_base,
                    carga_horaria=carga_horaria,
                    carga_horaria_origem=carga_horaria_origem,
                    data_criacao=data_criacao,
                    participacao=participacao,
                    fundeb=fundeb,
                    ampliacao_ch=ampliacao_ch,
                    suporte=suporte,
                    posgraduacao=posgraduacao,
                    carater_salario=caratersalario,
                    grupo=grupo
                    )

                carga_folhames.append(objeto_folhames)
                lista_incluidos.append(cod_servidor)

    cursor.close()
    del cursor


    if len(lista_erro_secretaria)>0:
        for kk in range(len(lista_erro_secretaria)):
            obj=LogErro(
                id_municipio=id_municipio,
                anomes=anomes,
                numero_linha=0,
                codigo='secretaria',
                observacao=lista_erro_secretaria[kk]
                )
            carga_erro_secretaria.append(obj)

    if len(lista_erro_setor)>0:
        for kk in range(len(lista_erro_setor)):
            obj=LogErro(
                id_municipio=id_municipio,
                anomes=anomes,
                numero_linha=0,
                codigo='setor',
                observacao=lista_erro_setor[kk]
                )
            carga_erro_setor.append(obj)

    if len(lista_erro_funcao)>0:
        for kk in range(len(lista_erro_funcao)):
            obj=LogErro(
                id_municipio=id_municipio,
                anomes=anomes,
                numero_linha=0,
                codigo='funcao',
                observacao=lista_erro_funcao[kk]
                )
            carga_erro_funcao.append(obj)


    if len(lista_erro_setor)>0:
        LogErro.objects.bulk_create(carga_erro_setor)

    if len(lista_erro_secretaria)>0:
        LogErro.objects.bulk_create(carga_erro_secretaria)

    if len(lista_erro_funcao)>0:
        LogErro.objects.bulk_create(carga_erro_funcao)

    Folhames.objects.bulk_create(carga_folhames)
    return 1


def importarFolhaPasso3(id_municipio,anomes,empresa):

    lista_erro_evento=[]
    listagem_folhames=listagens.listagemFolhames(id_municipio,anomes)
    lista=[]

    objetos=[]
    feventos=[]
    lista_incluidos=[]

    carga_erro=[]
    carga_folhaeventos=[]
    carga_folhames=[]

    carga_erro_evento=[]
    lista_erro_evento=[]
    lista_incluidos=[]
    carga_erro=[]
    carga_folhaeventos=[]
    carga_folhames=[]
    carga_erro_evento=[]

    queryS = Provento.objects.filter(id_municipio=id_municipio,anomes=anomes,grupamento__in=['S','s']).values('codigo','id_evento','id_evento_origem','previdencia','classificacao').annotate(valor_evento=Sum('valor_evento')).order_by('codigo')            


    for qp in range(len(queryS)):

        cod_servidor = queryS[qp]['codigo']
        previdencia = queryS[qp]['previdencia']
        cl_orcamentaria = queryS[qp]['classificacao']
        id_evento = queryS[qp]['id_evento']
        id_evento_origem = queryS[qp]['id_evento_origem']
        tabela = 1
        valor = queryS[qp]['valor_evento']

        obj_feventos = Folhaevento(
                id_municipio = id_municipio,
                anomes = anomes,
                cod_servidor = cod_servidor,
                previdencia = previdencia,
                cl_orcamentaria = cl_orcamentaria,
                id_evento = id_evento,
                tabela = tabela,
                valor = valor
            )

        carga_folhaeventos.append(obj_feventos)

    if len(lista_erro_evento)>0:
        for kk in range(len(lista_erro_evento)):
            obj=LogErro(
                id_municipio=id_municipio,
                anomes=anomes,
                numero_linha=0,
                codigo='evento',
                observacao=lista_erro_evento[kk]
                )
            carga_erro_evento.append(obj)


    if len(lista_erro_evento)>0:
        LogErro.objects.bulk_create(carga_erro_evento)

    if len(carga_folhaeventos)>0:
        Folhaevento.objects.bulk_create(carga_folhaeventos)

    return 1




def remover_acentuacao(string: str) -> str:
    normalized = unicodedata.normalize('NFD', string)
    return ''.join(
        [l for l in normalized if not unicodedata.combining(l)]
    )


