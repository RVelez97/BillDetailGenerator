from django.shortcuts import render
import re

from .forms import XMLUploadForm



def index(request):
    return render(request,'index.html')

def extract_data_from_line(line, pattern):
    return re.sub(pattern, '', line).strip().rstrip('\n')

def results(request):
    if request.method == 'POST':
        files = request.FILES.getlist('myfiles')
        total_resume=[]
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
                    ruc=extract_data_from_line(line,pattern)
            total_resume.insert(-1,[fechaEmision,numFactura,razonSocial,ruc,baseImponible,valor,importeTotal])
        

        
        return render(request,'results.html',context={'total_resume':total_resume})