from ..models import Servidor,Secretaria,Setor,Funcao,Vinculo,Evento

def colunasValores():
        lista1=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']


        lista2=[]
        lista3=[]
        lista4=[]
        for k in lista1:
                lista2.append('A'+k)
                lista3.append('B'+k)
                lista4.append('C'+k)
        return lista1+lista2+lista3+lista4


def criarDictNomeServidor(id_municipio):
        lista1=[]
        lista2=[]
        objs = Servidor.objects.filter(id_municipio=id_municipio).values('cod_servidor','nome','data_admissao')
        for obj in objs:
                lista1.append(
                        obj['cod_servidor']
                        )
                lista2.append(
                        {'nome':obj['nome'],'data':obj['data_admissao']}
                        )

        return dict(zip(lista1,lista2))


def criarDictIdSecretarias(id_municipio):
        lista1=[]
        lista2=[]
        secs = Secretaria.objects.filter(id_municipio=id_municipio)
        for sec in secs:
                lista1.append(
                        sec.id_secretaria
                        )
                secretaria = sec.secretaria_out if sec.secretaria_out!='' else sec.secretaria
                lista2.append(
                        secretaria
                        )

        return dict(zip(lista1,lista2))


def criarDictIdSetores(id_municipio):
        lista1=[]
        lista2=[]
        secs = Setor.objects.filter(id_municipio=id_municipio).order_by('id_setor')
        for sec in secs:
                lista1.append(
                        sec.id_setor
                        )
                setor = sec.setor_out if sec.setor_out!='' else sec.setor
                lista2.append(
                        setor
                        )

        return dict(zip(lista1,lista2))


def criarDictIdFuncoes(id_municipio):
        lista1=[]
        lista2=[]
        secs = Funcao.objects.filter(id_municipio=id_municipio,cancelado='N')
        for sec in secs:
                lista1.append(
                        sec.id_funcao
                        )
                funcao = sec.funcao_out if sec.funcao_out!='' else sec.funcao
                lista2.append(
                        funcao
                        )

        return dict(zip(lista1,lista2))


def criarDictIdVinculos(id_municipio):
        lista1=[]
        lista2=[]
        secs = Vinculo.objects.filter(id_municipio=id_municipio)
        for sec in secs:
                lista1.append(
                        sec.id_vinculo
                        )
                lista2.append(
                        sec.vinculo
                        )

        return dict(zip(lista1,lista2))

'''
def criarDictRefEventos(id_municipio,anomes):
        lista1=[]
        lista2=[]
        refE=Refeventos.objects.filter(id_municipio=id_municipio,anomes=anomes)
        for ref in refE:
                lista1.append(
                        ref.cod_servidor
                        )
                lista2.append(
                        ref.ref_eventos
                        )

        return dict(zip(lista1,lista2))
'''

def criarDictEventos(id_municipio):
        lista1=[]
        lista2=[]
        secs = Evento.objects.filter(id_municipio=id_municipio,cancelado='N').order_by('evento')
        for sec in secs:
                lista1.append(sec.id_evento)
                evento = sec.evento_out if sec.evento_out!='' else sec.evento
                lista2.append(evento)
        return dict(zip(lista1,lista2))


