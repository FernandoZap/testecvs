from django.db import connection
from  .models import Funcionario,Provento,Complemento,Ampliacao_ch,Suporte,Folhames,SemCadastro,Municipio
from django.db.models import Sum,Count
import datetime

def funTruncateTables(id_municipio,anomes):
    Funcionario.truncate()
    Provento.truncate()
    Complemento.truncate()
    Ampliacao_ch.truncate()
    Suporte.truncate()
    SemCadastro.truncate()


def atualizarTables():
    cursor = connection.cursor()
    cursor.execute("update secretarias set secretaria_out=secretaria where secretaria_out=''")
    cursor.execute("update setores set setor_out=setor where setor_out=''")
    cursor.execute("update funcoes set funcao_out=funcao where funcao_out=''")
    cursor.execute("update eventos set evento_out=evento where evento_out=''")

    cursor.execute("update secretarias set id_secretaria_out=id_secretaria where id_secretaria_out=0")
    cursor.execute("update setores set id_setor_out=id_setor where id_setor_out=0")
    cursor.execute("update funcoes set id_funcao_out=id_funcao where id_funcao_out=0")
    cursor.execute("update eventos set id_evento_out=id_evento where id_evento_out=0")

    return None


def funFolhames(id_municipio,anomes):
    lista=[]
    number_of_rows = Folhames.objects.filter(id_municipio=id_municipio,anomes=anomes).count()
    if number_of_rows>0:
        lista.append(id_municipio)
        lista.append(anomes)

    return lista

def fun_planilha(planilha,id_municipio,anomes,mesano):
    obj=Municipio.objects.get(id_municipio=id_municipio)
    planilha=planilha.upper()

    if obj is not None:
        entidade=obj.entidade
        entidade=entidade.upper()
        if entidade in planilha:
            if (anomes in planilha or mesano in planilha):
                return 1
    return 0

