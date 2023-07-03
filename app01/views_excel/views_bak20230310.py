from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseRedirect,Http404
from . import listagens,funcoes
from .. import dicionarios,funcoes as f_funcoes
from decimal import *

from ..models import Municipio,Folhames,Folhaevento,Evento,Vinculo,Funcao,Setor,XEvento
from django.db.models import Count,Sum,Min,Avg,Max,Q
import csv
import datetime
import os
import openpyxl
from django.core.files import File
from django.db import connection
import unicodedata


#def imprimirFolha(request):
#def tabelaRegenteSuporteMatriz(request):
#def tabelaMatriz
#def fun_nova_listaEventos
#def lista_Soma_Eventos
#def dictfetchall
#def lista_Regente_Suporte
#def fun_lista_servidores_com_pos
#def fun_lista_participacao
#def fun_lista_impressao_a
#def coletaDados
#def fun_dictAmpliacaoCh
#def tabelaRegenteSuporte
#def somaEventos
#def lista_SomaEventos
#def fun_Auxiliar_tabelaMatriz


def imprimirFolha(request):
    titulo = 'Impressao do Excel'
    municipios=Municipio.objects.filter(empresa__in=['SS','Layout','Aspec']).order_by('municipio')


    if request.method=='POST':
        id_municipio = request.POST['municipio']
        ano=request.POST['ano']
        mes=request.POST['mes']

        mesx=str(int(mes)+100)[-2:]
        anomes=int(ano+mesx)
        lista=[]

        query=Folhaevento.objects.filter(id_municipio=id_municipio,anomes=anomes).values('id_evento').annotate(soma=Sum('valor'))
        lista_id_evento = [e['id_evento'] for e in query]
        eventos = [ev.evento_out for ev in Evento.objects.filter(id_municipio=id_municipio,id_evento__in=lista_id_evento).order_by('evento')]

        ls_municipio = funcoes.entidade(id_municipio)
        if len(ls_municipio)>0:
            municipio=ls_municipio[0]
            empresa = ls_municipio[1]
            entidade = ls_municipio[2]
        label_arquivo=entidade+'_'+funcoes.mesPorExtenso(mes,1)+'_'+str(ano)+'.csv'


        colunas=listagens.colunasValores()

        ultima_coluna = colunas[len(eventos)+8]

        query=Folhames.objects.filter(id_municipio=id_municipio,anomes=anomes).values('cod_servidor','id_secretaria','id_setor','id_funcao','id_vinculo','previdencia','carga_horaria','num_dias').order_by('cod_servidor')

        dicNomeDoServidor=listagens.criarDictNomeServidor(id_municipio)
        dicNomeDaSecretaria=listagens.criarDictIdSecretarias(id_municipio)
        dicNomeDoSetor=listagens.criarDictIdSetores(id_municipio)
        dicNomeDaFuncao=listagens.criarDictIdFuncoes(id_municipio)
        dicNomeDoVinculo=listagens.criarDictIdVinculos(id_municipio)
        contador=2

        dictEventos=funcoes.eventosMesDoServidor(id_municipio,anomes)
        lista=[]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename='+label_arquivo

        cabecalho = funcoes.cabecalhoFolha(id_municipio,eventos)
        writer = csv.writer(response, delimiter=';')
        response.write(u'\ufeff'.encode('utf8'))
        writer.writerow(cabecalho)

        for qy in query:
            cod_servidor=qy['cod_servidor']


            lista.append(dicNomeDaSecretaria[qy['id_secretaria']])
            lista.append(dicNomeDoSetor.get(qy['id_setor'],'ERRO: '+str(qy['id_setor'])))
            lista.append(cod_servidor)
            lista.append(dicNomeDoServidor[cod_servidor]['nome'])
            lista.append(dicNomeDaFuncao.get(qy['id_funcao'],'ERRO: '+str(qy['id_funcao'])))
            lista.append(dicNomeDoVinculo[qy['id_vinculo']])
            lista.append(dicNomeDoServidor[cod_servidor]['data'])
            lista.append('CH '+str(qy['carga_horaria']))
            lista.append(qy['num_dias'])

            soma = 0

            eventosDoServidor=dictEventos.get(cod_servidor)
            if eventosDoServidor is None:
                lista=[]
                continue

            #[{'evento': 'ADC PTEMPSERV', 'valor': Decimal('381.28')}, {'evento': 'SALARIO BASE', 'valor': Decimal('3177.33')}]
            dicionario=funcoes.montarDicionarioEventoDoServidor(eventosDoServidor)
            #{'ADC PTEMPSERV': Decimal('381.28'), 'SALARIO BASE': Decimal('3177.33')}
            listaEventosDoServidor=funcoes.montaListaEventoDoServidor(eventosDoServidor)

            #['ADC PTEMPSERV', 'SALARIO BASE', 'SALARIO FAMILIA']
            for qq in range(len(eventos)):
                if eventos[qq] in listaEventosDoServidor:
                    valor=dicionario[eventos[qq]]
                    valor_str=str(valor)
                    valor_str = valor_str.replace('.',',')
                else:
                    valor_str='0'
                lista.append(valor_str)


            ci="J"+str(contador)

            cf=ultima_coluna+str(contador)
            formula="=soma("+ci+":"+cf+")"

            contador+=1
            lista.append(formula)

            writer.writerow(lista)
            lista=[]
        return response

    return render(request, 'app01/imprimirFolhaExcel.html',
        {
            'titulo': titulo,
            'municipios':municipios,
            'mensagem':''

        }
    )


