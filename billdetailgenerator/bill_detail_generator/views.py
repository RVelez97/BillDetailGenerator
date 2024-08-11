import csv
from django.http import HttpResponse
from django.shortcuts import render
import re

from .forms import XMLUploadForm

header=['Fecha','Total Sin Impuestos','Impuestos','Total','Numero de factura','Razon Social','RUC']
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
        global detail_of_bills
        pattern = re.compile('<.*?>')
        for i in range(len(files)):
            archive= str(files[i].read(),'ISO-8859-1').split('\r\n')
            fechaEmision = ''
            baseImponible = ''
            valor = ''
            importeTotal = ''
            numFactura=''
            razonSocial=''
            ruc = ''
            for line in archive:
                if('fechaEmision' in line):
                    fechaEmision=extract_data_from_line(line,pattern)
                elif('baseImponible' in line):
                    baseImponible=extract_data_from_line(line,pattern)
                elif('valor' in line):
                    valor=extract_data_from_line(line,pattern)
                elif('importeTotal' in line):
                    importeTotal=extract_data_from_line(line,pattern)
                elif('estab' in line):
                    numFactura+=extract_data_from_line(line,pattern)
                elif('ptoEmi' in line):
                    numFactura+='-'+extract_data_from_line(line,pattern)
                elif('secuencial' in line):
                    numFactura+='-'+extract_data_from_line(line,pattern)
                elif('razonSocial>' in line):
                    razonSocial=extract_data_from_line(line,pattern)
                elif('ruc' in line):
                    ruc=(re.sub(pattern, '', line).lstrip()).removesuffix('\n')
            detail_of_bills.insert(-1,[fechaEmision,baseImponible,valor,importeTotal,numFactura,razonSocial,ruc])
        

        
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