'''
def listas_TabelaMatriz(id_municipio,anomes,dict_idXfuncao):
    cursor = connection.cursor()
    cursor.execute("select id_funcao,CAST(salario_100H AS DECIMAL(0)) AS salario_100H_int,suporte,vinculo,MIN(salario_100H) AS salario_100H,sum(participacao*carga_horaria/100) as somaParticipacao \
            from folhames  \
            where id_municipio=%s and anomes=%s and fundeb='S' and salario_100H IS NOT NULL group by id_funcao,CAST(salario_100H AS DECIMAL(0)),suporte,vinculo",[id_municipio,anomes])
    query = dictfetchall(cursor)

    cursor.execute("select id_funcao,CAST(salario_100H AS DECIMAL(0)) AS salario_100H_int,suporte,vinculo,MIN(salario_100H) AS salario_100H, count(*) as qtde from folhames \
        where id_municipio=%s and anomes=%s and fundeb='S' and ampliacao_ch='S' and salario>0 and salario_100H IS NOT NULL \
        group by id_funcao,CAST(salario_100H AS DECIMAL(0)),suporte,vinculo",[id_municipio,anomes])
    queryAmpliacao = dictfetchall(cursor)


    lista_auxiliar_regente_efetivo=[]
    lista_auxiliar_regente_temporario=[]
    lista_auxiliar_suporte_efetivo=[]
    lista_auxiliar_suporte_temporario=[]

    lista_regente_efetivo=[]
    lista_regente_temporario=[]
    lista_suporte_efetivo=[]
    lista_suporte_temporario=[]


    lista_ampliacao_regenteE1=[]
    lista_ampliacao_regenteE2=[]
    lista_ampliacao_regenteT1=[]
    lista_ampliacao_regenteT2=[]
    lista_ampliacao_suporteE1=[]
    lista_ampliacao_suporteE2=[]
    lista_ampliacao_suporteT1=[]
    lista_ampliacao_suporteT2=[]

    #preencher lista2_reg e lista2_sup
    for q in query:
        if q['suporte']=='N':
            if q['vinculo']=='E':
                lista_regente_efetivo.append([q['id_funcao'],q['salario_100H'],q['somaParticipacao']])
                lista_auxiliar_regente_efetivo.append([q['id_funcao'],q['salario_100H']])
            else:
                lista_regente_temporario.append([q['id_funcao'],q['salario_100H'],q['somaParticipacao']])
                lista_auxiliar_regente_temporario.append([q['id_funcao'],q['salario_100H']])
        elif q['suporte']=='S':
            if q['vinculo']=='E':
                lista_suporte_efetivo.append([q['id_funcao'],q['salario_100H'],q['somaParticipacao']])
                lista_auxiliar_suporte_efetivo.append([q['id_funcao'],q['salario_100H']])
            else:
                lista_suporte_temporario.append([q['id_funcao'],q['salario_100H'],q['somaParticipacao']])
                lista_auxiliar_suporte_temporario.append([q['id_funcao'],q['salario_100H']])

    #preencher lista1_reg e lista1_sup


    for k in lista_auxiliar_regente_efetivo:
        if k not in lista_auxiliar_suporte_efetivo:
            lista_suporte_efetivo.append([k[0],k[1],0])


    for k in lista_auxiliar_suporte_efetivo:
        if k not in lista_auxiliar_regente_efetivo:
            lista_regente_efetivo.append([k[0],k[1],0])


    for k in lista_auxiliar_regente_temporario:
        if k not in lista_auxiliar_suporte_temporario:
            lista_suporte_temporario.append([k[0],k[1],0])


    for k in lista_auxiliar_suporte_temporario:
        if k not in lista_auxiliar_regente_temporario:
            lista_regente_temporario.append([k[0],k[1],0])


    for q in queryAmpliacao:
        if q['suporte']=='N':
            if q['vinculo']=='E':
                lista_ampliacao_regenteE1.append(str(q['id_funcao'])+'-'+ str(int(q['salario_100H'])))
                lista_ampliacao_regenteE2.append(q['qtde'])
            elif q['vinculo'] in ['T','C']:
                lista_ampliacao_regenteT1.append(str(q['id_funcao'])+'-'+ str(int(q['salario_100H'])))
                lista_ampliacao_regenteT2.append(q['qtde'])
        else:
            if q['vinculo']=='E':
                lista_ampliacao_suporteE1.append(str(q['id_funcao'])+'-'+ str(int(q['salario_100H'])))
                lista_ampliacao_suporteE2.append(q['qtde'])
            elif q['vinculo'] in ['T','C']:
                lista_ampliacao_suporteT1.append(str(q['id_funcao'])+'-'+ str(int(q['salario_100H'])))
                lista_ampliacao_suporteT2.append(q['qtde'])

    dictA_regenteE=dict(zip(lista_ampliacao_regenteE1,lista_ampliacao_regenteE2))
    dictA_regenteT=dict(zip(lista_ampliacao_regenteT1,lista_ampliacao_regenteT2))

    dictA_suporteE=dict(zip(lista_ampliacao_suporteE1,lista_ampliacao_suporteE2))
    dictA_suporteT=dict(zip(lista_ampliacao_suporteT1,lista_ampliacao_suporteT2))

###########################################################################
    if len(lista_ampliacao_regenteE1)>0:
        for k in range(len(lista_regente_efetivo)):
            id_funcao=str(lista_regente_efetivo[k][0])
            participacao=lista_regente_efetivo[k][2]
            sal100=str(int(lista_regente_efetivo[k][1]))

            aplic=dictA_regenteE.get(id_funcao+'-'+sal100,0)
            if aplic>0:
                lista_regente_efetivo[k][2]=participacao+aplic

    if len(lista_ampliacao_regenteT1)>0:
        for k in range(len(lista_regente_temporario)):
            id_funcao=str(lista_regente_temporario[k][0])
            participacao=lista_regente_temporario[k][2]
            sal100=str(int(lista_regente_temporario[k][1]))

            aplic=dictA_regenteT.get(id_funcao+'-'+sal100,0)
            if aplic>0:
                lista_regente_temporario[k][2]=participacao+aplic

    if len(lista_ampliacao_suporteE1)>0:
        for k in range(len(lista_suporte_efetivo)):
            id_funcao=str(lista_suporte_efetivo[k][0])
            participacao=lista_suporte_efetivo[k][2]
            sal100=str(int(lista_suporte_efetivo[k][1]))

            aplic=dictA_suporteE.get(id_funcao+'-'+sal100,0)
            if aplic>0:
                lista_suporte_efetivo[k][2]=participacao+aplic

    if len(lista_ampliacao_suporteT1)>0:
        for k in range(len(lista_suporte_temporario)):
            id_funcao=str(lista_suporte_temporario[k][0])
            participacao=lista_suporte_temporario[k][2]
            sal100=str(int(lista_suporte_temporario[k][1]))

            aplic=dictA_suporteT.get(id_funcao+'-'+sal100,0)
            if aplic>0:
                lista_suporte_temporario[k][2]=participacao+aplic


    for k in range(len(lista_regente_efetivo)):
        lista_regente_efetivo[k][0]=str(dict_idXfuncao.get(lista_regente_efetivo[k][0],0))+'('+str(lista_regente_efetivo[k][0])+')'
        lista_regente_efetivo[k][1]=str(lista_regente_efetivo[k][1])
        lista_regente_efetivo[k][2]=str(lista_regente_efetivo[k][2])


    for k in range(len(lista_suporte_efetivo)):
        lista_suporte_efetivo[k][0]=str(dict_idXfuncao.get(lista_suporte_efetivo[k][0],0))+'('+str(lista_suporte_efetivo[k][0])+')'
        lista_suporte_efetivo[k][1]=str(lista_suporte_efetivo[k][1])
        lista_suporte_efetivo[k][2]=str(lista_suporte_efetivo[k][2])


    for k in range(len(lista_regente_temporario)):
        lista_regente_temporario[k][0]=str(dict_idXfuncao.get(lista_regente_temporario[k][0],0))+'('+str(lista_regente_temporario[k][0])+')'
        lista_regente_temporario[k][1]=str(lista_regente_temporario[k][1])
        lista_regente_temporario[k][2]=str(lista_regente_temporario[k][2])


    for k in range(len(lista_suporte_temporario)):
        lista_suporte_temporario[k][0]=str(dict_idXfuncao.get(lista_suporte_temporario[k][0],0))+'('+str(lista_suporte_temporario[k][0])+')'
        lista_suporte_temporario[k][1]=str(lista_suporte_temporario[k][1])
        lista_suporte_temporario[k][2]=str(lista_suporte_temporario[k][2])

###########################################################################################################

    lista_regente_efetivo.sort()
    lista_suporte_efetivo.sort()
    lista_regente_temporario.sort()
    lista_suporte_temporario.sort()

    return [lista_regente_efetivo,lista_suporte_efetivo,lista_regente_temporario,lista_suporte_temporario]
'''

