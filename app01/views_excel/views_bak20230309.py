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
        anomes=str(ano)+str(int(mes)+100)[-2:]
        if tabela=='MATRIZ':
            return tabelaMatriz(id_municipio,int(anomes),tabela)
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
        (ls_efetivo_reg,ls_efetivo_sup,ls_temporario_reg,ls_temporario_sup) = lista_Regente_Suporte(id_municipio,anomes,tabela)
        (ls_somaEfetivo_reg,ls_somaEfetivo_sup,ls_somaTemporario_reg,ls_somaTemporario_sup) = lista_Soma_Eventos(id_municipio,anomes,tabela)

        (soma_carater_salario_reg_efetivo,soma_adicional_reg_efetivo,soma_suporte_reg_efetivo) =  somaEventos(ls_somaEfetivo_reg,'regente_efetivo')
        (soma_carater_salario_reg_temporario,soma_adicional_reg_temporario,soma_suporte_reg_temporario) =  somaEventos(ls_somaTemporario_reg,'regente_temporario')

        (soma_carater_salario_sup_efetivo,soma_adicional_sup_efetivo,soma_suporte_sup_efetivo) =  somaEventos(ls_somaEfetivo_sup,'suporte_efetivo')
        (soma_carater_salario_sup_temporario,soma_adicional_sup_temporario,soma_suporte_sup_temporario) =  somaEventos(ls_somaTemporario_sup,'suporte_temporario')



        if tabela=='MATRIZ':
            label_arquivo='tabelaMatriz-'+municipio+'.csv'
            titulo_relatorio='Tabela Matriz'
            primeira_parte=['Regentes Efetivo','Suporte Efetivo']
            segunda_parte=['Regentes Temporário','Suporte Temporário']
            titulo_resumo=['Resumo do Eventos - Regentes Efetivos','Resumo do Eventos - Regentes Temporarios']

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename='+label_arquivo

        #cabecalho = ['Nivel (Função)','100H','200H','Ampl.C.Hora','TOTAL','TOTAL 100H','Vencto','Sal.Base']
        cabecalho1=[titulo_relatorio]
        cabecalho2=[municipio+ '- '+mesEano]

        cabecalho3=['Função ','Total 100h','Vencimento Base','','','','Total 100h','Vencimento Base']
        writer = csv.writer(response, delimiter=';')
        response.write(u'\ufeff'.encode('utf8'))
        hlinha=0
        writer.writerow(cabecalho1)
        writer.writerow(cabecalho2)

        for kl in range(2):
            s1=Decimal(0)
            s2=Decimal(0)
            if kl==0:
                ls_impressao1=ls_efetivo_reg
                ls_impressao2=ls_efetivo_sup
                titulo_regente=primeira_parte[0]
                titulo_suporte=primeira_parte[1]
            else:
                ls_impressao1=ls_temporario_reg
                ls_impressao2=ls_temporario_sup
                titulo_regente=segunda_parte[0]
                titulo_suporte=segunda_parte[1]

            writer.writerow([titulo_regente,'','','','','',titulo_suporte])
            writer.writerow(cabecalho3)
            writer.writerow([''])

            for kreg in range(len(ls_impressao1)):
                hlinha+=1
                s1+=ls_impressao1[kreg][7]
                s2+=ls_impressao2[kreg][7]

                k7=funcoes.formatMilhar(ls_impressao1[kreg][7])
                k8=funcoes.formatMilhar(ls_impressao1[kreg][8])

                w7=funcoes.formatMilhar(ls_impressao2[kreg][7])
                w8=funcoes.formatMilhar(ls_impressao2[kreg][8])

                writer.writerow([ls_impressao1[kreg][1],k7,k8,'','','',w7,w8])

            writer.writerow(['Soma',funcoes.formatMilhar(s1),'','','','Soma',funcoes.formatMilhar(s2),''])

            writer.writerow([''])
            writer.writerow([''])

        s3=Decimal(0)
        s4=Decimal(0)

        s1=soma_carater_salario_reg_temporario
        s2=soma_carater_salario_reg_efetivo
        s3=soma_adicional_reg_temporario
        s4=soma_adicional_reg_efetivo
        s5=soma_suporte_reg_temporario
        s6=soma_suporte_reg_efetivo



        writer.writerow(['Regentes'])
        writer.writerow(['','Temporario','Efetivo','Total'])
        writer.writerow(['S. Base',funcoes.formatMilhar(s1),funcoes.formatMilhar(s2),funcoes.formatMilhar(s1+s2)])
        writer.writerow(['Suporte',funcoes.formatMilhar(s5),funcoes.formatMilhar(s6),funcoes.formatMilhar(s5+s6)])
        writer.writerow(['Adicionais',funcoes.formatMilhar(s3),funcoes.formatMilhar(s4),funcoes.formatMilhar(s3+s4)])
        writer.writerow(['Encargos','','',''])
        writer.writerow(['Total',funcoes.formatMilhar(s1+s3+s5),funcoes.formatMilhar(s2+s4+s6),funcoes.formatMilhar(s1+s2+s3+s4+s4+s6)])

        s1=soma_carater_salario_sup_temporario
        s2=soma_carater_salario_sup_efetivo
        s3=soma_adicional_sup_temporario
        s4=soma_adicional_sup_efetivo
        s5=soma_suporte_sup_temporario
        s6=soma_suporte_sup_efetivo


        writer.writerow([''])
        writer.writerow([''])
        writer.writerow([''])
        writer.writerow(['Suportes'])
        writer.writerow(['','Temporario','Efetivo','Total'])
        writer.writerow(['S. Base',funcoes.formatMilhar(s1),funcoes.formatMilhar(s2),funcoes.formatMilhar(s1+s2)])
        writer.writerow(['Suporte',funcoes.formatMilhar(s5),funcoes.formatMilhar(s6),funcoes.formatMilhar(s5+s6)])
        writer.writerow(['Adicionais',funcoes.formatMilhar(s3),funcoes.formatMilhar(s4),funcoes.formatMilhar(s3+s4)])
        writer.writerow(['Encargos','','',''])
        writer.writerow(['Total',funcoes.formatMilhar(s1+s3+s5),funcoes.formatMilhar(s2+s4+s6),funcoes.formatMilhar(s1+s2+s3+s4+s5+s6)])

        writer.writerow([''])
        writer.writerow([''])
        writer.writerow([''])


        return response

    else:
        return render(request, 'app01/tabelaRegenteSuporte.html',
            {
                'titulo': 'Tabela Regente/Suporte/Matriz',
                'municipios':municipios,
            }
        )