def tabelaRegenteSuporteMatriz(request):
    titulo='Tabela Regente/Suporte/Matriz'
    municipios = Municipio.objects.filter(empresa__in=['SS','Layout','Aspec']).order_by('municipio')
    if (request.method == "POST"):
        id_municipio=int(request.POST['municipio'])
        ano=request.POST['ano']
        mes=request.POST['mes']
        tabela=request.POST['tabela']
        tabela=tabela.upper()
        anomes=int(str(ano)+str(int(mes)+100)[-2:])
        if tabela=='MATRIZ':
            return tabelaMatriz(id_municipio,anomes,tabela)
        else:
            return tabelaRegenteSuporte(id_municipio,anomes,tabela)
    return render(request, 'app01/tabelaRegenteSuporteMatriz.html',
            {
                'titulo': titulo,
                'municipios':municipios,
            }
        )

def tabelaMatriz(id_municipio,anomes,tabela):
    if 1==1:
        mesEano=str(anomes)[-2:]+'/'+str(anomes)[0:4]
        obj=Municipio.objects.get(id_municipio=id_municipio)
        municipio=obj.municipio
        tabela=tabela.upper()
        listao = lista_Regente_Suporte(id_municipio,anomes,tabela)
        listao.sort()

        #(ls_somaEfetivo_reg,ls_somaEfetivo_sup,ls_somaTemporario_reg,ls_somaTemporario_sup) = lista_Soma_Eventos(id_municipio,anomes,tabela)
        (listao_soma,resumo_soma)=lista_SomaEventos(id_municipio,anomes)
        listao_soma.sort()
        resumo_soma.sort()

        if tabela=='MATRIZ':
            label_arquivo='tabelaMatriz-'+municipio+'.csv'
            titulo_relatorio='Tabela Matriz'
            primeira_parte=['Regentes e Suporte Efetivo']
            segunda_parte=['Regentes e Suporte Temporário']
            titulo_resumo=['Resumo do Eventos - Regentes Efetivos','Resumo do Eventos - Regentes Temporarios']

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename='+label_arquivo

        #cabecalho = ['Nivel (Função)','100H','200H','Ampl.C.Hora','TOTAL','TOTAL 100H','Vencto','Sal.Base']
        cabecalho1=[titulo_relatorio]
        cabecalho2=[municipio+ '- '+mesEano]

        cabecalho3=['Função ','Regente Total 100h','Suporte Total 100h','Vencimento Base']
        writer = csv.writer(response, delimiter=';')
        response.write(u'\ufeff'.encode('utf8'))
        hlinha=0
        writer.writerow(cabecalho1)
        writer.writerow(cabecalho2)



        for kl in range(2):
            s1=Decimal(0)
            s2=Decimal(0)
            kk1=Decimal(0)
            kk2=Decimal(0)
            if kl==0:
                titulo_regente=primeira_parte[0]
            else:
                titulo_regente=segunda_parte[0]

            writer.writerow([titulo_regente])
            writer.writerow(cabecalho3)
            writer.writerow([''])

            for kreg in listao:
                hlinha+=1
                if kl==0:
                    kk1=funcoes.formatMilhar(kreg[4]+2*kreg[5]+kreg[6])
                    kk2=funcoes.formatMilhar(kreg[10]+2*kreg[11]+kreg[12])
                    s1+=kreg[4]+2*kreg[5]+kreg[6]
                    s2+=kreg[10]+2*kreg[11]+kreg[12]

                    if kreg[4]+kreg[5]+kreg[6]+kreg[10]+kreg[11]+kreg[12]==0:
                        continue

                    writer.writerow(
                        [
                        kreg[1],
                        kk1,
                        kk2,
                        funcoes.formatMilhar(kreg[3]),
                        ]
                    )
                else:
                    s1+=kreg[7]+2*kreg[8]+kreg[9]
                    s2+=kreg[13]+2*kreg[14]+kreg[15]

                    kk1=funcoes.formatMilhar(kreg[7]+2*kreg[8]+kreg[9])
                    kk2=funcoes.formatMilhar(kreg[13]+2*kreg[14]+kreg[15])
                    if kreg[7]+kreg[8]+kreg[9]+kreg[13]+kreg[14]+kreg[15]==0:
                        continue

                    writer.writerow(
                        [
                        kreg[1],
                        kk1,
                        kk2,
                        funcoes.formatMilhar(kreg[3])
                        ]
                    )
            writer.writerow(['Soma',funcoes.formatMilhar(s1),funcoes.formatMilhar(s2)])
            writer.writerow([''])
            writer.writerow([''])
        s3=Decimal(0)
        s4=Decimal(0)
        s5=Decimal(0)
        s6=Decimal(0)

        writer.writerow(['Resumo Geral'])
        writer.writerow(['Funcao','Quantidade Efetivo','Vencto. Base','Custo Efetivo','','Quantidade Temporário','Vencto. Base','Custo Temporário'])

        s1=Decimal(0)
        s2=Decimal(0)
        s3=Decimal(0)
        s4=Decimal(0)


        for kreg in listao:
            (tot1,custo1,tot2,custo2) = fun_Auxiliar_tabelaMatriz(kreg)
            s1+=tot1
            s2+=tot2
            s3+=custo1
            s4+=custo2

            writer.writerow(
                [
                    kreg[1],
                    funcoes.formatMilhar(tot1),
                    funcoes.formatMilhar(kreg[3]),
                    funcoes.formatMilhar(custo1),
                    '',
                    funcoes.formatMilhar(tot2),
                    funcoes.formatMilhar(kreg[3]),
                    funcoes.formatMilhar(custo2)
                ]
            )
        writer.writerow(['Soma',funcoes.formatMilhar(s1),'',funcoes.formatMilhar(s3),'',funcoes.formatMilhar(s2),'',funcoes.formatMilhar(s4)])

        writer.writerow([''])
        writer.writerow([''])
        writer.writerow([''])
        writer.writerow(['Resumo dos Evento'])
        writer.writerow(['Evento','Regente Efetivo','Regente Temporário','Soma 1','Suporte Efetivo','Suporte Temporario','Soma 2','Soma 1+2'])
        for kre in resumo_soma:

            writer.writerow(
                [
                    kre[1],
                    funcoes.formatMilhar(kre[2]),
                    funcoes.formatMilhar(kre[3]),
                    funcoes.formatMilhar(kre[4]),
                    funcoes.formatMilhar(kre[5]),
                    funcoes.formatMilhar(kre[6]),
                    funcoes.formatMilhar(kre[7]),
                    funcoes.formatMilhar(kre[4]+kre[7])
                ]
            )

    

        return response            

    else:
        return render(request, 'app01/tabelaRegenteSuporte.html',
            {
                'titulo': 'Tabela Regente/Suporte/Matriz',
                'municipios':municipios,
            }
        )

