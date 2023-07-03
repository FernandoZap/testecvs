from  .models import Folhames,Municipio,Secretaria,Setor,Funcao,Evento,Vinculo
from . import funcoes as fu,dicionarios

def listar_models_02(id_municipio,tabela,complemento,carater_salario,pos_graduacao):
    lista=[]
    ls_ampliacao_ch=['S','N']
    ls_suporte=['S','N']
    ls_carater_salario=['S','N']
    ls_pos_graduacao=['S','N']

    ls_fundeb=['S','N']
    ls_professor=['S','N']
    apelido='T'
    filtro=''
    obs=''
    cancelado='N'
    if 'C'==complemento[0]:
        cancelado='S'

    if tabela=='Eventos':
        if 'A' in complemento:
            ls_ampliacao_ch=['S']
            filtro='Ampliacao de CH'
        if 'S' in complemento:
            ls_suporte=['S']
            if filtro=='':
                filtro='Suporte'
            else:
                filtro='Ampliacao CH e Suporte'
        if 'S' in carater_salario:
            ls_carater_salario=['S']
            if filtro=='':
                filtro='Carater Salario'
            else:
                filtro=filtro+'/'+'Carater Salario'
        if 'S' in pos_graduacao:
            ls_pos_graduacao=['S']
            if filtro=='':
                filtro='Pos Graduacao'
            else:
                filtro=filtro+'/'+'Pos Graduacao'

    elif tabela=='Funcoes':
        if 'P' in complemento:
            ls_professor=['S']
            filtro='Professor'
    elif tabela=='Setores':
        if 'F' in complemento:
            ls_fundeb=['S']
            filtro='Fundeb'
    if 'a' in complemento:
        apelido='S'
        obs='Nome Trocado'
    if filtro!='':
        filtro =' ('+filtro+')'

    if tabela=='Eventos':
        if cancelado=='S':
            eventos = Evento.objects.filter(id_municipio=id_municipio,cancelado='S').order_by('evento')
        else:
            eventos = Evento.objects.filter(id_municipio=id_municipio,ampliacao_ch__in=ls_ampliacao_ch,suporte__in=ls_suporte,carater_salario__in=ls_carater_salario,posgraduacao__in=ls_pos_graduacao,cancelado='N').order_by('evento')
        dict_e=dicionarios.dict_idXEvento(id_municipio)
        for ev in eventos:
            suporte=''
            ampliacao=''
            carater_salario=''
            pos_graduacao=''

            if apelido=='S':
                if ev.id_evento==ev.id_evento_out and ev.evento==ev.evento_out:
                    continue

            if ev.suporte=='S':
                suporte='Suporte'
            if ev.ampliacao_ch=='S':
                ampliacao='Ampliacao de CH'
            if ev.carater_salario=='S':
                carater_salario='SIM'
            if ev.posgraduacao=='S':
                pos_graduacao='SIM'

            if ev.id_evento==ev.id_evento_out:
                if ev.evento==ev.evento_out:
                    descricao2=''
                else:
                    descricao2=ev.evento_out
            else:
                descricao2=dict_e.get(ev.id_evento_out,'')
            lista.append(
                {
                'descricao1':ev.evento,
                'descricao2':descricao2,
                'complemento1':suporte,
                'complemento2':ampliacao,
                'complemento3':carater_salario,
                'complemento4':pos_graduacao
                }
            ) 
    elif tabela=='Funcoes':
        funcoes = Funcao.objects.filter(id_municipio=id_municipio,professor__in=ls_professor,cancelado='N').order_by('funcao')
        dict_f=dicionarios.dict_idXfuncao(id_municipio)
        for ev in funcoes:
            professor=''
            if apelido=='S':
                if ev.id_funcao==ev.id_funcao_out and ev.funcao==ev.funcao_out:
                    continue

            if ev.professor=='S':
                professor='Professor'
            if ev.id_funcao==ev.id_funcao_out:
                if ev.funcao==ev.funcao_out:
                    descricao2=''
                else:
                    descricao2=ev.funcao_out
            else:
                descricao2=dict_f.get(ev.id_funcao_out,'')

            lista.append(
                {
                'descricao1':ev.funcao,
                'descricao2':descricao2,
                'complemento1':professor,
                'complemento2':'',
                'complemento3':'',
                'complemento4':''

                }
            ) 

    elif tabela=='Setores':
        setores = Setor.objects.filter(id_municipio=id_municipio,fundeb__in=ls_fundeb).order_by('setor')
        dict_s=dicionarios.dict_idXsetor(id_municipio)
        for ev in setores:
            if apelido=='S':
                if ev.id_setor==ev.id_setor_out and ev.setor==ev.setor_out:
                    continue

            fundeb=''
            if ev.fundeb=='S':
                fundeb='Fundeb'
            if ev.id_setor==ev.id_setor_out:
                if ev.setor==ev.setor_out:
                    descricao2=''
                else:
                    descricao2=ev.setor_out
            else:
                descricao2=dict_s.get(ev.id_setor_out,'')

            lista.append(
                {
                'descricao1':ev.setor,
                'descricao2':descricao2,
                'complemento1':fundeb,
                'complemento2':'',
                'complemento3':'',
                'complemento4':''

                }
            ) 
    elif tabela=='Secretarias':
        secretarias = Secretaria.objects.filter(id_municipio=id_municipio).order_by('secretaria')
        dict_s=dicionarios.dict_idXsecretaria(id_municipio)
        for ev in secretarias:
            if apelido=='S':
                if ev.id_secretaria==ev.id_secretaria_out and ev.secretaria==ev.secretaria_out:
                    continue
            if ev.id_secretaria==ev.id_secretaria_out:
                if ev.secretaria==ev.secretaria_out:
                    descricao2=''
                else:
                    descricao2=ev.secretaria_out
            else:
                descricao2=dict_s.get(ev.id_secretaria_out,'')


            lista.append(
                {
                'descricao1':ev.secretaria,
                'descricao2':descricao2,
                'complemento1':'',
                'complemento2':'',
                'complemento3':'',
                'complemento4':''

                }
            ) 
    elif tabela=='Vinculos':
        vinculos = Vinculo.objects.filter(id_municipio=id_municipio).order_by('vinculo')
        for ev in vinculos:
            if ev.grupo=='E':
                grupo='EFETIVO'
            elif ev.grupo=='T':
                grupo='TEMPORARIO'
            elif ev.grupo=='C':
                grupo='COMISSIONADO'
            elif ev.grupo=='A':
                grupo='APOSENTADO'
            elif ev.grupo=='P':
                grupo='AGENTE POLITICO'
            else:
                grupo=ev.grupo


            lista.append(
                {
                'descricao1':ev.vinculo,
                'descricao2':'',
                'complemento1':'Grupo :'+grupo,
                'complemento2':''
                }
            )

    elif tabela=='CH':
        chs = CargaHoraria.objects.filter(id_municipio=id_municipio)
        for ch in chs:
            lista.append(
                {
                  'descricao1': ch.cargah_origem,
                  'descricao2': ch.cargah_convertida,
                  'complemento1':'',
                  'complemento2': '',
                  'complemento3':'',
                  'complemento4':''

                }
            )

    return [lista,filtro,obs]


