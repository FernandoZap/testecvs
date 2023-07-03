from .models import Secretaria,Setor,Funcao,Evento,Vinculo,Tab_salario,Tab_salarioch,Servidor,Folhames,Municipio

def listagemServidores(id_municipio):
    lista=[]
    servidores = Servidor.objects.filter(id_municipio=id_municipio)
    for servidor in servidores:
        lista.append(str(servidor.cod_servidor))
    return lista


def criarDictVinculos(id_municipio,tipo):
        lista1=[]
        lista2=[]
        lista3=[]
        secs = Vinculo.objects.filter(id_municipio=id_municipio).order_by('id_vinculo')
        for sec in secs:
                lista1.append(
                        sec.vinculo.upper()
                        )
                lista2.append(
                        sec.id_vinculo
                        )
                lista3.append(
                       sec.grupo
                    )

        if tipo=='id':
            return dict(zip(lista1,lista2))
        else:
            return dict(zip(lista1,lista3))


def listagemVinculos(id_municipio):
        lista=[]
        vinculos = Vinculo.objects.filter(id_municipio=id_municipio)
        for vinculo in vinculos:
                lista.append(vinculo.vinculo.upper())
        return lista


def listagemFolhames(id_municipio,anomes):
    lista=[]
    folhames = Folhames.objects.filter(id_municipio=id_municipio,anomes=anomes)
    for folha in folhames:
        lista.append(str(folha.cod_servidor)+'-'+str(anomes))
    return lista

def criarDictIdEventosVantagens(id_municipio):
        lista1=[]
        lista2=[]
        secs = Evento.objects.filter(id_municipio=id_municipio,cancelado='N').order_by('evento')
        for sec in secs:
                lista1.append(sec.id_evento)
                lista2.append(sec.evento_out)
        return dict(zip(lista1,lista2))

def criarDictMunicipios():
        lista1=[]
        lista2=[]
        nums = Municipio.objects.filter(empresa__in=['SS','Layout','Aspec'])
        for obj in nums:
                lista1.append(obj.id_municipio)
                lista2.append(obj.municipio)
        return dict(zip(lista1,lista2))


def lista_de_vantagens(id_municipio):
        lista=[]
        vantagens = Evento.objects.filter(id_municipio=id_municipio,cancelado='N')
        for vantagem in vantagens:
                lista.append(vantagem.evento.upper())
        return lista