def fun_nova_listaEventos(id_municipio,anomes):
    cursor = connection.cursor()
    cursor.execute("Select fm.suporte,case when fm.vinculo in ('T','C') then 'T' \
    else 'E' end as vinculo,fe.id_evento,sum(valor) as soma \
    from folhames fm,folhaeventos fe \
    where fm.id_municipio=fe.id_municipio and fm.anomes=fe.anomes and fm.cod_servidor=fe.cod_servidor\
    and fm.id_municipio=%s and fm.anomes=%s \
    and fm.fundeb='S' and fm.vinculo in ('E','T','C')\
    group by fm.suporte,fm.vinculo,fe.id_evento",[id_municipio,anomes])
    query = dictfetchall(cursor)
    return query




def dictfetchall(cursor):
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]


def lista_Soma_Eventos(id_municipio,anomes,tabela):
    lista_regente_efetivo=[]
    lista_regente_temporario=[]
    lista_suporte_efetivo=[]
    lista_suporte_temporario=[]      
    dicionario=listagens.criarDictEventos(id_municipio)          
    #lista_eventos_carater_salario=[ev.id_evento for ev in Evento.objects.filter(id_municipio=id_municipio,carater_salario='S')]
    lista_eventos_pos=[ev.id_evento for ev in Evento.objects.filter(id_municipio=id_municipio,posgraduacao='S')]
    lista_eventos_suporte=[ev.id_evento for ev in Evento.objects.filter(id_municipio=id_municipio,suporte='S')]
    lista_eventos_salBase=[ev.id_evento for ev in Evento.objects.filter(id_municipio=id_municipio,evento='VENCIMENTO BASE')]
    
    lista_soma=fun_nova_listaEventos(id_municipio,anomes) 
    for k in lista_soma:
        ordenacao=8
        tipo_evento='adicional'
        id_evento=k['id_evento']
        desc_evento=dicionario.get(id_evento,'')
        soma=k['soma']
        if id_evento in lista_eventos_suporte:
            tipo_evento='suporte'
            ordenacao=4
        elif id_evento in lista_eventos_salBase:
            tipo_evento='salario-base'
            ordenacao=1
        else:
            tipo_evento='adicional'
            ordenacao=8

        if k['suporte']=='S':
            if k['vinculo']=='E':
                lista_suporte_efetivo.append([ordenacao,tipo_evento,desc_evento,soma])
            else:
                lista_suporte_temporario.append([ordenacao,tipo_evento,desc_evento,soma])
        else:
            if k['vinculo']=='E':
                lista_regente_efetivo.append([ordenacao,tipo_evento,desc_evento,soma])
            else:
                lista_regente_temporario.append([ordenacao,tipo_evento,desc_evento,soma])
    lista_regente_efetivo.sort()
    lista_regente_temporario.sort()
    lista_suporte_efetivo.sort()
    lista_suporte_temporario.sort()
    if tabela=='REGENTE':
        return [lista_regente_efetivo,lista_regente_temporario]
    elif tabela=='SUPORTE':
        return [lista_suporte_efetivo,lista_suporte_temporario]
    else:
        return [lista_regente_efetivo,lista_suporte_efetivo,lista_regente_temporario,lista_suporte_temporario]                


def lista_Regente_Suporte(id_municipio,anomes,tabela):

    if 1==1:
        tp_evento_ampliacao_ch=()
        lista = [k.id_evento for k in Evento.objects.filter(id_municipio=id_municipio,ampliacao_ch='S')]
        for kl in lista:
            tp_evento_ampliacao_ch += (kl,)

        lista_eventos_suporte = [k.id_evento for k in Evento.objects.filter(id_municipio=id_municipio,suporte='S')]
        lista_eventos_carater_salario = [k.id_evento for k in Evento.objects.filter(id_municipio=id_municipio).filter(carater_salario='S')]

        tupla=tuple([k.id_evento for k in Evento.objects.filter(id_municipio=id_municipio).filter(posgraduacao='S')])

        if id_municipio==44 and anomes==202302:
            tupla=[]


        if tupla:
            tupla_servidores_com_pos=tuple(fun_lista_servidores_com_pos(id_municipio,anomes,tupla))
        else:
            tupla_servidores_com_pos=[]

        if tupla_servidores_com_pos:
            qFolha_com_pos=fun_lista_participacao(id_municipio,anomes,tupla_servidores_com_pos,True)
        else:
            qFolha_com_pos=[]

        qFolha_sem_pos=fun_lista_participacao(id_municipio,anomes,tupla_servidores_com_pos,False)

        tupla_eventos_ampliacao = tuple([k.id_evento for k in Evento.objects.filter(id_municipio=id_municipio,ampliacao_ch='S')])
        '''
        for k in qFolha_sem_pos:
            print (k['id_funcao'])
        '''
        listao=fun_lista_impressao_a(qFolha_sem_pos,qFolha_com_pos,tupla_servidores_com_pos,tupla_eventos_ampliacao,id_municipio,anomes)

        ''' 
        for k in listao[0:15]:
            print(k)
        '''

        return listao


