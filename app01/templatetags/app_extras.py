from django import template
from django.contrib.humanize.templatetags.humanize import intcomma


register = template.Library()


'''
@register.simple_tag
def total_folha():

    return Folha.objects.count()
'''
'''
@register.simple_tag
def total_folha_mes(id_municipio,anomes,tipo):

    cursor = connection.cursor()

    sql = "select f001_total_folha("+str(id_municipio)+","+str(anomes)+",'"+tipo+"')"

    cursor.execute(sql)
    r0 = cursor.fetchall()
    #r0 = dictfetchall(cursor)

    r1 =  (r0[0])[0]

    cursor.close()
    del cursor

    if r1 is None:
        r1=0

    r=currency(r1)

    comp=len(str(r))

    r1=str(r)

    r = r1[0:comp-3]+','+r1[-2:]

    return r

'''
'''
@register.simple_tag
def total_departamento(id_municipio,anomes,tipo,id_departamento):

    cursor = connection.cursor()

    sql = "SELECT f002_total_departamento("+str(id_municipio)+","+str(anomes)+",'"+tipo+"',"+str(id_departamento)+")"

    cursor.execute(sql)
    r0 = cursor.fetchall()

    r1 =  (r0[0])[0]

    cursor.close()
    del cursor

    if r1 is None:
        r1=0

    r=currency(r1)

    comp=len(str(r))

    r1=str(r)

    r = r1[0:comp-3]+','+r1[-2:]

    return r
'''
'''
@register.simple_tag
def total_setor(id_municipio,anomes,tipo,id_departamento,id_setor):

    cursor = connection.cursor()

    sql = "SELECT f003_total_setor("+str(id_municipio)+","+str(anomes)+",'"+tipo+"',"+str(id_departamento)+","+str(id_setor)+")"

    cursor.execute(sql)
    r0 = cursor.fetchall()
    #r2 = dictfetchall(cursor)

    r1 =  (r0[0])[0]

    cursor.close()
    del cursor

    if r1 is None:
        r1=0

    r=currency(r1)

    comp=len(str(r))

    r1=str(r)


    r = r1[0:comp-3]+','+r1[-2:]

    return r
'''



def currency(dollars):
    dollars = round(float(dollars), 2)
    return "%s%s" % (intcomma(int(dollars)), ("%0.2f" % dollars)[-3:])
register.filter('currency', currency)


@register.simple_tag
def formatMilhar(valor):
    r1=currency(valor)
    r = r1[0:len(r1)-3]+','+r1[-2:]

    return r




