from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseRedirect,Http404
from . import listagens,funcoes
from .. import dicionarios,funcoes as f_funcoes



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
        if tabela=='Matriz':
            return tabelaMatriz(id_municipio,ano,mes,tabela)
        else:
            return tabelaRegenteSuporte2(id_municipio,ano,mes,tabela)
    return render(request, 'app01/tabelaRegenteSuporteMatriz.html',
            {
                'titulo': titulo,
                'municipios':municipios,
            }
        )

def tabelaMatriz(id_municipio,ano,mes,tabela):

    anomes=str(ano)+str(int(mes)+100)[1:]
    tipo_vinculo='T'
    lista_impressao_1=[]
    lista_impressao_2=[]
    obj=Municipio.objects.get(id_municipio=id_municipio)

    response = HttpResponse(content_type='text/csv')
    dict_idXfuncao=dicionarios.dict_idXfuncao(id_municipio)

    label_arquivo=obj.entidade+'_'+str(anomes)+'.csv'
    response['Content-Disposition'] = 'attachment; filename='+label_arquivo

    (lista_regente,lista_suporte,lista_regente_t,lista_suporte_t) = f_funcoes.listas_TabelaMatriz(id_municipio,anomes,dict_idXfuncao)
    lista_somaEventos = f_funcoes.listas_TabelaMatriz_2(id_municipio,anomes)


    cabecalho=['Nivel','Regente 100h','Suporte 100h','Soma', 'Vencimento']
    writer = csv.writer(response, delimiter=';')
    response.write(u'\ufeff'.encode('utf8'))
    lista_impressao_1.append([obj.entidade+' - ' +str(anomes)[-2:]+'/'+str(anomes)[0:4]])
    lista_impressao_1.append([''])
    lista_impressao_1.append(['Efetivos - Regentes e Suporte'])
    lista_impressao_1.append(cabecalho)

    for k in range(len(lista_impressao_1)):
        writer.writerow(lista_impressao_1[k])

    hlinha=5
    lista_impressao_1=[]
    for k in range(len(lista_regente)):
        soma = formatMilhar(float(lista_regente[k][2]) + float(lista_suporte[k][2]))
        lista_regente[k][1]=formatMilhar(float(lista_regente[k][1]))
        lista_regente[k][2]=formatMilhar(float(lista_regente[k][2]))
        lista_suporte[k][1]=formatMilhar(float(lista_suporte[k][1]))
        lista_suporte[k][2]=formatMilhar(float(lista_suporte[k][2]))

        row1="B"+str(hlinha)
        row2="C"+str(hlinha)

        lista_impressao_1.append(
            [
               lista_regente[k][0],
               lista_regente[k][2],
               lista_suporte[k][2],
               '='+row1+'+'+row2,
               lista_regente[k][1]
            ]
        )
        hlinha+=1


    hlinha=hlinha+5

    for k in range(len(lista_regente_t)):
        soma = formatMilhar(float(lista_regente_t[k][2])+float(lista_suporte_t[k][2]))
        lista_regente_t[k][1]=formatMilhar(float(lista_regente_t[k][1]))
        lista_regente_t[k][2]=formatMilhar(float(lista_regente_t[k][2]))
        lista_suporte_t[k][1]=formatMilhar(float(lista_suporte_t[k][1]))
        lista_suporte_t[k][2]=formatMilhar(float(lista_suporte_t[k][2]))

        row1="B"+str(hlinha)
        row2="C"+str(hlinha)

        lista_impressao_2.append(
            [
               lista_regente_t[k][0],
               lista_regente_t[k][2],
               lista_suporte_t[k][2],
               '='+row1+'+'+row2,
               lista_regente_t[k][1]
            ]
        )

        hlinha+=1


    for k in range(len(lista_impressao_1)):
        writer.writerow(lista_impressao_1[k])

    writer.writerow([])
    writer.writerow([])
    writer.writerow([])
    writer.writerow(['Temporarios - Regentes e Suporte'])
    writer.writerow(['Nivel','Regente 100h','Suporte 100h','Soma','Vencimento'])

    for k in range(len(lista_impressao_2)):
        writer.writerow(lista_impressao_2[k])

    writer.writerow([])
    writer.writerow([])
    writer.writerow(['Soma dos Eventos'])
    writer.writerow(['Evento','Efetivo','Tempórario'])
    for k in range(len(lista_somaEventos)):
        writer.writerow(lista_somaEventos[k])


    return response