def fun_lista_servidores_com_pos(id_municipio,anomes,lista_eventos_posgraduacao):
    lista=[]
    cursor = connection.cursor()
    cursor.execute("select distinct fe.cod_servidor from folhaeventos fe,folhames fm \
    where fe.id_municipio=%s and fm.fundeb='S' and fm.vinculo in ('E','T','C') \
    and fe.id_municipio=fm.id_municipio and fe.anomes=fm.anomes and fe.cod_servidor=fm.cod_servidor \
    and fe.anomes=%s and fe.id_evento in %s",[id_municipio,anomes,lista_eventos_posgraduacao]) 
    query = dictfetchall(cursor)
    for kl in query:
        lista.append(kl['cod_servidor'])
    return lista


def fun_lista_participacao(id_municipio,anomes,tupla_profs_com_pos,posgraduacao):
    cursor = connection.cursor()    
    if not posgraduacao and tupla_profs_com_pos:
        # sem pos, mas como existe professor com pos temos que informar essa lista
        cursor.execute("Select fu.id_funcao,CAST(salario_100H AS DECIMAL(0)) as salario_100H_int,carga_horaria,fm.suporte, \
        case when fm.vinculo in ('T','C') then 'T' \
        else 'E' end as vinculo, \
        MIN(salario_100H) AS salario_100H,sum(participacao) as somaParticipacao,sum(vencimento_base) as somaVencimento \
        from folhames fm,funcoes fu where fm.id_municipio=%s and anomes=%s \
        and fm.fundeb='S' and fm.vinculo in ('E','T','C') \
        and fu.id_funcao=fm.id_funcao and fu.id_municipio=fm.id_municipio\
        and fm.cod_servidor not in %s \
        and salario>0 group by fu.id_funcao,salario_100H_int,carga_horaria,fm.suporte,fm.vinculo order by fm.id_funcao,salario_100H_int",[id_municipio,anomes,tupla_profs_com_pos])
    elif not posgraduacao and not tupla_profs_com_pos:
        # sem pos, mas não existe professor com pos
        cursor.execute("Select fu.id_funcao,CAST(salario_100H AS DECIMAL(0)) as salario_100H_int,carga_horaria,fm.suporte, \
        case when fm.vinculo in ('T','C') then 'T' \
        else 'E' end as vinculo, \
        MIN(salario_100H) AS salario_100H,sum(participacao) as somaParticipacao,sum(vencimento_base) as somaVencimento \
        from folhames fm,funcoes fu where fm.id_municipio=%s and anomes=%s \
        and fm.fundeb='S' and fm.vinculo in ('E','T','C') \
        and fu.id_funcao=fm.id_funcao and fu.id_municipio=fm.id_municipio\
        and salario>0 group by fu.id_funcao,salario_100H_int,carga_horaria,fm.suporte,fm.vinculo order by fm.id_funcao,salario_100H_int",[id_municipio,anomes])
    elif posgraduacao and tupla_profs_com_pos:
        cursor.execute("Select fu.id_funcao,CAST(salario_100H AS DECIMAL(0)) as salario_100H_int,carga_horaria,fm.suporte, \
        case when fm.vinculo in ('T','C') then 'T' \
        else 'E' end as vinculo, \
        MIN(salario_100H) AS salario_100H,sum(participacao) as somaParticipacao,sum(vencimento_base) as somaVencimento \
        from folhames fm,funcoes fu where fm.id_municipio=%s and anomes=%s \
        and fm.fundeb='S' and fm.vinculo in ('E','T','C') \
        and fm.cod_servidor in %s \
        and fu.id_funcao=fm.id_funcao and fu.id_municipio=fm.id_municipio\
        and salario>0 group by fu.id_funcao,salario_100H_int,carga_horaria,fm.suporte,fm.vinculo order by fm.id_funcao,salario_100H_int",[id_municipio,anomes,tupla_profs_com_pos])

    query = dictfetchall(cursor)        
    return query


def fun_lista_impressao_a(qLista,qListaPos,tupla_servidores_pos,tupla_ampliacaoch,id_municipio,anomes):
    #print (tupla_servidores_pos)
    #print (tupla_ampliacaoch)

    if tupla_servidores_pos and tupla_ampliacaoch:
        dictAmpliacaoCh_com_pos=fun_dictAmpliacaoCh(id_municipio,anomes,tupla_servidores_pos,tupla_ampliacaoch,True)
    else:
        dictAmpliacaoCh_com_pos=[]

    if not tupla_servidores_pos:
        tupla_servidores_pos=(0,0)

    if tupla_ampliacaoch:
        dictAmpliacaoCh_sem_pos=fun_dictAmpliacaoCh(id_municipio,anomes,tupla_servidores_pos,tupla_ampliacaoch,False)
    else:        
        dictAmpliacaoCh_sem_pos=[]

    lista_impressao_a=[]
    lista_controle=[]
    somaGeral=0
    lista_regente_efetivo=[]
    lista_regente_temporario=[]
    lista_suporte_efetivo=[]
    lista_suporte_temporario=[]
    dictFuncoes=listagens.criarDictIdFuncoes(id_municipio)
    lista_funcao_prof=[ev.id_funcao for ev in Funcao.objects.filter(id_municipio=id_municipio,professor='S')]


    listao=[]
    for k in range(2):
        if k==0:
            lista_q=qLista
            posgraduacao=False
            dictAmpliacao=dictAmpliacaoCh_sem_pos
        else:
            lista_q=qListaPos
            posgraduacao=True            
            dictAmpliacao=dictAmpliacaoCh_com_pos
        for qy in lista_q:
            #if [qy['id_funcao'],qy['salario_100H_int'],qy['suporte'],qy['vinculo']] not in lista_controle:
            if [qy['id_funcao'],qy['salario_100H_int']] not in lista_controle:
                lista_controle.append([qy['id_funcao'],qy['salario_100H_int']])
                funcao=dictFuncoes.get(qy['id_funcao'],'')
                if qy['id_funcao'] in lista_funcao_prof:
                    tipo_funcao=21
                else:
                    tipo_funcao=11
                lista=coletaDados(tipo_funcao,funcao,qy['id_funcao'],qy['salario_100H_int'],qy['suporte'],qy['vinculo'],qy['salario_100H'],lista_q,dictAmpliacao,posgraduacao)
                listao.append(lista)

    return listao