def dictfetchall(cursor):
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]

'''
def listas_TabelaMatriz_2(id_municipio,anomes):
    cursor = connection.cursor()
    cursor.execute("select fe.id_evento,ev.evento,sum(fe.valor) as soma from folhames fm,folhaeventos fe,eventos ev \
       where fm.id_municipio=fe.id_municipio and fm.anomes=fe.anomes and fm.cod_servidor=fe.cod_servidor\
       and ev.id_municipio=fe.id_municipio\
       and fe.id_municipio=%s and fe.anomes=%s\
       and fm.fundeb='S' and fm.vinculo='E'\
       and fe.id_evento=ev.id_evento\
       group by fe.id_evento,ev.evento",[id_municipio,anomes])
    queryE = dictfetchall(cursor)

    cursor.execute("select fe.id_evento,ev.evento,sum(fe.valor) as soma from folhames fm,folhaeventos fe,eventos ev \
       where fm.id_municipio=fe.id_municipio and fm.anomes=fe.anomes and fm.cod_servidor=fe.cod_servidor\
       and ev.id_municipio=fe.id_municipio\
       and fe.id_municipio=%s and fe.anomes=%s\
       and fm.fundeb='S' and fm.vinculo in ('T','C')\
       and fe.id_evento=ev.id_evento\
       group by fe.id_evento,ev.evento",[id_municipio,anomes])


    queryT = dictfetchall(cursor)

    lista_efetivo=[]
    lista_temporario=[]
    lista_auxiliar_efetivo=[]
    lista_auxiliar_temporario=[]
    lista_resumo=[]

    for q in queryE:
        lista_efetivo.append([q['evento'],q['soma']])
        lista_auxiliar_efetivo.append(q['evento'])

    for q in queryT:
        lista_temporario.append([q['evento'],q['soma']])
        lista_auxiliar_temporario.append(q['evento'])


    for k in range(len(lista_auxiliar_efetivo)):
        if lista_auxiliar_efetivo[k] not in lista_auxiliar_temporario:
           lista_auxiliar_temporario.append(lista_auxiliar_efetivo[k])

    lista=lista_auxiliar_temporario


    lista.sort()

    for k in range(len(lista)):
        item = lista[k]
        valor1 = formatMilhar(float(pesqEvento(item,lista_efetivo)))
        valor2 = formatMilhar(float(pesqEvento(item,lista_temporario)))
        lista_resumo.append([item,valor1,valor2])

    cursor.close()
    del cursor

    return lista_resumo
'''



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


def pesqEvento(item,lista_pesquisa):
    for k in lista_pesquisa:
        if item == k[0]:
            return k[1]
    return 0

def fun_datahora():
    agora =  datetime.datetime.now()
    agora_string = agora.strftime("%A %d %B %y %I:%M")
    agora_datetime = datetime.datetime.strptime(agora_string, "%A %d %B %y %I:%M")
    agora_datetime=str(agora_datetime)
    agora_datetime=agora_datetime.replace('-','')
    agora_datetime=agora_datetime.replace(':','')
    return agora_datetime

