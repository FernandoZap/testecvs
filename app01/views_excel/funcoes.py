# -*- coding: utf-8 -*-
import os
import sys
import re
from ..models import LogErro,Municipio,Funcao,Evento,Folhaevento
from . import listagens
import zipfile
import re
from django.db import connection
from django.db.models import Count,Sum
import unidecode
import unicodedata



def mesPorExtenso(mes,modelo):

    lista_mes=['','JANEIRO','FEVEREIRO','MARÇO','ABRIL','MAIO','JUNHO','JULHO','AGOSTO','SETEMBRO','OUTUBRO','NOVEMBRO','DEZEMBRO']
    if modelo==1:
        return lista_mes[int(mes)]
    elif modelo==2:
        return (lista_mes[int(mes)])[0:3]


def mesReferencia(mes):
    lista_mes=['','JANEIRO','FEVEREIRO','MARÇO','ABRIL','MAIO','JUNHO','JULHO','AGOSTO','SETEMBRO','OUTUBRO','NOVEMBRO','DEZEMBRO']
    return lista_mes[int(mes)]


def cabecalhoFolha(id_municipio,eventos):
    lista=[]

    lista.append('Secretaria')
    lista.append('Setor')
    lista.append('Matricula')
    lista.append('Nome')
    lista.append('Funcao')
    lista.append('Vinculo')
    lista.append('DataAdmissao')
    lista.append('CargaHoraria')
    lista.append('Dias')

    #lista_eventos = [ob.evento for ob in Evento.objects.filter(id_municipio=id_municipio,cancelado='N',tipo='V',exibe_excel=1).order_by('evento')]
    lista_eventos = eventos


    for kk in range(len(lista_eventos)):
        lista.append(lista_eventos[kk])
    lista.append('Soma')

    return lista



def modelos(string_id_municipio):
    modelos_lista = [('86', 2), ('76', 1)]
    modelos = dict(modelos_lista)
    return modelos[string_id_municipio]


def strings_pesquisa(id_municipio):

    lista1=[]
    lista2=[]
    secs = Municipio.objects.all()
    for sec in secs:
        lista1.append(
            str(sec.id_municipio)
            )
        lista2.append(
            'PREFEITURA MUNICIPAL DE '+(sec.municipio).upper()
            )

    dicionario = dict(zip(lista1,lista2))
    return dicionario[str(id_municipio)]

def entidade(id_municipio):
    munic = Municipio.objects.get(id_municipio=id_municipio)
    lista=[]
    if munic is not None:
        lista.append(munic.municipio)
        lista.append(munic.empresa)
        lista.append(munic.entidade)
    return lista



def nome_do_municipio(id_municipio):

    lista1=[]
    lista2=[]
    secs = Municipio.objects.all()
    for sec in secs:
        lista1.append(
            sec.id_municipio
            )
        lista2.append(
            (sec.municipio).upper()
            )

    dicionario = dict(zip(lista1,lista2))
    return dicionario[id_municipio]


def eventosMes(id_municipio,anomes):
    cursor = connection.cursor()
    cursor.execute("select fm.cod_servidor,ev.id_evento, ev.evento_out as evento,coalesce(fm.valor,0) as valor \
    from eventos ev inner join folhaeventos fm on fm.id_evento=ev.id_evento and \
    fm.anomes=%s and fm.id_municipio=%s \
    where ev.tipo='V' order by cod_servidor",[anomes,id_municipio])

    query = dictfetchall(cursor)
    for kk in range(0,len(query)):
        cod_servidor=query[kk]['cod_servidor']
        break

    lst1=[]
    lst2=[]
    lst3=[]
    for kk in range(0,len(query)):
        flag=0
        if query[kk]['cod_servidor'] not in lst1:
            if len(lst3)>0:
                lst2.append(lst3)
            lst1.append(query[kk]['cod_servidor'])
            lst3=[]
            lst3.append(
                {
                    'evento':query[kk]['evento'],
                    'valor':query[kk]['valor']
                }
            )
        else:
            lst3.append(
                {
                    'evento':query[kk]['evento'],
                    'valor':query[kk]['valor']
                }
            )
    lst2.append(lst3)
    return dict(zip(lst1,lst2))



def dictfetchall(cursor):
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]


def gravarErro_01(id_municipio,anomes,observacao):
    log=LogErro(id_municipio=id_municipio,anomes=anomes,observacao=observacao)
    log.save()
    return 'ok'

def remove_accents(input_str):
    nkfd_form = unicodedata.normalize('NFKD', input_str)
    only_ascii = nkfd_form.encode('ASCII', 'ignore')
    return only_ascii

def to_ascii(ls):
    for i in range(len(ls)):
        ls[i] = unidecode.unidecode(ls[i])
    return ls

def to_ascii_string(string):
    return unidecode.unidecode(string)


def remove_combining_fluent(string: str) -> str:
    normalized = unicodedata.normalize('NFD', string)
    return ''.join(
        [l for l in normalized if not unicodedata.combining(l)]
    )


def montarDiciionarioEventoDoServidor(eventosDoServidor):
    lista1=[]
    lista2=[]
    for kk in range(len(eventosDoServidor)):
        lista1.append(eventosDoServidor[kk]['evento'])
        lista2.append(eventosDoServidor[kk]['valor'])
    return dict(zip(lista1,lista2))


def montaListaEventoDoServidor(eventosDoServidor):
    lista=[]
    for kk in range(len(eventosDoServidor)):
        lista.append(eventosDoServidor[kk]['evento'])
    return lista



def eventosMesDoServidor(id_municipio,anomes):
    # esta funcao monta um dicionario do codigo dos servidores e a lista de seus eventos e valores
    # [serv1:[{'vencimento base',1212},{'gratificacao',650}],serv2:[{'vencimento base',1850},{'gratificacao',650}]]
    lista1=[]
    lista2=[]
    lista3=[]
    dicionarioIdEvento=listagens.criarDictEventos(id_municipio)
    query=Folhaevento.objects.filter(id_municipio=id_municipio,anomes=anomes).values('cod_servidor','id_evento','valor').order_by('cod_servidor')
    for q in query:
        if q['cod_servidor'] not in lista1:
            lista1.append(q['cod_servidor'])
            if len(lista3)>0:
                lista2.append(lista3)
                lista3=[]
            lista3.append(
                {
                'evento':dicionarioIdEvento[q['id_evento']],
                'valor':q['valor']
                }
                )
        else:
            lista3.append(
                {
                'evento':dicionarioIdEvento[q['id_evento']],
                'valor':q['valor']
                }
                )
    lista2.append(lista3)
    return dict(zip(lista1,lista2))


def montarDicionarioEventoDoServidor(eventosDoServidor):
    lista1=[]
    lista2=[]
    for kk in range(len(eventosDoServidor)):
        lista1.append(eventosDoServidor[kk]['evento'])
        lista2.append(eventosDoServidor[kk]['valor'])
    return dict(zip(lista1,lista2))

def formatMilhar(valor):
    if valor=='':
        return valor
    elif valor is None:
        return valor
    if valor<0:
        valor=valor*(-1)
        sinal='-'
    else:
        sinal=''

    vd = f"{valor:,.2f}"
    vd = vd.replace('.','-')
    vd = vd.replace(',','.')
    vd = vd.replace('-',',')
    return sinal+vd