def coletaDados(tipo_funcao,funcao,id_funcao,salario_100H_int,suporte,vinculo,salario_100H,queryLista,dictAmpliacao,posgraduacao):
    soma100=Decimal(0)
    soma200=Decimal(0)
    q100=Decimal(0)
    q200=Decimal(0)
    listao=[]
    ampliacao=Decimal(0)
    salario100=Decimal(0)

    ch_reg_ef100=Decimal(0)
    ch_reg_ef200=Decimal(0)
    ch_reg_te100=Decimal(0)
    ch_reg_te200=Decimal(0)

    ch_sup_ef100=Decimal(0)
    ch_sup_ef200=Decimal(0)
    ch_sup_te100=Decimal(0)
    ch_sup_te200=Decimal(0)

    amp_reg_ef=Decimal(0)
    amp_reg_te=Decimal(0)
    amp_sup_ef=Decimal(0)
    amp_sup_te=Decimal(0)

    for qq in queryLista:
        #if 1==1:

        if qq['id_funcao']==id_funcao and qq['salario_100H_int']==salario_100H_int:

            if int(qq['carga_horaria'])==100:
                q100=qq['somaParticipacao']
                salario100=qq['salario_100H']
            elif int(qq['carga_horaria'])==200:
                q200=qq['somaParticipacao']
                salario100=qq['salario_100H']
            string=suporte+vinculo+str(qq['id_funcao'])+str(qq['salario_100H_int']) 
            if dictAmpliacao:
                ampliacao=dictAmpliacao.get(string,Decimal(0))

            if qq['suporte']=='N':
                if qq['vinculo']=='E':
                    if int(qq['carga_horaria'])==100:
                        ch_reg_ef100=q100
                        amp_reg_ef=ampliacao
                    else:
                        ch_reg_ef200=q200
                        amp_reg_ef=ampliacao
                else:
                    if int(qq['carga_horaria'])==100:
                        ch_reg_te100=q100
                        amp_reg_te=ampliacao
                    else:
                        ch_reg_te200=q200
                        amp_reg_te=ampliacao
            else:
                if qq['vinculo']=='E':
                    if int(qq['carga_horaria'])==100:
                        ch_sup_ef100=q100
                        amp_sup_ef=ampliacao
                    else:
                        ch_sup_ef200=q200
                        amp_sup_ef=ampliacao
                else:
                    if int(qq['carga_horaria'])==100:
                        ch_sup_te100=q100
                        amp_sup_te=ampliacao
                    else:
                        ch_sup_te200=q200
                        amp_sup_te=ampliacao

    qSoma1=q100+q200+ampliacao
    qSoma2=q100+q200*2+ampliacao
    if not posgraduacao:
        descfuncao=funcao+' ('+str(id_funcao)+')'
    else:
        descfuncao=funcao+' POS ('+str(id_funcao)+')'
    listao.append(tipo_funcao)
    listao.append(descfuncao)
    listao.append(salario_100H_int)
    listao.append(salario100)    
    listao.append(ch_reg_ef100)
    listao.append(ch_reg_ef200)
    listao.append(amp_reg_ef)
    listao.append(ch_reg_te100)
    listao.append(ch_reg_te200)
    listao.append(amp_reg_te)
    listao.append(ch_sup_ef100)
    listao.append(ch_sup_ef200)
    listao.append(amp_sup_ef)
    listao.append(ch_sup_te100)
    listao.append(ch_sup_te200)
    listao.append(amp_sup_te)
    return listao