def fun_dict_ampliacaoch(id_municipio,anomes,suporte,tp_vinculo_efetivo,tp_evento_ampliacao_ch,posgraduacao):
    cursor = connection.cursor()

    if posgraduacao=='':
        cursor.execute("select fm.id_funcao,CAST(salario_100H AS DECIMAL(0)) as salario_100H_int,sum(valor/salario_100H) as participacao \
        from folhaeventos fe,folhames fm \
        where fe.cod_servidor=fm.cod_servidor and fe.id_municipio=fm.id_municipio \
        and fe.id_municipio=%s and fe.anomes=fm.anomes and fm.anomes=%s \
        and fm.ampliacao_ch='S' and fm.suporte=%s and fm.id_vinculo in %s \
        and not exists (select * from folhaeventos fe2,eventos ev where ev.id_evento=fe2.id_evento and ev.posgraduacao='N' and fe2.id_municipio=fe.id_municipio and fe2.anomes=fe.anomes and fe2.cod_servidor=fe.cod_servidor) \
        and fe.id_evento in %s and salario_100H IS NOT NULL group by fm.id_funcao,CAST(salario_100H AS DECIMAL(0)) order by id_funcao",[id_municipio,anomes,suporte,tp_vinculo_efetivo,tp_evento_ampliacao_ch])
    else:
        cursor.execute("select fm.id_funcao,CAST(salario_100H AS DECIMAL(0)) as salario_100H_int,sum(valor/salario_100H) as participacao \
        from folhaeventos fe,folhames fm \
        where fe.cod_servidor=fm.cod_servidor and fe.id_municipio=fm.id_municipio \
        and fe.id_municipio=%s and fe.anomes=fm.anomes and fm.anomes=%s \
        and fm.ampliacao_ch='S' and fm.suporte=%s and fm.id_vinculo in %s \
        and exists (select * from folhaeventos fe2,eventos ev where ev.id_evento=fe2.id_evento and ev.posgraduacao='N' and fe2.id_municipio=fe.id_municipio and fe2.anomes=fe.anomes and fe2.cod_servidor=fe.cod_servidor) \
        and fe.id_evento in %s and salario_100H IS NOT NULL group by fm.id_funcao,CAST(salario_100H AS DECIMAL(0)) order by id_funcao",[id_municipio,anomes,suporte,tp_vinculo_efetivo,tp_evento_ampliacao_ch])

    query = dictfetchall(cursor)

    lisSalario=[]
    lisParticipacao=[]
    for qp in query:
        qp_funcao = str(qp['id_funcao'])
        qp_salario = str(qp['salario_100H_int'])
        qp_participacao = round(qp['participacao'],4)
        lisSalario.append(qp_funcao+'-'+qp_salario)
        lisParticipacao.append(qp_participacao)
    return dict(zip(lisSalario,lisParticipacao))


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
    lista_eventos_carater_salario=[ev.id_evento for ev in Evento.objects.filter(id_municipio=id_municipio,carater_salario='S')]
    lista_eventos_pos=[ev.id_evento for ev in Evento.objects.filter(id_municipio=id_municipio,posgraduacao='S')]
    lista_eventos_suporte=[ev.id_evento for ev in Evento.objects.filter(id_municipio=id_municipio,suporte='S')]

    lista_soma=fun_nova_listaEventos(id_municipio,anomes) 
    for k in lista_soma:
        tipo_evento='z-adicional'
        id_evento=k['id_evento']
        desc_evento=dicionario.get(id_evento,'')
        soma=k['soma']
        if id_evento in lista_eventos_carater_salario:
            tipo_evento='carater_salario'
        elif id_evento in lista_eventos_pos:
            tipo_evento='posgraduacao'
        elif id_evento in lista_eventos_suporte:
            tipo_evento='suporte'

        if k['suporte']=='S':
            if k['vinculo']=='E':
                lista_suporte_efetivo.append([tipo_evento,desc_evento,soma])
            else:
                lista_suporte_temporario.append([tipo_evento,desc_evento,soma])
        else:
            if k['vinculo']=='E':
                lista_regente_efetivo.append([tipo_evento,desc_evento,soma])
            else:
                lista_regente_temporario.append([tipo_evento,desc_evento,soma])
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
        [lista_regente_efetivo,lista_regente_temporario,lista_suporte_efetivo,lista_suporte_temporario]=fun_lista_impressao_a(qFolha_sem_pos,qFolha_com_pos,tupla_servidores_com_pos,tupla_eventos_ampliacao,id_municipio,anomes)

        ''' 
        print (f'lista_regente_efetivo: {len(lista_regente_efetivo)}')
        print (f'lista_regente_temporario: {len(lista_regente_temporario)}')
        print (f'lista_suporte_efetivo: {len(lista_suporte_efetivo)}')
        print (f'lista_suporte_temporario: {len(lista_suporte_temporario)}')
        '''
        lista_reg=[]
        lista_sup=[]
        v_zero=Decimal(0)

        for k in lista_regente_efetivo:
            lista_reg.append([k[0],k[1],k[2],k[8]])
        for k in lista_suporte_efetivo:
            lista_sup.append([k[0],k[1],k[2],k[8]])


        for k1 in lista_reg:
            inclui=True
            for k2 in lista_sup:
                if k2==k1:
                    inclui=False
                    break
            if inclui:
                lista_suporte_efetivo.append([k1[0],k1[1],k1[2],v_zero,v_zero,v_zero,v_zero,v_zero,k1[3]])

        for k1 in lista_sup:
            inclui=True
            for k2 in lista_reg:
                if k2==k1:
                    inclui=False
                    break
            if inclui:
                lista_regente_efetivo.append([k1[0],k1[1],k1[2],v_zero,v_zero,v_zero,v_zero,v_zero,k1[3]])

        lista_reg=[]
        lista_sup=[]
        for k in lista_regente_temporario:
            lista_reg.append([k[0],k[1],k[2],k[8]])
        for k in lista_suporte_temporario:
            lista_sup.append([k[0],k[1],k[2],k[8]])

        for k1 in lista_reg:
            inclui=True
            for k2 in lista_sup:
                if k2==k1:
                    inclui=False
                    break
            if inclui:
                lista_suporte_temporario.append([k1[0],k1[1],k1[2],v_zero,v_zero,v_zero,v_zero,v_zero,k1[3]])

        for k1 in lista_sup:
            inclui=True
            for k2 in lista_reg:
                if k2==k1:
                    inclui=False
                    break
            if inclui:
                lista_regente_temporario.append([k1[0],k1[1],k1[2],v_zero,v_zero,v_zero,v_zero,v_zero,k1[3]])

        lista_regente_efetivo.sort()
        lista_regente_temporario.sort()
        lista_suporte_temporario.sort()
        lista_suporte_efetivo.sort()

        if tabela=='REGENTE':
            return [lista_regente_efetivo,lista_regente_temporario]
        elif tabela=='SUPORTE':
            return [lista_suporte_efetivo,lista_suporte_temporario]
        else:
            return [lista_regente_efetivo,lista_suporte_efetivo,lista_regente_temporario,lista_suporte_temporario]

