from django.shortcuts import render
import re

from .forms import XMLUploadForm



def index(request):
    return render(request,'index.html')


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
                    fechaEmision=(re.sub(pattern, '', line).lstrip()).removesuffix('\n')
                elif('baseImponible' in line):
                    baseImponible=(re.sub(pattern, '', line).lstrip()).removesuffix('\n')
                elif('valor' in line):
                    valor=(re.sub(pattern, '', line).lstrip()).removesuffix('\n')
                elif('importeTotal' in line):
                    importeTotal=(re.sub(pattern, '', line).lstrip()).removesuffix('\n')
                elif('estab' in line):
                    numFactura+=(re.sub(pattern, '', line).lstrip()).removesuffix('\n')
                elif('ptoEmi' in line):
                    numFactura+='-'+(re.sub(pattern, '', line).lstrip()).removesuffix('\n')
                elif('secuencial' in line):
                    numFactura+='-'+(re.sub(pattern, '', line).lstrip()).removesuffix('\n')
                elif('razonSocial>' in line):
                    razonSocial=(re.sub(pattern, '', line).lstrip()).removesuffix('\n')
                elif('ruc' in line):
                    ruc=(re.sub(pattern, '', line).lstrip()).removesuffix('\n')
            total_resume.insert(-1,[fechaEmision,baseImponible,valor,importeTotal,numFactura,razonSocial,ruc])
        

        
        return render(request,'results.html',context={'total_resume':total_resume})