def fun_dictAmpliacaoCh(id_municipio,anomes,tupla_servidores_com_pos,tupla_eventos_ampliacao,posgraduacao):
    cursor = connection.cursor()    
    if not posgraduacao:
        cursor.execute("select fm.suporte, \
        case when fm.vinculo in ('T','C') then 'T' \
        else 'E' end as vinculo, \
        fm.id_funcao,CAST(fm.salario_100H AS DECIMAL(0)) as salario_100H_int,sum(fe.valor/fm.salario_100H) as participacao \
        from folhaeventos fe,folhames fm \
        where fe.cod_servidor=fm.cod_servidor and fe.id_municipio=fm.id_municipio and fe.anomes=fm.anomes \
        and fe.id_municipio=%s and fe.anomes=%s \
        and fm.ampliacao_ch='S' \
        and fm.vinculo in ('E','T','C') \
        and fm.cod_servidor not in %s \
        and fe.id_evento in %s \
        and fm.salario_100H IS NOT NULL \
        group by fm.suporte,fm.vinculo,fm.id_funcao,CAST(fm.salario_100H AS DECIMAL(0)) order by fm.suporte",[id_municipio,anomes,tupla_servidores_com_pos,tupla_eventos_ampliacao])
    else:
        cursor.execute("select fm.suporte, \
        case when fm.vinculo in ('T','C') then 'T' \
        else 'E' end as vinculo, \
        fm.id_funcao,CAST(fm.salario_100H AS DECIMAL(0)) as salario_100H_int,sum(fe.valor/fm.salario_100H) as participacao \
        from folhaeventos fe,folhames fm \
        where fe.cod_servidor=fm.cod_servidor and fe.id_municipio=fm.id_municipio and fe.anomes=fm.anomes \
        and fe.id_municipio=%s and fe.anomes=%s \
        and fm.ampliacao_ch='S' and fm.vinculo in ('E','T','C') \
        and fm.cod_servidor in %s \
        and fe.id_evento in %s and fm.salario_100H IS NOT NULL \
        group by fm.suporte,fm.vinculo,fm.id_funcao,CAST(fm.salario_100H AS DECIMAL(0)) order by fm.id_funcao",[id_municipio,anomes,tupla_servidores_com_pos,tupla_eventos_ampliacao])
    query = dictfetchall(cursor)        

    lisSalario=[]
    lisParticipacao=[]
    for qp in query:
        chave = qp['suporte']+qp['vinculo']+str(qp['id_funcao'])+str(qp['salario_100H_int'])
        valor = round(qp['participacao'],4)
        lisSalario.append(chave)
        lisParticipacao.append(valor)
    return dict(zip(lisSalario,lisParticipacao))


def teste(request):
    id_municipio=38
    anomes=202209
    lista_Regente_Suporte(id_municipio,anomes)
    return  HttpResponse("<h1>Encerrado</h1>")

def tabelaRegenteSuporte(id_municipio,anomes,tabela):
    if 1==1:
        mesEano=str(anomes)[-2:]+'/'+str(anomes)[0:4]
        obj=Municipio.objects.get(id_municipio=id_municipio)
        municipio=obj.municipio
        tabela=tabela.upper()
        (listao) = lista_Regente_Suporte(id_municipio,anomes,tabela)
        listao.sort()
        (lista_somaE,lista_somaT) = lista_Soma_Eventos(id_municipio,anomes,tabela)
        for k in lista_somaE:
            print (k)
        if tabela=='REGENTE':
            label_arquivo='tabelaRegente-'+municipio+'.csv'
            titulo_relatorio='Regentes - Efetivos E Temporarios'
            primeira_parte=['Regentes Efetivo','Regentes Temporario']
            titulo_resumo=['Resumo do Eventos - Regentes Efetivos','Resumo do Eventos - Regentes Temporarios']
            total_soma_evento=['Total Regente Efetivo','Total Regente Contratado']
        else:
            label_arquivo='tabelaSuporte-'+municipio+'.csv'
            titulo_relatorio='Suporte - Efetivos E Temporarios'
            primeira_parte=['Suportes Efetivo','Suportes Temporario']
            titulo_resumo=['Resumo do Eventos - Suportes Efetivos','Resumo do Eventos - Suportes Temporarios']
            total_soma_evento=['Total Suporte Efetivo','Total Suporte Contratado']

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename='+label_arquivo

        #cabecalho = ['Nivel (Função)','100H','200H','Ampl.C.Hora','TOTAL','TOTAL 100H','Vencto','Sal.Base']
        cabecalho1=[titulo_relatorio]
        cabecalho2=[municipio+ '- '+mesEano]
        cabecalho3=['Função ','100-Horas','200-Horas','Ampliacao','Total','Total 100Horas','Vencimento','Sal. Base']
        writer = csv.writer(response, delimiter=';')
        response.write(u'\ufeff'.encode('utf8'))
        hlinha=0
        writer.writerow(cabecalho1)
        writer.writerow(cabecalho2)

        nlinha_inicio=3
        nlinha_termino=2


        s1=Decimal(0)
        s2=Decimal(0)
        s3=Decimal(0)
        s4=Decimal(0)
        s5=Decimal(0)
        s6=Decimal(0)

        v100=Decimal(0)
        v200=Decimal(0)
        vAmpliacao=Decimal(0)
        vVencimentoBase=Decimal(0)

        f1=Decimal(0)
        f2=Decimal(0)
        f3=Decimal(0)

        nlinha=5
        for kl in range(2):
            if kl==0:
                lista_impressao2=lista_somaE
                soma_eventos=Decimal(0)
            else:
                lista_impressao2=lista_somaT

            writer.writerow([primeira_parte[kl]])
            writer.writerow(cabecalho3)
            writer.writerow([''])
            if kl==0:
                nlinha_termino=5
                nlinha_inicio=6

            for k in listao:
                hlinha+=1
                funcao=k[1]
                vVencimentoBase=k[3]
                if tabela=='REGENTE':
                    if kl==0:
                        if k[4]+k[5]+k[6]==0:
                            continue
                        v100=k[4]
                        v200=k[5]
                        vAmpliacao=k[6]
                    else:
                        if k[7]+k[8]+k[9]==0:
                            continue
                        v100=k[7]
                        v200=k[8]
                        vAmpliacao=k[9]
                elif tabela=='SUPORTE':
                    if kl==0:
                        if k[10]+k[11]+k[12]==0:
                            continue
                        v100=k[10]
                        v200=k[11]
                        vAmpliacao=k[12]
                    else:
                        if k[13]+k[14]+k[15]==0:
                            continue
                        v100=k[13]
                        v200=k[14]
                        vAmpliacao=k[15]

                f1=v100+v200+vAmpliacao
                f2=v100+v200*2+vAmpliacao
                f3=(v100+v200*2+vAmpliacao)*vVencimentoBase

                s1+=v100
                s2+=v200
                s3+=vAmpliacao
                s4+=f1
                s5+=f2
                s6+=f3
                writer.writerow([funcao,funcoes.formatMilhar(v100),funcoes.formatMilhar(v200),funcoes.formatMilhar(vAmpliacao),funcoes.formatMilhar(f1),funcoes.formatMilhar(f2),funcoes.formatMilhar(vVencimentoBase),funcoes.formatMilhar(f3)])
                nlinha_termino+=1
            form1="=SOMA(B"+str(nlinha_inicio)+":B"+str(nlinha_termino)+")"
            form2="=SOMA(C"+str(nlinha_inicio)+":C"+str(nlinha_termino)+")"
            form3="=SOMA(D"+str(nlinha_inicio)+":D"+str(nlinha_termino)+")"
            form4="=SOMA(E"+str(nlinha_inicio)+":E"+str(nlinha_termino)+")"
            form5="=SOMA(F"+str(nlinha_inicio)+":F"+str(nlinha_termino)+")"
            form6="=SOMA(H"+str(nlinha_inicio)+":H"+str(nlinha_termino)+")"

            writer.writerow(['',form1,form2,form3,form4,form5,'',form6])   

            nlinha_inicio=nlinha_termino+6


            writer.writerow([''])

            writer.writerow([titulo_resumo[kl]])
            
            writer.writerow(['Evento','Soma'])

            s3=Decimal(0)
            tev1=''
            nlinha_termino+=5

            for k in lista_impressao2:
                if k[1]=='carater-salario':
                    tipo_evento=' (Caráter Salário)'
                elif k[1]=='posgraduacao':
                    tipo_evento=' (Pós)'
                elif k[1]=='suporte':
                    tipo_evento=' (Suporte)'
                else:
                    tipo_evento=''

                if tev1!=k[0]:
                    writer.writerow([''])
                    if tev1!='':
                        nlinha_termino+=1
                    tev1=k[0]

                writer.writerow([k[2]+tipo_evento,funcoes.formatMilhar(k[3])])
                nlinha_termino+=1

            #writer.writerow(['nlinha_termino',nlinha_inicio,nlinha_termino])                
            if kl==0 or kl==1:
                form6="=SOMA(B"+str(nlinha_inicio)+":B"+str(nlinha_termino)+")"                
                writer.writerow(['Sub Total',form6])
                nlinha_termino+=1
                nlinha_inicio=nlinha_termino

                writer.writerow(['Encargos',''])
                nlinha_termino+=1
                form1="=SOMA(B"+str(nlinha_inicio)+":B"+str(nlinha_termino)+")"                
                writer.writerow([total_soma_evento[kl],form1])
                #writer.writerow(['nlinha_termino',nlinha_inicio,nlinha_termino])                

            writer.writerow([''])
            writer.writerow([''])
            nlinha_inicio=nlinha_termino+7
            nlinha_termino+=6
            


        return response            