def imprime_analise(id_municipio,anomes,codFuncao):
    lista1=[]
    dict_vinculo=dicionarios.dict_idXvinculo(id_municipio)
    dict_funcao=dicionarios.de_funcoes_out(id_municipio)

    array_funcoes=codFuncao.split(',')
    lista_funcoes=[]
    for k in array_funcoes:
        kl=k.strip()
        lista_funcoes.append(int(kl))

    query=Folhames.objects.filter(id_municipio=id_municipio,anomes=anomes,id_funcao__in=lista_funcoes,fundeb='S').values('id_funcao','cod_servidor','suporte','ampliacao_ch','carga_horaria','salario_100H','id_vinculo','participacao','carga_horaria_origem','vencimento_base','salario').order_by('id_funcao') 

    for q in query:
        funcao=dict_funcao.get(q['id_funcao'],'')
        funcao=funcao+' ('+str(q['id_funcao'])+')'
        cod_servidor=q['cod_servidor']
        suporte=q['suporte']
        if suporte=='S':
            suporte='SIM'
        else:
            suporte='NÃO'
        ampliacao=q['ampliacao_ch']
        if ampliacao=='S':
            ampliacao='SIM'
        else:
            ampliacao='NÃO'
        carga_horaria=q['carga_horaria']
        carga_horaria_origem=q['carga_horaria_origem']
        salario_100H=fu.formatMilhar(q['salario_100H'])
        vinculo=dict_vinculo.get(q['id_vinculo'],'')
        participacao=fu.formatMilhar(q['participacao'])
        vencimento_base=fu.formatMilhar(q['vencimento_base'])
        salario=fu.formatMilhar(q['salario'])

        if q['participacao'] and q['salario_100H']:
            if carga_horaria==100:
                v_calculado=q['participacao']*q['salario_100H']
            else:
                v_calculado=q['participacao']*2*q['salario_100H']
            diferenca = v_calculado-q['vencimento_base']
        else:
            v_calculado=0
            diferenca=0

        lista1.append([funcao,cod_servidor,suporte,ampliacao,carga_horaria_origem,carga_horaria,salario_100H,vencimento_base,salario,vinculo,participacao,fu.formatMilhar(v_calculado),fu.formatMilhar(diferenca)])
    return lista1

