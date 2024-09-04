import csv
from django.http import HttpResponse
from django.shortcuts import render
import re
import xml.etree.ElementTree as et
import datetime


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
        
        
        global detail_of_bills
        for i in range(len(files)):
            information = str(files[i].read(),'ISO-8859-1')   
            ind1=information.index('<infoTributaria>')
            ind2=information.index('</infoAdicional>')
            information="<?xml version='1.0' encoding='ISO-8859-1'?>\n"+'<data>\n'+information[ind1:ind2+len('</infoAdicional>')]+'\n</data>\n'
            root=et.fromstring(information)
            key=''
            bill_number=''
            tax_percentaje=0

            for element in root.findall('infoTributaria'):
                key=element.find('ruc').text
                key+='| '+element.find('razonSocial').text
                if key not in output:
                    output[key]={}
                bill_number=element.find('estab').text+'-'+element.find('ptoEmi').text+'-'+element.find('secuencial').text
                output[key][bill_number] = {}
                
            for element in root.findall('infoFactura'):
                date=element.find('fechaEmision').text
                date_splitted= date.split('/')
                if(datetime.datetime(year=int(date_splitted[2]),month=int(date_splitted[1]),day=int(date_splitted[0]))>= datetime.datetime(year=2024,month=4,day=1)):
                    tax_percentaje = 0.15
                else:
                    tax_percentaje =0.12
                output[key][bill_number]['Fecha de Emisión']=date
                output[key][bill_number]['Dirección del Establecimiento']=element.find('dirEstablecimiento').text
                total_out_of_taxes=float(element.find('totalSinImpuestos').text)
                total_of_taxes=round(total_out_of_taxes*tax_percentaje,2)
                output[key][bill_number]['Total sin Impuestos']=total_out_of_taxes
                output[key][bill_number]['Total en Impuestos']=total_of_taxes
                output[key][bill_number]['Total']=total_of_taxes+total_out_of_taxes
            index=0    
            output[key][bill_number]['Detalles']={}
            for detalle in root.findall('detalles'):
                for element in detalle.findall('detalle'):
                    output[key][bill_number]['Detalles'][index]={}
                    output[key][bill_number]['Detalles'][index]['Descripción']=element.find('descripcion').text
                    output[key][bill_number]['Detalles'][index]['Cantidad']=element.find('cantidad').text
                    for impuesto in element.findall('impuestos'):
                        for detalle_impuesto in impuesto.findall('impuesto'):
                            total_out_of_taxes=float(detalle_impuesto.find('baseImponible').text)
                            total_of_taxes=float(detalle_impuesto.find('valor').text)
                            output[key][bill_number]['Detalles'][index]['Total sin Impuestos'] = round(total_out_of_taxes,2)
                            output[key][bill_number]['Detalles'][index]['Total en Impuestos'] = round(total_of_taxes,2)
                            output[key][bill_number]['Detalles'][index]['Valor final'] = round(total_of_taxes+total_out_of_taxes,2)
                    index += 1
        return render(request,'results.html',
                      context = {
                          'output':output,
                          })
    
def download_as_csv(request):
    global output
    bills_detail = []
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