def somaEventos(lista):
    adicional_refe=Decimal(0)
    adicional_rtemp=Decimal(0)
    adicional_sefe=Decimal(0)
    adicional_stemp=Decimal(0)
    suporte_refe=Decimal(0)
    suporte_rtemp=Decimal(0)
    suporte_sefe=Decimal(0)
    suporte_stemp=Decimal(0)
    salario_base_refe=Decimal(0)
    salario_base_rtemp=Decimal(0)
    salario_base_sefe=Decimal(0)
    salario_base_stemp=Decimal(0)
    lista=[]


    for k in lista:
        if suporte=='N':
            if vinculo=='E':
                if k[0] in ['adicional']:
                    adicional_refe+=k[2]
                elif k[0] in ['suporte']:
                    suporte_refe=k[2]
                elif k[0] in ['salario-base']:
                    salario_base_refe=k[2]
            else:
                if k[0] in ['adicional']:
                    adicional_rtemp+=k[2]
                elif k[0] in ['suporte']:
                    suporte_rtemp=k[2]
                elif k[0] in ['salario-base']:
                    salario_base_rtemp=k[2]
        else:
            if vinculo=='E':
                if k[0] in ['adicional']:
                    adicional_sefe+=k[2]
                elif k[0] in ['suporte']:
                    suporte_sefe=k[2]
                elif k[0] in ['salario-base']:
                    salario_base_sefe=k[2]
            else:
                if k[0] in ['adicional']:
                    adicional_stemp+=k[2]
                elif k[0] in ['suporte']:
                    suporte_stemp=k[2]
                elif k[0] in ['salario-base']:
                    salario_base_stemp=k[2]

    if adicional_refe+adicional_rtemp+adicional_sefe+adicional_stemp>0:
        t1=''
        t2=''
        if adicional_refe+adicional_rtemp>0:
            t1='Adicional'
        if adicional_sefe+adicional_stemp>0:
            t2='Adicional'
        lista.append(8,t1,adicional_refe,adicional_rtemp,adicional_refe+adicional_rtemp,t2,adicional_sefe,adicional_stemp,adicional_sefe+adicional_stemp)

    if suporte_refe+suporte_rtemp+suporte_sefe+suporte_stemp>0:
        t1=''
        t2=''
        if suporte_refe+suporte_rtemp>0:
            t1='Suporte'
        if suporte_sefe+suporte_stemp>0:
            t2='Suporte'
        lista.append(4,t1,suporte_refe,suporte_rtemp,suporte_refe+suporte_rtemp,t2,suporte_sefe,suporte_stemp,suporte_sefe+suporte_stemp)

    if salario_base_refe+salario_base_rtemp+salario_base_sefe+salario_base_stemp>0:
        t1=''
        t2=''
        if salario_base_refe+salario_base_rtemp>0:
            t1='Sal. Base'
        if salario_base_sefe+salario_base_stemp>0:
            t2='Sal. Base'
        lista.append(1,t1,salario_base_refe,salario_base_rtemp,salario_base_refe+salario_base_rtemp,t2,salario_base_sefe,salario_base_stemp,salario_base_sefe+salario_base_stemp)
    return lista



