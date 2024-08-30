import csv
from django.http import HttpResponse
from django.shortcuts import render
import re
import xml.etree.ElementTree as et


output ={}

def index(request):
    global output
    output ={}
    return render(request,'index.html')

def extract_data_from_line(line, pattern):
    return re.sub(pattern, '', line).strip().rstrip('\n')

def results(request):
    if request.method == 'POST':
        global output
        files = request.FILES.getlist('myfiles')
        fields={
            'fechaEmision':True,
            'estab':False,
            'ptoEmi':False,
            'secuencial':False,
            'razonSocial':True,
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
        
        global detail_of_bills
        for i in range(len(files)):
            information = str(files[i].read(),'ISO-8859-1')   
            ind1=information.index('<infoTributaria>')
            ind2=information.index('</infoAdicional>')
            information="<?xml version='1.0' encoding='ISO-8859-1'?>\n"+'<data>\n'+information[ind1:ind2+len('</infoAdicional>')]+'\n</data>\n'
            root=et.fromstring(information)
            key=''
            for element in root.findall('infoTributaria'):
                if fields['ruc']:
                    key=element.find('ruc').text
                if fields['razonSocial']:
                    key+='| '+element.find('razonSocial').text
                    if key not in output:
                        output[key]={}
                if fields['estab']:
                    bill_number=element.find('estab').text+'-'+element.find('ptoEmi').text+'-'+element.find('secuencial').text
                    output[key][bill_number]={}
                

                
            for element in root.findall('infoFactura'):
                if fields['fechaEmision']:
                    output[key][bill_number]['Fecha de Emisión']=element.find('fechaEmision').text
                for x in element.findall('totalConImpuestos'):
                    for y in x.findall('totalImpuesto'):
                        if fields['baseImponible']:
                            output[key][bill_number]['Total sin Impuestos']=y.find('baseImponible').text
                        if fields['valor']:
                            output[key][bill_number]['Total en Impuestos']=y.find('valor').text
                if fields['importeTotal']:
                    output[key][bill_number]['Total']=element.find('importeTotal').text
        return render(request,'results.html',context={'output':output})
    
def download_as_csv(request):
    global output
    bills_detail=[]
    for company_info,content in output.items():
        for bill_number,details in content.items():
            r=[company_info,bill_number]
            for detail in details.values():
                r.append(detail)
            bills_detail.append(r)
                
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="report.csv"'},
    )

    writer = csv.writer(response)
    writer.writerows([detail for detail in bills_detail])

    return response