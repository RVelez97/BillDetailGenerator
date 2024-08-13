import csv
from django.http import HttpResponse
from django.shortcuts import render
import re

from .forms import XMLUploadForm
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
        pattern = re.compile('<.*?>')
        for i in range(len(files)):
            archive= str(files[i].read(),'ISO-8859-1').split('\r\n')
            row=[]
            flag_base_imponible=False
            flag_valor=False
            for line in archive:
                for key,value in fields.items():
                    if ((key in line) and value):
                        if(key=='ptoEmi' or key=='secuencial'):
                            row[-1]+=f'-{extract_data_from_line(line,pattern)}'
                        elif(key=='baseImponible'):
                            if(not flag_base_imponible):
                                row.append(extract_data_from_line(line,pattern))
                            flag_base_imponible=True
                        elif(key=='valor'):
                            if(not flag_valor):
                                row.append(extract_data_from_line(line,pattern))
                            flag_valor=True
                        else:
                            row.append(extract_data_from_line(line,pattern))
            detail_of_bills.insert(-1,row)
        

        
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