def lista_SomaEventos(id_municipio,anomes):
    query = fun_nova_listaEventos(id_municipio,anomes)
    lista=[]
    listao=[]
    lsregefet=[]
    lsregefet_valor=[]

    lsregtemp=[]
    lsregtemp_valor=[]

    lssupefet=[]
    lssupefet_valor=[]

    lssuptemp=[]
    lssuptemp_valor=[]
    lista_vencimento_base=[k.id_evento for k in Evento.objects.filter(id_municipio=id_municipio,evento='VENCIMENTO BASE')]
    lista_carater_salario=[k.id_evento for k in Evento.objects.filter(id_municipio=id_municipio,carater_salario='S')]
    lista_suporte=[k.id_evento for k in Evento.objects.filter(id_municipio=id_municipio,suporte='S')]
    tipo=''
    ordenacao=0
    lista_soma=[]
    for ky in query:
        tipo='adcional'
        ordenacao=9
        if ky['id_evento'] not in lista:

            lista.append(ky['id_evento'])
        if ky['suporte']=='N':
            if ky['vinculo']=='E':
                lsregefet.append(ky['id_evento'])
                lsregefet_valor.append(ky['soma'])
            else:
                lsregtemp.append(ky['id_evento'])
                lsregtemp_valor.append(ky['soma'])
        else:
            if ky['vinculo']=='E':
                lssupefet.append(ky['id_evento'])
                lssupefet_valor.append(ky['soma'])
            else:
                lssuptemp.append(ky['id_evento'])
                lssuptemp_valor.append(ky['soma'])


    dicRegEfet=dict(zip(lsregefet,lsregefet_valor))
    dicRegTemp=dict(zip(lsregtemp,lsregtemp_valor))
    dicSupEfet=dict(zip(lssupefet,lssupefet_valor))
    dicSupTemp=dict(zip(lssuptemp,lssuptemp_valor))
    dicEventos=listagens.criarDictEventos(id_municipio)


    for kv in lista:
        if kv in lista_vencimento_base:
            tipo='salario-base'
            ordenacao=1
        elif kv in lista_carater_salario:
            tipo='carater-salario'
            ordenacao=4
        elif kv in lista_suporte:
            tipo='suporte'
            ordenacao=7
        else:
            tipo='adicional'
            ordenacao=9
        descEvento=dicEventos.get(kv,'')

        e1=Decimal(dicRegEfet.get(kv,0))
        e2=Decimal(dicRegTemp.get(kv,0))
        e3=Decimal(dicSupEfet.get(kv,0))
        e4=Decimal(dicSupTemp.get(kv,0))
        listao.append([ordenacao,tipo,descEvento,kv,e1,e2,e3,e4])

    sb1=Decimal(0)
    sb2=Decimal(0)
    sb3=Decimal(0)
    sb4=Decimal(0)
    cs1=Decimal(0)
    cs2=Decimal(0)
    cs3=Decimal(0)
    cs4=Decimal(0)
    sp1=Decimal(0)
    sp2=Decimal(0)
    sp3=Decimal(0)
    sp4=Decimal(0)
    ad1=Decimal(0)
    ad2=Decimal(0)
    ad3=Decimal(0)
    ad4=Decimal(0)


    for k in listao:
        if k[1]=='salario-base':
            sb1+=k[4]
            sb2+=k[5]
            sb3+=k[6]
            sb4+=k[7]
        elif k[1]=='carater-salario':
            cs1+=k[4]
            cs2+=k[5]
            cs3+=k[6]
            cs4+=k[7]
        elif k[1]=='suporte':
            sp1+=k[4]
            sp2+=k[5]
            sp3+=k[6]
            sp4+=k[7]
        elif k[1]=='adicional':
            ad1+=k[4]
            ad2+=k[5]
            ad3+=k[6]
            ad4+=k[7]

    tsbr=Decimal(sb1+sb2)
    tsbs=Decimal(sb3+sb4)

    tcsr=Decimal(cs1+cs2)
    tcss=Decimal(cs3+cs4)

    tspr=Decimal(sp1+sp2)
    tsps=Decimal(sp3+sp4)

    tadr=Decimal(ad1+ad2)
    tads=Decimal(ad3+ad4)

    tot1=sb1+cs1+sp1+ad1
    tot2=sb2+cs2+sp2+ad2
    tot3=tsbr+tcsr+tspr+tadr
    tot4=sb3+cs3+sp3+ad3
    tot5=sb4+cs4+sp4+ad4
    tot6=tsbs+tcss+tsps+tads

    lista_soma.append([1,'Salario Base',sb1,sb2,tsbr,sb3,sb4,tsbs])
    lista_soma.append([2,'Carater Salario',cs1,cs2,tcsr,cs3,cs4,tcss])
    lista_soma.append([3,'Suporte',sp1,sp2,tspr,sp3,sp4,tsps])
    lista_soma.append([4,'Adicional',ad1,ad2,tadr,ad3,ad4,tads])
    lista_soma.append([9,'Soma',tot1,tot2,tot3,tot4,tot5,tot6])

    return [listao,lista_soma]


def fun_Auxiliar_tabelaMatriz(lista):
    v1=lista[4]+lista[5]*2+lista[6]+lista[10]+lista[11]*2+lista[12]
    v2=lista[7]+lista[8]*2+lista[9]+lista[13]+lista[14]*2+lista[15]
    c1=v1*lista[3]
    c2=v2*lista[3]

    return [v1,c1,v2,c2]