def fun_lista_servidores_com_pos(id_municipio,anomes,lista_eventos_posgraduacao):
    lista=[]
    cursor = connection.cursor()
    cursor.execute("select distinct fe.cod_servidor from folhaeventos fe \
    where fe.id_municipio=%s and fe.anomes=%s and fe.id_evento in %s",[id_municipio,anomes,lista_eventos_posgraduacao]) 
    query = dictfetchall(cursor)
    for kl in query:
        lista.append(kl['cod_servidor'])
    return lista


def fun_lista_participacao(id_municipio,anomes,tupla_profs_com_pos,posgraduacao):
    cursor = connection.cursor()
    if not posgraduacao and tupla_profs_com_pos:
        cursor.execute("Select fm.suporte,fu.id_funcao,professor, \
        case when fm.vinculo in ('T','C') then 'T' \
        else 'E' end as vinculo,\
        carga_horaria,CAST(salario_100H AS DECIMAL(0)) as salario_100H_int,MIN(salario_100H) AS salario_100H,sum(participacao) as somaParticipacao,sum(vencimento_base) as somaVencimento\
        from folhames fm,funcoes fu where fm.id_municipio=%s and anomes=%s \
        and fm.fundeb='S'\
        and fu.id_funcao=fm.id_funcao and fu.id_municipio=fm.id_municipio\
        and fm.cod_servidor not in %s \
        and salario>0 group by fm.suporte,fu.id_funcao,professor,vinculo,carga_horaria,CAST(salario_100H AS DECIMAL(0)) order by fm.suporte",[id_municipio,anomes,tupla_profs_com_pos])
    elif not posgraduacao and not tupla_profs_com_pos:
        cursor.execute("Select fm.suporte,fu.id_funcao,professor, \
        case when fm.vinculo in ('T','C') then 'T' \
        else 'E' end as vinculo,\
        carga_horaria,CAST(salario_100H AS DECIMAL(0)) as salario_100H_int,MIN(salario_100H) AS salario_100H,sum(participacao) as somaParticipacao,sum(vencimento_base) as somaVencimento\
        from folhames fm,funcoes fu where fm.id_municipio=%s and anomes=%s \
        and fm.fundeb='S'\
        and fu.id_funcao=fm.id_funcao and fu.id_municipio=fm.id_municipio\
        and salario>0 group by fm.suporte,fu.id_funcao,professor,vinculo,carga_horaria,CAST(salario_100H AS DECIMAL(0)) order by fm.suporte",[id_municipio,anomes])
    elif posgraduacao and tupla_profs_com_pos:
        cursor.execute("Select fm.suporte,fu.id_funcao,professor, \
        case when fm.vinculo in ('T','C') then 'T' \
        else 'E' end as vinculo,\
        carga_horaria,CAST(salario_100H AS DECIMAL(0)) as salario_100H_int,MIN(salario_100H) AS salario_100H,sum(participacao) as somaParticipacao,sum(vencimento_base) as somaVencimento\
        from folhames fm,funcoes fu where fm.id_municipio=%s and anomes=%s \
        and fm.fundeb='S' \
        and fm.cod_servidor in %s \
        and fu.id_funcao=fm.id_funcao and fu.id_municipio=fm.id_municipio\
        and salario>0 group by fm.suporte,fu.id_funcao,professor,vinculo,carga_horaria,CAST(salario_100H AS DECIMAL(0)) order by fm.suporte",[id_municipio,anomes,tupla_profs_com_pos])

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


    lista=[]
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
            if [qy['id_funcao'],qy['salario_100H_int'],qy['suporte'],qy['vinculo']] not in lista_controle:
                lista_controle.append([qy['id_funcao'],qy['salario_100H_int'],qy['suporte'],qy['vinculo']])
                funcao=dictFuncoes.get(qy['id_funcao'],'')
                if qy['id_funcao'] in lista_funcao_prof:
                    tipo_funcao=21
                else:
                    tipo_funcao=11
                lista=coletaDados(tipo_funcao,funcao,qy['id_funcao'],qy['salario_100H_int'],qy['suporte'],qy['vinculo'],qy['salario_100H'],lista_q,dictAmpliacao,posgraduacao)
                if qy['suporte']=='N':
                    if qy['vinculo']=='E':
                        lista_regente_efetivo.append(lista)
                    else:
                        lista_regente_temporario.append(lista)
                else:
                    if qy['vinculo']=='E':
                        lista_suporte_efetivo.append(lista)
                    else:
                        lista_suporte_temporario.append(lista)

    return [lista_regente_efetivo,lista_regente_temporario,lista_suporte_efetivo,lista_suporte_temporario]

