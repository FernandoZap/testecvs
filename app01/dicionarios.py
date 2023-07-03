from .models import Secretaria,Setor,Funcao,Evento,Vinculo,Tab_salario,Tab_salarioch,Tabela_salario,CargaHoraria

def de_secretarias(id_municipio):
    lista1=[]
    lista2=[]
    lista3=[]
    secs = Secretaria.objects.filter(id_municipio=id_municipio).order_by('id_secretaria')
    for sec in secs:
        lista1.append(
            sec.secretaria.upper()
        )
        lista2.append(
            sec.id_secretaria
        )
        lista3.append(
            sec.id_secretaria_out if sec.id_secretaria_out>0 else sec.id_secretaria
        )

    return [dict(zip(lista1,lista2)),dict(zip(lista2,lista3))]

def de_setores(id_municipio):
    lista1=[]
    lista2=[]
    lista3=[]
    lista_fundeb=[]
    sts = Setor.objects.filter(id_municipio=id_municipio)
    for st in sts:
        lista1.append(
            st.setor.upper()
        )
        lista2.append(
            st.id_setor
        )
        lista3.append(
            st.id_setor_out if st.id_setor_out>0 else st.id_setor
        )
        if st.fundeb=='S':
            lista_fundeb.append(st.id_setor)

    return [dict(zip(lista1,lista2)),dict(zip(lista2,lista3)),lista_fundeb]


def de_eventos(id_municipio):
    lista1=[]
    lista2=[]
    lista3=[]
    lista_suporte=[]
    lista_ampliacao_ch=[]
    lista_carater_salario=[]
    lista_posgraduacao=[]

    eventos = Evento.objects.filter(id_municipio=id_municipio,cancelado='N')
    for ev in eventos:
        lista1.append(
            ev.evento.upper()
        )
        lista2.append(
            ev.id_evento
        )
        lista3.append(
            ev.id_evento_out if ev.id_evento_out>0 else ev.id_evento
        )
        if ev.suporte=='S':
            lista_suporte.append(ev.id_evento)

        if ev.ampliacao_ch=='S':
            lista_ampliacao_ch.append(ev.id_evento)

        if ev.posgraduacao=='S':
            lista_posgraduacao.append(ev.id_evento)

        if ev.carater_salario=='S':
            lista_carater_salario.append(ev.id_evento)



    return [dict(zip(lista1,lista2)),dict(zip(lista2,lista3)),lista_suporte,lista_ampliacao_ch,lista_posgraduacao,lista_carater_salario]


def de_funcoes(id_municipio):
    lista1=[]
    lista2=[]
    lista3=[]
    lista_prof=[]

    funcs = Funcao.objects.filter(id_municipio=id_municipio,cancelado='N')
    for func in funcs:
        lista1.append(
            func.funcao.upper()
        )

        lista2.append(
            func.id_funcao
        )

        lista3.append(
            func.id_funcao_out
        )
        if func.professor=='S':
           lista_prof.append(func.id_funcao)

    return [dict(zip(lista1,lista2)),dict(zip(lista2,lista3)),lista_prof]


def de_vinculos(id_municipio):
    lista1=[]
    lista2=[]
    vincs = Vinculo.objects.filter(id_municipio=id_municipio)
    for vc in vincs:
        lista1.append(
            vc.vinculo.upper()
        )

        lista2.append(
            vc.id_vinculo
        )

    return dict(zip(lista1,lista2))

def de_tab_salarios(id_municipio):
    lista1=[]
    lista2=[]
    lista3=[]
    tabsal = Tab_salario.objects.filter(id_municipio=id_municipio)
    for tb in tabsal:
        lista1.append(
            tb.id_funcao
        )

        valor_dec=tb.valor
        valor_int=int(tb.valor)
        lista2.append(valor_dec)
        lista3.append(valor_int)


    return [dict(zip(lista1,lista2)),dict(zip(lista1,lista3))]


def de_tab_salariosch(id_municipio):
    lista1=[]
    lista2=[]
    tabsal = Tab_salarioch.objects.filter(id_municipio=id_municipio)
    for tb in tabsal:
        id_funcao_origem = str(tb.id_funcao_origem)
        valor=str(int(tb.valor))
        cargah_errada=str(tb.carga_horaria_errada)
        cargah_certa=str(tb.carga_horaria_certa)
        lista1.append(id_funcao_origem+'-'+valor+'-'+cargah_errada)
        lista2.append(cargah_certa)

    return dict(zip(lista1,lista2))




def de_tabela_salarios(id_municipio):
    lista1=[]
    lista2=[]
    listaf=[]
    listai=[]
    listad=[]

    tabsalA = Tabela_salario.objects.filter(id_municipio=id_municipio)
    tabsalB = Tabela_salario.objects.filter(id_municipio=id_municipio)

    for tb in tabsalA:
        id_funcao_origem=tb.id_funcao_origem
        lista1=[]
        lista2=[]
        for tb2 in tabsalB:
            if tb2.id_funcao_origem==id_funcao_origem:
                lista1.append(tb2.salario_100h_int)
                lista2.append(tb2.salario_100h_dec)
        listaf.append(id_funcao_origem)
        listai.append(lista1)
        listad.append(lista2)


    return [dict(zip(listaf,listai)),dict(zip(listaf,listad))]

