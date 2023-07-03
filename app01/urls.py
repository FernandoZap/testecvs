from  django.urls import include, path
from django.contrib import admin
from . import views as v1
from .views_excel import views as vv


app_name = 'app01'

urlpatterns = [
    path('cargahoraria', v1.cadastrarCargaHorariaErrada, name='cargahoraria'),
    path('cargahoraria_ajax_01/', v1.cargahoraria_ajax_01, name="cargahoraria_01"),
    path('listar_ch', v1.listarCargaHorariaErrada, name='listar_ch'),
    path('remover_ch/<int:id>', v1.removerCargaHorariaErrada, name='remover_ch'),
    path('tab_salarios',v1.tabela_salarios, name='tabela_salarios'),
    path('importar_excel_folha',v1.importar_excel_folha,name='importar_excel_folha'),
    path('planilhaErrada', v1.planilhaErrada, name='planilhaErrada'),
    path('processarFolha', v1.processarFolha, name='processarFolha'),
    path('listSomaEventos', v1.listSomaEventos, name='listSomaEventos'),
    path('folhasProcessadas', v1.folhasProcessadas, name='folhasProcessadas'),
    path('imprimirFolha', vv.imprimirFolha, name='imprimirFolha'),
    path('tabelaParticipacaoExcel', vv.tabelaParticipacaoExcel, name='tabelaParticipacaoExcel'),
    path('testeparam/<int:id_municipio>', v1.testeparam, name='testeparam'),
    path('testeparam2/<int:id_municipio>/<int:anomes>', v1.testeparam2, name='testeparam2'),
    path('deletarFl',v1.deletar_folha,name='deletarFl'),
    path('mensagemDelFl/<int:id_municipio>/<int:anomes><str:mensagem>',v1.mensagem_deletar_folha, name='mensagemDelFolha'),
    path('atualizarSalario',v1.atualizar_tabela_salario,name='atualizar_salario'),
    path('lerExcel',v1.ler_excel,name='lerExcel'),
    path('gravarFuncao',v1.gravarFuncao,name='gravarFuncao'),
    path('imprimeAnalise/<int:id_municipio>/<int:anomes>/<str:codFuncao>', v1.imprimeAnalise,name='imprimeAnalise'), 
    path('listarModels_01',v1.listarModels_01,name='listarModels_01'),
    path('listarModels_02/<int:id_municipio>/<str:tabela>/<str:complemento>/<str:carater_salario>/<str:pos_graduacao>',v1.listarModels_02,name='listarModels_02'),
    path('consultarSuporte', v1.consultarSuporte,name='consultarSuporte'),
    path('listarModels_03B/<int:id_municipio>/<str:tabela>',v1.listarModels_03B,name='listarModels_03B'),
    path('abrirExcel', v1.abrirExcel, name='abrirExcel'),
    path('listarParticipacaoAmpliacao', v1.listarParticipacaoAmpliacao, name='listarParticipacaoAmpliacao'),
    path('abrirRegenteSuporteMatriz/<int:id_arquivo>', v1.abrirRegenteSuporteMatriz, name='abrirRegenteSuporteMatriz'),
    path('listarExcel_ajax_01/', v1.listarExcel_ajax_01),
    path('listarExcel', v1.listarExcel, name='listarExcel'),
    #path('tabela4Em1', vv.tabelaRegenteSuporteMatrizExcel_teste, name='tabela4Em1'),
]