def tabelaRegenteSuporte2(id_municipio,ano,mes,tabela):
    opcao=''
    query1=None
    query2=None
    titulo='Tabela Regente/Suporte'
    municipio=''
    referencia=''
    rs=0
    lista_eventos=[]
    lista2=[]
    total=0
    total_v=0
    total_d=0
    total_r=0
    qT=0
    if (1==1):
        obj=Municipio.objects.get(id_municipio=id_municipio)
        municipio=obj.municipio
        if tabela=='Suporte':
            suporte='S'
        else:
            suporte='N'
        mesx = str(int(mes)+100)[-2:]

        anomes = int(ano+mesx)
        referencia = mesx+"/"+ano

        tp_vinculo_efetivo=()
        lista = [k.id_vinculo for k in Vinculo.objects.filter(id_municipio=id_municipio,grupo='E')]
        for k in range(len(lista)):
            tp_vinculo_efetivo += (lista[k],)

        tp_vinculo_temporario=()
        if tabela=='Suporte':
            lista = [k.id_vinculo for k in Vinculo.objects.filter(id_municipio=id_municipio,grupo__in=['T','C'])]
        else:
            lista = [k.id_vinculo for k in Vinculo.objects.filter(id_municipio=id_municipio,grupo__in=['T'])]
        for k in range(len(lista)):
            tp_vinculo_temporario += (lista[k],)


        tp_funcao_professor=()
        lista = [k.id_funcao for k in Funcao.objects.filter(id_municipio=id_municipio,professor='S')]
        for k in range(len(lista)):
            tp_funcao_professor += (lista[k],)

        tp_evento_ampliacao_ch=()
        lista = [k.id_evento for k in Evento.objects.filter(id_municipio=id_municipio,ampliacao_ch='S')]
        for k in range(len(lista)):
            tp_evento_ampliacao_ch += (lista[k],)

        lista_xeventos_tipo_1 = [k.id_evento for k in XEvento.objects.filter(id_municipio=id_municipio,tipo='1')]
        lista_xeventos_tipo_2 = [k.id_evento for k in Evento.objects.filter(id_municipio=id_municipio).filter(Q(ampliacao_ch='S') | Q(evento__startswith='VENCIMENTO BASE'))]

        # query para definir a ampliacao de carga horaria somente dos professores agrupando pelo salário (salario_100H)
        # o fórmula é dividindo a soma dos valores do evento ampliacao pela salario_100H
        if len(tp_evento_ampliacao_ch)>0:
            dict_AmpCHEfetivoSemPos=fun_dict_ampliacaoch(id_municipio,anomes,suporte,tp_vinculo_efetivo,tp_evento_ampliacao_ch,'N')
            dict_AmpCHEfetivoComPos=fun_dict_ampliacaoch(id_municipio,anomes,suporte,tp_vinculo_efetivo,tp_evento_ampliacao_ch,'S')

            dict_AmpCHTemporarioComPos=fun_dict_ampliacaoch(id_municipio,anomes,suporte,tp_vinculo_temporario,tp_evento_ampliacao_ch,'S')
            dict_AmpCHTemporarioSemPos=fun_dict_ampliacaoch(id_municipio,anomes,suporte,tp_vinculo_temporario,tp_evento_ampliacao_ch,'N')


        else:
            dict_AmpCHEfetivoSemPos=dict(zip([0],[0]))
            dict_AmpCHEfetivoComPos=dict(zip([0],[0]))

            dict_AmpCHTemporarioSemPos=dict(zip([0],[0]))
            dict_AmpCHTemporarioComPos=dict(zip([0],[0]))


        qNProfE=fun_Folhames_nao_professor(id_municipio,anomes,suporte,tp_vinculo_efetivo,tp_funcao_professor)
        qSProfE=fun_Folhames_professor(id_municipio,anomes,suporte,tp_vinculo_efetivo,tp_funcao_professor)



        qEventosE=fun_listaEventos(id_municipio,anomes,suporte,tp_vinculo_efetivo)

        qNProfT=fun_Folhames_nao_professor(id_municipio,anomes,suporte,tp_vinculo_temporario,tp_funcao_professor)
        qSProfT=fun_Folhames_professor(id_municipio,anomes,suporte,tp_vinculo_temporario,tp_funcao_professor)
        qEventosT=fun_listaEventos(id_municipio,anomes,suporte,tp_vinculo_temporario)
        qEventosAmpliacaoCH=[k.id_evento for k in Evento.objects.filter(id_municipio=id_municipio,ampliacao_ch='S')]


        lista101=[]
        lista102=[]
        lista201=[]
        lista202=[]

        lcompchE=[]
        lista=[]
        lista1=[]
        lista2=[]
        lista_impressao_a=[]
        lista_impressao_b=[]
        lista_impressao_c=[]
        lista_impressao_d=[]

        lista_impressao=[]

        # Dicionario (id_funcao X funcao) tirado da tabela Tab2_Funcao
        dictFuncoes=listagens.criarDictIdFuncoes(id_municipio)

        if tabela=='Regente':
            label_arquivo='tabelaRegente-'+municipio+'.csv'
            titulo_relatorio='Regentes Efetivos e Temporarios'
            primeira_parte='Regentes Efetivo'
            segunda_parte='Regentes Temporario'
        else:
            label_arquivo='tabelaSuporte-'+municipio+'.csv'
            titulo_relatorio='Suporte Efetivos e Temporarios'
            primeira_parte='Suporte Efetivo'
            segunda_parte='Suporte Temporario'

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename='+label_arquivo

        #cabecalho = ['Nivel (Função)','100H','200H','Ampl.C.Hora','TOTAL','TOTAL 100H','Vencto','Sal.Base']
        cabecalho=['NIVEL','100-Horas','200-Horas','Ampliacao-CH','Total','Total 100Horas','Vencimento','SalarioBase']
        writer = csv.writer(response, delimiter=';')
        response.write(u'\ufeff'.encode('utf8'))
        lista_impressao.append([municipio+' '+str(anomes),titulo_relatorio])
        lista_impressao.append([''])
        lista_impressao.append([primeira_parte])
        lista_impressao.append(cabecalho)


        lista=[]
        row=1
        listav=[]
        iii=0
        lista_controle=[]
        somaGeral=0
        soma=0
        lista_impressao_a=fun_lista_impressao_a(qNProfE,qSProfE,dict_AmpCHE,id_municipio)
        lista_impressao_b=fun_lista_impressao_b(qEventosE,id_municipio,lista_xeventos_tipo_1,lista_xeventos_tipo_2,qEventosAmpliacaoCH)

        lista_impressao_c=fun_lista_impressao_a(qNProfT,qSProfT,dict_AmpCHT,id_municipio)
        lista_impressao_d=fun_lista_impressao_b(qEventosT,id_municipio,lista_xeventos_tipo_1,lista_xeventos_tipo_2,qEventosAmpliacaoCH)
        for k in range(len(lista_impressao)):
            writer.writerow(lista_impressao[k])

        hlinha=4
        for k in range(len(lista_impressao_a)):
            hlinha+=1
            writer.writerow(lista_impressao_a[k])
            s1=lista_impressao_a[k][-1:][0]
            s2=s1.replace('.','')
            s3=s2.replace(',','.')
            soma+=float(s3)
        rangeS="=soma(H5:H"+str(hlinha)+")"
        #writer.writerow(['','','','','','','Soma',formatMilhar(soma)])
        writer.writerow(['','','','','','','Soma',rangeS])

        for k in range(len(lista_impressao_b)):
            writer.writerow(lista_impressao_b[k])

        writer.writerow([''])
        writer.writerow([''])
        writer.writerow([segunda_parte])
        writer.writerow(cabecalho)

        soma=0
        for k in range(len(lista_impressao_c)):
            writer.writerow(lista_impressao_c[k])
            s1=lista_impressao_c[k][-1:][0]
            s2=s1.replace('.','')
            s3=s2.replace(',','.')
            soma+=float(s3)
        writer.writerow(['','','','','','','Soma',formatMilhar(soma)])



        for k in range(len(lista_impressao_d)):
            writer.writerow(lista_impressao_d[k])

        return response