def de_secretarias_12(id_municipio):
    lista1=[]
    lista2=[]
    secs = Secretaria.objects.filter(id_municipio=id_municipio).order_by('id_secretaria')
    for sec in secs:
        lista1.append(
            sec.secretaria.upper()
        )
        lista2.append(
            sec.id_secretaria
        )

    return dict(zip(lista1,lista2))


def de_funcoes_out(id_municipio):
    lista1=[]
    lista2=[]

    funcs = Funcao.objects.filter(id_municipio=id_municipio)
    for func in funcs:
        lista1.append(
            func.funcao.upper()
        )

        lista2.append(
            func.id_funcao
        )
    return dict(zip(lista2,lista1))

def dict_funcoesXid(id_municipio):
    lista1=[]
    lista2=[]

    funcs = Funcao.objects.filter(id_municipio=id_municipio,cancelado='N')
    for func in funcs:
        lista1.append(
            func.funcao.upper()
        )
        lista2.append(
            func.id_funcao
        )
    return dict(zip(lista1,lista2))


def dict_secretariasXid(id_municipio):
    lista1=[]
    lista2=[]

    secretarias = Secretaria.objects.filter(id_municipio=id_municipio)
    for obj in secretarias:
        lista1.append(
            obj.secretaria.upper()
        )
        lista2.append(
            obj.id_secretaria
        )
    return dict(zip(lista1,lista2))

def dict_setoresXid(id_municipio):
    lista1=[]
    lista2=[]

    setores = Setor.objects.filter(id_municipio=id_municipio)
    for obj in setores:
        lista1.append(
            obj.setor.upper()
        )
        lista2.append(
            obj.id_setor
        )
    return dict(zip(lista1,lista2))

def dict_eventosXid(id_municipio):
    lista1=[]
    lista2=[]

    eventos = Evento.objects.filter(id_municipio=id_municipio)
    for obj in eventos:
        lista1.append(
            obj.evento.upper()
        )
        lista2.append(
            obj.id_evento
        )
    return dict(zip(lista1,lista2))

def dict_idXEvento(id_municipio):
    lista1=[]
    lista2=[]

    eventos = Evento.objects.filter(id_municipio=id_municipio,cancelado='N')
    for obj in eventos:
        lista1.append(
            obj.evento.upper()
        )
        lista2.append(
            obj.id_evento
        )
    return dict(zip(lista2,lista1))


def dict_idXfuncao(id_municipio):
    lista1=[]
    lista2=[]

    objs = Funcao.objects.filter(id_municipio=id_municipio,cancelado='N')
    for obj in objs:
        lista1.append(
            obj.funcao.upper()
        )
        lista2.append(
            obj.id_funcao
        )
    return dict(zip(lista2,lista1))


def dict_idXsetor(id_municipio):
    lista1=[]
    lista2=[]

    objs = Setor.objects.filter(id_municipio=id_municipio)
    for obj in objs:
        lista1.append(
            obj.setor.upper()
        )
        lista2.append(
            obj.id_setor
        )
    return dict(zip(lista2,lista1))

def dict_idXsecretaria(id_municipio):
    lista1=[]
    lista2=[]

    objs = Secretaria.objects.filter(id_municipio=id_municipio)
    for obj in objs:
        lista1.append(
            obj.secretaria.upper()
        )
        lista2.append(
            obj.id_secretaria
        )
    return dict(zip(lista2,lista1))



def dict_idXvinculo(id_municipio):
    lista1=[]
    lista2=[]

    vinculos = Vinculo.objects.filter(id_municipio=id_municipio)
    for obj in vinculos:
        lista1.append(
            obj.vinculo.upper()
        )
        lista2.append(
            obj.id_vinculo
        )
    return dict(zip(lista2,lista1))


def dict_id_vinculoXgrupo(id_municipio):
    lista1=[]
    lista2=[]
    vincs = Vinculo.objects.filter(id_municipio=id_municipio)
    for vc in vincs:
        lista1.append(
            vc.id_vinculo
        )

        lista2.append(
            vc.grupo
        )

    return dict(zip(lista1,lista2))


def dict_chorigemXid(id_municipio):
    lista1=[]
    lista2=[]

    chs = CargaHoraria.objects.filter(id_municipio=id_municipio)
    for obj in chs:
        lista1.append(
            obj.cargah_origem
        )
        lista2.append(
            obj.id_cargahoraria
        )
    return dict(zip(lista1,lista2))


def cargah_origemXcargah_convertida(id_municipio):
    lista1=[]
    lista2=[]

    chs = CargaHoraria.objects.filter(id_municipio=id_municipio)
    for obj in chs:
        lista1.append(
            obj.cargah_origem
        )
        lista2.append(
            obj.cargah_convertida
        )
    return dict(zip(lista1,lista2))


def dict_eventos_cancelados(id_municipio):
    lista1=[]
    lista2=[]

    eventos = Evento.objects.filter(id_municipio=id_municipio,cancelado='S')
    for ev in eventos:
        lista1.append(
            ev.evento.upper()
        )
        lista2.append(
            ev.id_evento
        )
    return dict(zip(lista1,lista2))

