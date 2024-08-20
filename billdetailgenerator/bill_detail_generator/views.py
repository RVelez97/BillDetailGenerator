import csv
from django.http import HttpResponse
from django.shortcuts import render
import re

import xml.etree.ElementTree as et
header=[]
detail_of_bills=[]

def index(request):
    global detail_of_bills,header
    detail_of_bills=[]
    header=[]
    return render(request,'index.html')

def extract_data_from_line(line, pattern):
    return re.sub(pattern, '', line).strip().rstrip('\n')

def results(request):
    if request.method == 'POST':
        global header
        files = request.FILES.getlist('myfiles')
        fields={
            'fechaEmision':True,
            'estab':False,
            'ptoEmi':False,
            'secuencial':False,
            'razonSocial>':True,
            'ruc':False,
            'baseImponible':False,
            'valor':False,
            'importeTotal':True,
            }
        if('show-all-fields-option' in request.POST):
            fields['baseImponible']=True
            fields['valor']=True
            fields['importeTotal']=True
            fields['estab']=True
            fields['ptoEmi']=True
            fields['secuencial']=True
            fields['ruc']=True
        if('show-bill-number-option' in request.POST):
            fields['estab']=True
            fields['ptoEmi']=True
            fields['secuencial']=True
        if('show-ruc-option' in request.POST):
            fields['ruc']=True
        if('show-total-detailed-option' in request.POST):
            fields['baseImponible']=True
            fields['valor']=True
        if fields['razonSocial>']:
            header.append('Razon Social')
        if fields['ruc']:
            header.append('RUC')
        if fields['estab']:
            header.append('Numero de factura')
        if fields['fechaEmision']:
            header.append('Fecha de Emision')
        if fields['baseImponible']:
            header.append('Total Sin Impuestos')
        if fields['valor']:
            header.append('Impuestos')
        if fields['importeTotal']:
            header.append('Total')
        
        
        print(fields)
        global detail_of_bills
        for i in range(len(files)):
            information = str(files[i].read(),'ISO-8859-1')   
            ind1=information.index('<infoTributaria>')
            ind2=information.index('</infoAdicional>')
            information="<?xml version='1.0' encoding='ISO-8859-1'?>\n"+'<data>\n'+information[ind1:ind2+len('</infoAdicional>')]+'\n</data>\n'
            root=et.fromstring(information)
            row=[]
            for element in root.findall('infoTributaria'):
                row.append(element.find('razonSocial').text)
                row.append(element.find('ruc').text)
                row.append(element.find('estab').text+'-'+element.find('ptoEmi').text+'-'+element.find('secuencial').text)
            for element in root.findall('infoFactura'):
                row.append(element.find('fechaEmision').text)
                for x in element.findall('totalConImpuestos'):
                    for y in x.findall('totalImpuesto'):
                        row.append(y.find('baseImponible').text)
                        row.append(y.find('valor').text)
                row.append(element.find('importeTotal').text)
            print(row)
            detail_of_bills.append(row)
        return render(request,'results.html',context={'total_resume':detail_of_bills,'header':header})
    
def download_as_csv(request):
    global header
    global detail_of_bills
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="report.csv"'},
    )

    writer = csv.writer(response)
    writer.writerow(header)
    writer.writerows([detail for detail in detail_of_bills])

    return response