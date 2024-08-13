import csv
from django.http import HttpResponse
from django.shortcuts import render
import re

from .forms import XMLUploadForm

header=['Fecha','Numero de factura','Razon Social','RUC','Total Sin Impuestos','Impuestos','Total']
detail_of_bills=[]

def index(request):
    global detail_of_bills
    detail_of_bills=[]
    return render(request,'index.html')

def extract_data_from_line(line, pattern):
    return re.sub(pattern, '', line).strip().rstrip('\n')

def results(request):
    if request.method == 'POST':
        files = request.FILES.getlist('myfiles')
        fields={
            'fechaEmision':True,
            'baseImponible':True,
            'valor':False,
            'importeTotal':True,
            'estab':False,
            'ptoEmi':False,
            'secuencial':False,
            'razonSocial>':True,
            'ruc':False
            }
        if('show-bill-number-option' in request.POST):
            fields['estab']=True
            fields['ptoEmi']=True
            fields['secuencial']=True
        if('show-ruc-option' in request.POST):
            fields['ruc']=True
        if('show-total-out-of-taxes-option' not in request.POST):
            fields['baseImponible']=False
        if('show-total-taxes-option' in request.POST):
            fields['valor']=True
        print(fields)
        global detail_of_bills
        pattern = re.compile('<.*?>')
        for i in range(len(files)):
            archive= str(files[i].read(),'ISO-8859-1').split('\r\n')
            row=[]
            for line in archive:
                for key,value in fields.items():
                    if (key in line and value):
                        if(key=='ptoEmi' or key=='secuencial'):
                            row[-1]+='-'+extract_data_from_line(line,pattern)
                        row.append(extract_data_from_line(line,pattern))
            detail_of_bills.insert(-1,row)
        

        
        return render(request,'results.html',context={'total_resume':detail_of_bills})
    
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