def coletaDados(tipo_funcao,funcao,id_funcao,salario_100H_int,suporte,vinculo,salario_100H,queryLista,dictAmpliacao,posgraduacao):
    soma100=Decimal(0)
    soma200=Decimal(0)
    q100=Decimal(0)
    q200=Decimal(0)
    lista=[]
    ampliacao=Decimal(0)
    salario100=Decimal(0)
    for qq in queryLista:
        #if 1==1:
        if qq['id_funcao']==id_funcao and qq['salario_100H_int']==salario_100H_int and qq['suporte']==suporte and qq['vinculo']==vinculo:
            if suporte=='S':
                tipo1='S'
            else:
                tipo1='R'
            if vinculo=='E':
                tipo2='E'
            else:
                tipo2='T'

            if int(qq['carga_horaria'])==100:
                q100=q100+qq['somaParticipacao']
                salario100=qq['salario_100H']
            elif int(qq['carga_horaria'])==200:
                q200=q200+qq['somaParticipacao']
                salario100=qq['salario_100H']
            string=suporte+vinculo+str(qq['id_funcao'])+str(qq['salario_100H_int']) 
            if dictAmpliacao:
                ampliacao=dictAmpliacao.get(string,Decimal(0))

    qSoma1=q100+q200+ampliacao
    qSoma2=q100+q200*2+ampliacao
    lista.append(tipo_funcao)
    if not posgraduacao:
        lista.append(funcao+' ('+str(id_funcao)+')')
    else:
        lista.append(funcao+' POS ('+str(id_funcao)+')')
    lista.append(salario_100H_int)
    #lista.append(tipo1+tipo2)
    lista.append(q100)
    lista.append(q200)
    lista.append(ampliacao)
    lista.append(qSoma1)
    lista.append(qSoma2)
    lista.append(salario100)

    return lista


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
        case when fm.vinculo in ('T','C') then 'C' \
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
        mesEano=anomes[-2:]+'/'+anomes[0:4]
        obj=Municipio.objects.get(id_municipio=id_municipio)
        municipio=obj.municipio
        tabela=tabela.upper()
        (lista_efetivo,lista_temporario) = lista_Regente_Suporte(id_municipio,anomes,tabela)
        (lista_somaE,lista_somaT) = lista_Soma_Eventos(id_municipio,anomes,tabela)
        if tabela=='REGENTE':
            label_arquivo='tabelaRegente-'+municipio+'.csv'
            titulo_relatorio='Regentes - Efetivos E Temporarios'
            primeira_parte=['Regentes Efetivo','Regentes Temporario']
            titulo_resumo=['Resumo do Eventos - Regentes Efetivos','Resumo do Eventos - Regentes Temporarios']
        else:
            label_arquivo='tabelaSuporte-'+municipio+'.csv'
            titulo_relatorio='Suporte - Efetivos E Temporarios'
            primeira_parte=['Suportes Efetivo','Suportes Temporario']
            titulo_resumo=['Resumo do Eventos - Suportes Efetivos','Resumo do Eventos - Suportes Temporarios']

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

        for kl in range(2):
            if kl==0:
                lista_impressao1=lista_efetivo
                lista_impressao2=lista_somaE
            else:
                lista_impressao1=lista_temporario
                lista_impressao2=lista_somaT

            writer.writerow([primeira_parte[kl]])
            writer.writerow(cabecalho3)
            writer.writerow([''])

            s3=Decimal(0)
            s4=Decimal(0)
            s5=Decimal(0)
            s6=Decimal(0)
            s7=Decimal(0)
            s8=Decimal(0)
            s9=Decimal(0)

            for k in lista_impressao1:
                hlinha+=1
                s3+=k[3]
                s4+=k[4]
                s5+=k[5]
                s6+=k[6]
                s7+=k[7]
                s9+=k[7]*k[8]

                k3=funcoes.formatMilhar(k[3])
                k4=funcoes.formatMilhar(k[4])
                k5=funcoes.formatMilhar(k[5])
                k6=funcoes.formatMilhar(k[6])
                k7=funcoes.formatMilhar(k[7])
                k8=funcoes.formatMilhar(k[8])
                k9=funcoes.formatMilhar(k[7]*k[8])

                writer.writerow([k[1],k3,k4,k5,k6,k7,k8,k9])
            writer.writerow(['',funcoes.formatMilhar(s3),funcoes.formatMilhar(s4),funcoes.formatMilhar(s5),funcoes.formatMilhar(s6),funcoes.formatMilhar(s7),'',funcoes.formatMilhar(s9)])

            writer.writerow([''])
            writer.writerow([''])
            writer.writerow([titulo_resumo[kl]])
            writer.writerow(['Evento','Soma'])

            s3=Decimal(0)
            tev1=''
            for k in lista_impressao2:
                tev2=k[0]
                if k[0]=='carater_salario':
                    tipo_evento=' (Caráter Salário)'
                elif k[0]=='posgraduacao':
                    tipo_evento=' (Pós)'
                elif k[0]=='suporte':
                    tipo_evento=' (Suporte)'
                else:
                    tipo_evento=''
                s3+=k[2]
                if tev1!=k[0]:
                    writer.writerow([''])
                    tev1=k[0]


                writer.writerow([k[1]+tipo_evento,funcoes.formatMilhar(k[2])])
            writer.writerow(['Total',funcoes.formatMilhar(s3)])
            writer.writerow([''])
            writer.writerow([''])

        return response


def somaEventos(lista,tipo):
    soma_carater_salario=Decimal(0)
    soma_adicional=Decimal(0)
    soma_suporte=Decimal(0)
    for k in lista:
        if k[0] in ['carater_salario','posgraduacao']:
            soma_carater_salario+=k[2]
        elif k[0] in ['z-adicional']:
            soma_adicional+=k[2]
        elif k[0] in ['suporte']:
            soma_suporte+=k[2]

    return [soma_carater_salario,soma_adicional,soma_suporte]