def tabelaRegenteSuporte(request):

    opcao=''
    query1=None
    query2=None
    titulo='Tabela Regente/Suporte'
    municipio=''
    referencia=''
    rs=0
    lista_eventos=[]
    lista2=[]
    total=0
    total_v=0
    total_d=0
    total_r=0
    qT=0
    municipios = Municipio.objects.filter(empresa__in=['SS','Layout','Aspec']).order_by('municipio')
    if (request.method == "POST"):
        id_municipio=int(request.POST['municipio'])
        ano=request.POST['ano']
        mes=request.POST['mes']
        obj=Municipio.objects.get(id_municipio=id_municipio)
        municipio=obj.municipio
        tabela=request.POST['tabela']
        tabela=tabela.upper()
        if tabela=='SUPORTE':
            suporte='S'
        else:
            suporte='N'

        mesx = str(int(mes)+100)[-2:]
        anomes = int(ano+mesx)
        referencia = mesx+"/"+ano

        tp_vinculo_efetivo=()
        lista = [k.id_vinculo for k in Vinculo.objects.filter(id_municipio=id_municipio,grupo='E')]
        for k in range(len(lista)):
            tp_vinculo_efetivo += (lista[k],)

        tp_vinculo_temporario=()
        if tabela=='SUPORTE':
            lista = [k.id_vinculo for k in Vinculo.objects.filter(id_municipio=id_municipio,grupo__in=['T','C'])]
        else:
            lista = [k.id_vinculo for k in Vinculo.objects.filter(id_municipio=id_municipio,grupo__in=['T'])]
        for k in range(len(lista)):
            tp_vinculo_temporario += (lista[k],)


        tp_funcao_professor=()
        lista = [k.id_funcao for k in Funcao.objects.filter(id_municipio=id_municipio,professor='S')]
        for k in range(len(lista)):
            tp_funcao_professor += (lista[k],)

        tp_evento_ampliacao_ch=()
        lista = [k.id_evento for k in Evento.objects.filter(id_municipio=id_municipio,ampliacao_ch='S')]
        for k in range(len(lista)):
            tp_evento_ampliacao_ch += (lista[k],)

        lista_eventos_suporte = [k.id_evento for k in Evento.objects.filter(id_municipio=id_municipio,suporte='S')]
        lista_eventos_carater_salario = [k.id_evento for k in Evento.objects.filter(id_municipio=id_municipio).filter(carater_salario='S')]



        # query para definir a ampliacao de carga horaria somente dos professores agrupando pelo salário (salario_100H)
        # o fórmula é dividindo a soma dos valores do evento ampliacao pela salario_100H
        if len(tp_evento_ampliacao_ch)>0:
            dict_AmpCHEf=fun_dict_ampliacaoch(id_municipio,anomes,suporte,tp_vinculo_efetivo,tp_evento_ampliacao_ch,'')
            dict_AmpCHEfPos=fun_dict_ampliacaoch(id_municipio,anomes,suporte,tp_vinculo_efetivo,tp_evento_ampliacao_ch,'pos')

            dict_AmpCHTp=fun_dict_ampliacaoch(id_municipio,anomes,suporte,tp_vinculo_temporario,tp_evento_ampliacao_ch,'')
            dict_AmpCHTpPos=fun_dict_ampliacaoch(id_municipio,anomes,suporte,tp_vinculo_temporario,tp_evento_ampliacao_ch,'pos')

        else:
            dict_AmpCHEf=dict(zip([0],[0]))
            dict_AmpCHTp=dict(zip([0],[0]))
            dict_AmpCHEfPos=dict(zip([0],[0]))
            dict_AmpCHTpPos=dict(zip([0],[0]))


        qNProfE=fun_Folhames_nao_professor(id_municipio,anomes,suporte,tp_vinculo_efetivo,tp_funcao_professor)
        qSProfE=fun_Folhames_professor(id_municipio,anomes,suporte,tp_vinculo_efetivo,tp_funcao_professor)
        qSPosEF=fun_Folhames_profesPos(id_municipio,anomes,suporte,tp_vinculo_efetivo,tp_funcao_professor)


        qEventosE=fun_listaEventos(id_municipio,anomes,suporte,tp_vinculo_efetivo)

        qNProfT=fun_Folhames_nao_professor(id_municipio,anomes,suporte,tp_vinculo_temporario,tp_funcao_professor)
        qSProfT=fun_Folhames_professor(id_municipio,anomes,suporte,tp_vinculo_temporario,tp_funcao_professor)
        qSPosTP=fun_Folhames_profesPos(id_municipio,anomes,suporte,tp_vinculo_temporario,tp_funcao_professor)


        qEventosT=fun_listaEventos(id_municipio,anomes,suporte,tp_vinculo_temporario)
        qEventosAmpliacaoCH=[k.id_evento for k in Evento.objects.filter(id_municipio=id_municipio,ampliacao_ch='S')]


        lista101=[]
        lista102=[]
        lista201=[]
        lista202=[]

        lcompchE=[]
        lista=[]
        lista1=[]
        lista2=[]
        lista_impressao_a=[]
        lista_impressao_b=[]
        lista_impressao_c=[]
        lista_impressao_d=[]

        lista_impressao=[]

        # Dicionario (id_funcao X funcao) tirado da tabela Tab2_Funcao
        dictFuncoes=listagens.criarDictIdFuncoes(id_municipio)

        if tabela=='REGENTE':
            label_arquivo='tabelaRegente-'+municipio+'.csv'
            titulo_relatorio='Regentes Efetivos/Temporarios'
            primeira_parte='Regentes Efetivo'
            segunda_parte='Regentes Temporario'
        else:
            label_arquivo='tabelaSuporte-'+municipio+'.csv'
            titulo_relatorio='Suporte Efetivos/Temporarios'
            primeira_parte='Suporte Efetivo'
            segunda_parte='Suporte Temporario'

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename='+label_arquivo

        #cabecalho = ['Nivel (Função)','100H','200H','Ampl.C.Hora','TOTAL','TOTAL 100H','Vencto','Sal.Base']
        cabecalho=['NIVEL','100-Horas','200-Horas','Ampliacao-CH','Total','Total 100Horas','Vencimento','SalarioBase']
        writer = csv.writer(response, delimiter=';')
        response.write(u'\ufeff'.encode('utf8'))
        lista_impressao.append([municipio+' '+str(anomes),titulo_relatorio])
        lista_impressao.append([''])
        lista_impressao.append([primeira_parte])
        lista_impressao.append(cabecalho)


        lista=[]
        row=1
        listav=[]
        iii=0
        lista_controle=[]
        somaGeral=0
        soma=0
        lista_impressao_a=fun_lista_impressao_a(qNProfE,qSProfE,qSPosEF,dict_AmpCHEf,dict_AmpCHEfPos,id_municipio)
        (lista_impressao_b, ls_soma_efetivo)=fun_lista_impressao_b(qEventosE,id_municipio,lista_eventos_suporte,lista_eventos_carater_salario,qEventosAmpliacaoCH)
        lista_impressao_a.sort()

        lista_impressao_c=fun_lista_impressao_a(qNProfT,qSProfT,qSPosTP,dict_AmpCHTp,dict_AmpCHTpPos,id_municipio)
        (lista_impressao_d, ls_soma_temporario)=fun_lista_impressao_b(qEventosT,id_municipio,lista_eventos_suporte,lista_eventos_carater_salario,qEventosAmpliacaoCH)
        lista_impressao_c.sort()

        for k in range(len(lista_impressao)):
            writer.writerow(lista_impressao[k])

        hlinha=4
        for k in range(len(lista_impressao_a)):
            hlinha+=1
            writer.writerow(lista_impressao_a[k])
            s1=lista_impressao_a[k][-1:][0]
            s2=s1.replace('.','')
            s3=s2.replace(',','.')
            soma+=float(s3)
        rangeS="=soma(H5:H"+str(hlinha)+")"
        #writer.writerow(['','','','','','','Soma',formatMilhar(soma)])
        writer.writerow(['','','','','','','Soma',rangeS])

        for k in range(len(lista_impressao_b)):
            writer.writerow(lista_impressao_b[k])

        writer.writerow([''])
        writer.writerow([''])
        writer.writerow([segunda_parte])
        writer.writerow(cabecalho)

        soma=0
        for k in range(len(lista_impressao_c)):
            writer.writerow(lista_impressao_c[k])
            s1=lista_impressao_c[k][-1:][0]
            s2=s1.replace('.','')
            s3=s2.replace(',','.')
            soma+=float(s3)
        writer.writerow(['','','','','','','Soma',formatMilhar(soma)])



        for k in range(len(lista_impressao_d)):
            writer.writerow(lista_impressao_d[k])

        writer.writerow([])
        writer.writerow([])
        writer.writerow([])

        if tabela=='REGENTE' :
            writer.writerow(['Regente Resumo'])
        else:
            writer.writerow(['Suporte Resumo'])

        writer.writerow(['Item','Temporario','Efetivo','Total'])
        total_sbase=ls_soma_temporario[0][1]+ls_soma_efetivo[0][1]
        total_adicional=ls_soma_temporario[1][1]+ls_soma_efetivo[1][1]
        total_suporte=ls_soma_temporario[2][1]+ls_soma_efetivo[2][1]

        total_c1=ls_soma_temporario[0][1]+ls_soma_temporario[1][1]+ls_soma_temporario[2][1]
        total_c2=ls_soma_efetivo[0][1]+ls_soma_efetivo[1][1]+ls_soma_efetivo[2][1]


        total_c3=total_c1+total_c2

        writer.writerow(['S. Base',formatMilhar(ls_soma_temporario[0][1]),formatMilhar(ls_soma_efetivo[0][1]),formatMilhar(total_sbase)])
        writer.writerow(['Adicionais',formatMilhar(ls_soma_temporario[1][1]),formatMilhar(ls_soma_efetivo[1][1]),formatMilhar(total_adicional)])
        if tabela=='SUPORTE':
            writer.writerow(['Suporte',formatMilhar(ls_soma_temporario[2][1]),formatMilhar(ls_soma_efetivo[2][1]),formatMilhar(total_suporte)])


        writer.writerow(['Encargos','','',''])

        writer.writerow(['Totais',formatMilhar(total_c1),formatMilhar(total_c2),formatMilhar(total_c3)])

        return response
    else:
        return render(request, 'app01/tabelaRegenteSuporte.html',
            {
                'titulo': titulo,
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



def fun_Folhames_nao_professor(id_municipio,anomes,suporte,tp_vinculo_efetivo,tp_funcao_professor):
    cursor = connection.cursor()
    cursor.execute("Select id_funcao,carga_horaria,CAST(salario_100H AS DECIMAL(0)) as salario_100H_int,MIN(salario_100H) AS salario_100H,sum(participacao) as somaParticipacao,sum(vencimento_base) as somaVencimento \
    from folhames where id_municipio=%s and anomes=%s \
    and fundeb='S' and suporte=%s and id_vinculo in %s and id_funcao not in %s \
    and salario>0 group by id_funcao,carga_horaria,CAST(salario_100H AS DECIMAL(0)) order by id_funcao",[id_municipio,anomes,suporte,tp_vinculo_efetivo,tp_funcao_professor]);
    query = dictfetchall(cursor)
    return query

def fun_Folhames_professor(id_municipio,anomes,suporte,tp_vinculo_efetivo,tp_funcao_professor):
    cursor = connection.cursor()
    cursor.execute("Select id_funcao,carga_horaria,CAST(salario_100H AS DECIMAL(0)) as salario_100H_int,MIN(salario_100H) AS salario_100H,sum(participacao) as somaParticipacao,sum(vencimento_base) as somaVencimento \
    from folhames fm where id_municipio=%s and anomes=%s \
    and fundeb='S' and suporte=%s and id_vinculo in %s and id_funcao in %s \
    and not exists (select * from folhaeventos fv,eventos ev where fv.id_evento=ev.id_evento and fv.id_municipio=fm.id_municipio and fv.anomes=fm.anomes and fv.cod_servidor=fm.cod_servidor and ev.posgraduacao='S') \
    and salario>0 group by id_funcao,carga_horaria,CAST(salario_100H AS DECIMAL(0))  order by id_funcao",[id_municipio,anomes,suporte,tp_vinculo_efetivo,tp_funcao_professor]);
    query = dictfetchall(cursor)
    return query

def fun_Folhames_profesPos(id_municipio,anomes,suporte,tp_vinculo_efetivo,tp_funcao_professor):
    cursor = connection.cursor()
    cursor.execute("Select id_funcao,carga_horaria,CAST(salario_100H AS DECIMAL(0)) as salario_100H_int,MIN(salario_100H) AS salario_100H,sum(participacao) as somaParticipacao,sum(vencimento_base) as somaVencimento \
    from folhames fm where id_municipio=%s and anomes=%s \
    and fundeb='S' and suporte=%s and id_vinculo in %s and id_funcao in %s \
    and exists (select * from folhaeventos fv,eventos ev where fv.id_evento=ev.id_evento and fv.id_municipio=fm.id_municipio and fv.anomes=fm.anomes and fv.cod_servidor=fm.cod_servidor and ev.posgraduacao='S') \
    and salario>0 group by id_funcao,carga_horaria,CAST(salario_100H AS DECIMAL(0)) order by id_funcao",[id_municipio,anomes,suporte,tp_vinculo_efetivo,tp_funcao_professor]);
    query = dictfetchall(cursor)
    return query



def fun_listaEventos(id_municipio,anomes,suporte,tp_vinculo_efetivo):
    qlista=[qS['cod_servidor'] for qS in Folhames.objects.filter(id_municipio=id_municipio,anomes=anomes,suporte=suporte,id_vinculo__in=tp_vinculo_efetivo,id_setor__in=[ss.id_setor for ss in Setor.objects.filter(id_municipio=id_municipio,fundeb='S')]).values('cod_servidor').order_by('cod_servidor')]
    #existem alguns eventos que não devem sair na lista qEventos, por exemplo, ampliacao de carga horaria
    #qEventosON=[qS.id_evento for qS in Evento.objects.filter(id_municipio=id_municipio,ampliacao_ch='N')]
    qEventos=Folhaevento.objects.filter(id_municipio=id_municipio,anomes=anomes,cod_servidor__in=qlista).values('id_evento').annotate(soma=Sum('valor'))
    #qEventos=Folhaevento.objects.filter(id_municipio=id_municipio,anomes=anomes,cod_servidor__in=qlista).values('id_evento').annotate(soma=Sum('valor'))
    return qEventos

def fun_lista_impressao_a(qNProf,qSProf,qSPos,dict_AmpCH,dict_AmpCHPos,id_municipio):
    lista_impressao_a=[]
    lista_controle=[]
    somaGeral=0
    dictFuncoes=listagens.criarDictIdFuncoes(id_municipio)
    for qy in qNProf:
        id_funcao=qy['id_funcao']
        salario_100h=qy['salario_100H']
        salario_100h_int=qy['salario_100H_int']
        if (id_funcao,salario_100h_int) not in lista_controle:
            lista_impressao_a.append(coletaDados_nprof(id_funcao,salario_100h_int,salario_100h,qNProf,dictFuncoes))
            lista_controle.append((id_funcao,salario_100h_int))

    lista_controle=[]
    for qy in qSProf:
        if qy['carga_horaria']!=100 and qy['carga_horaria']!=200:
            continue
        id_funcao=qy['id_funcao']
        salario_100H=qy['salario_100H']
        salario_100H_int=qy['salario_100H_int']
        if [id_funcao,salario_100H_int] not in lista_controle:
            lista_impressao_a.append(coletaDados_sprof(id_funcao,salario_100H_int,salario_100H,qSProf,dictFuncoes,dict_AmpCH,''))
            lista_controle.append([id_funcao,salario_100H_int])

    lista_controle=[]
    for qy in qSPos:
        if qy['carga_horaria']!=100 and qy['carga_horaria']!=200:
            continue
        id_funcao=qy['id_funcao']
        salario_100H=qy['salario_100H']
        salario_100H_int=qy['salario_100H_int']
        if [id_funcao,salario_100H_int] not in lista_controle:
            lista_impressao_a.append(coletaDados_sprof(id_funcao,salario_100H_int,salario_100H,qSPos,dictFuncoes,dict_AmpCHPos,'pos'))
            lista_controle.append([id_funcao,salario_100H_int])

    return lista_impressao_a



def fun_lista_impressao_b(qEventos,id_municipio,ls_eventos_suporte,ls_eventos_carater_salario,listaAmpliacaoCH):
    lista_impressao_b=[]
    lista_impressao_b.append([''])
    lista_impressao_b.append([''])
    lista_impressao_b.append([''])
    lista_impressao_b.append(['Resumo Eventos *'])
    ls_suporte=[]
    lista_resumo=[]


    dict_eventoXidevento = listagens.criarDictEventos(id_municipio)

    soma1=0
    soma2=0
    soma_salario=0
    soma_adicionais=0
    soma_suporte=0

    for key,value in dict_eventoXidevento.items():
        for qx in qEventos:
            vaux=0
            if qx['id_evento'] in ls_eventos_suporte:
                if qx['id_evento']==key:
                    ls_suporte.append([value,formatMilhar(qx['soma'])])
                    soma2+=qx['soma']
                    soma_suporte+=qx['soma']
                    vaux=1
            if qx['id_evento'] in ls_eventos_carater_salario:
                if qx['id_evento']==key:
                    lista_impressao_b.append([value,formatMilhar(qx['soma'])])
                    soma_salario+=qx['soma']
                    soma2+=qx['soma']
                    vaux=1
            if vaux==1:
                break
            if qx['id_evento']==key:
                soma2+=qx['soma']
                lista_resumo.append([value,formatMilhar(qx['soma'])])
                soma_adicionais+=qx['soma']
                break

    lista_impressao_b.append([''])
    lista_impressao_b.append([''])
    for kev in ls_suporte:
        lista_impressao_b.append(kev)

    lista_impressao_b.append([''])
    lista_impressao_b.append([''])

    lista_resumo.append(['Soma',formatMilhar(soma2)]) 
    for kres in lista_resumo:
        lista_impressao_b.append(kres)
    return [lista_impressao_b,[['soma_salario',soma_salario],['soma_adicionais',soma_adicionais],['soma_suporte',soma_suporte]]]

def coletaDados_nprof(id_funcao,salario_100h_int,salario_100h,query,dictFuncoes):
    qtde100=0
    qtde200=0
    soma100=0
    soma200=0
    salario100=0
    salario200=0
    q100=0
    q200=0
    lista=[]
    total_geral=0
    for q in query:
        if q['id_funcao']==id_funcao and q['salario_100H_int']==salario_100h_int:
            if int(q['carga_horaria'])==100:
                qtde100=qtde100+q['somaParticipacao']
                q100=q100+q['somaParticipacao']
                salario100=salario_100h
                soma100=soma100+q['somaVencimento']
            else:
                q200=q200+q['somaParticipacao']
                qtde200=qtde200+q['somaParticipacao']
                salario100=salario_100h
                soma200=soma200+q['somaVencimento']
    qtde100=str(qtde100)
    qtde100=qtde100.replace('.',',')
    qtde200=str(qtde200)
    qtde200=qtde200.replace('.',',')

    qSoma1=q100+q200
    qSoma2=q100+q200*2
    lista.append(dictFuncoes[id_funcao]+' ('+str(id_funcao)+')')
    lista.append(str(qtde100)[0:6])
    lista.append(str(qtde200)[0:6])
    lista.append('0')
    lista.append(formatMilhar(qSoma1))
    lista.append(formatMilhar(qSoma2))
    total = qSoma2*salario100
    lista.append(formatMilhar(salario100))
    lista.append(formatMilhar(total))
    #lista.append(total)
    return lista

def coletaDados_sprof(id_funcao,salario_100H_int,salario_100H,query,dictFuncoes,dictAmpliacaoCH,posgraduacao):
    qtde100=0
    qtde200=0
    soma100=0
    soma200=0
    salario100=0
    salario200=0
    q100=0
    q200=0
    lista=[]
    for q in query:
        if q['id_funcao']==id_funcao and q['salario_100H_int']==salario_100H_int:
            if int(q['carga_horaria'])==100:
                q100=q100+q['somaParticipacao']
                qtde100=qtde100+q['somaParticipacao']
                salario100=salario_100H
                soma100=soma100+q['somaVencimento']
            elif int(q['carga_horaria'])==200:
                q200=q200+q['somaParticipacao']
                qtde200=qtde200+q['somaParticipacao']
                salario100=salario_100H
                soma200=soma200+q['somaVencimento']
    qtde100=str(round(qtde100,2))
    qtde100=qtde100.replace('.',',')
    qtde200=str(qtde200)
    qtde200=qtde200.replace('.',',')

    if posgraduacao=='':
        ampliacao=dictAmpliacaoCH.get(str(id_funcao)+'-'+str(salario_100H_int),0)
    else:
        ampliacao=dictAmpliacaoCH.get(str(id_funcao)+'pos-'+str(salario_100H_int),0)

    qSoma1=q100+q200+ampliacao
    qSoma2=q100+q200*2+ampliacao

    if posgraduacao=='':
        lista.append(dictFuncoes[id_funcao]+' ('+str(id_funcao)+')')
    else:
        lista.append(dictFuncoes[id_funcao]+' POS ('+str(id_funcao)+')')

    lista.append(str(qtde100))
    lista.append(str(qtde200))
    lista.append(str(ampliacao).replace('.',','))
    lista.append(formatMilhar(qSoma1))
    lista.append(formatMilhar(qSoma2))
    lista.append(formatMilhar(salario100))
    total=qSoma2*salario100
    lista.append(formatMilhar(total))

    return lista


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

def dictfetchall(cursor):
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]



