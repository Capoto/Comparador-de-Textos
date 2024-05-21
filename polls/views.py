from django.shortcuts import render

from django.http import HttpResponse
#from PyPDF2 import PdfReader
from PyPDF2 import PdfReader
import difflib
from spire.doc import *
from spire.doc.common import *
import requests
import xmltodict
import csv
import zipfile
import io
from django.conf import settings



def download_zip(l,nome):
    # create a zip file on-the-fly
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w') as zip_file:
        # add files to the zip file
        for i in l:
            zip_file.write(i)
        
    
    # create the HttpResponse object with the appropriate Content-Type header.
    response = HttpResponse(buffer.getvalue(), content_type='application/x-zip-compressed')
    # set the Content-Disposition header to force download of the file
    response['Content-Disposition'] = 'attachment;filename='+nome+".zip"
    return response 


def index(request):

    if request.method=="POST":
        form = request.FILES['myfile']
        form2 = request.FILES['myfile2']
        texto1=""
        texto2=""
        if  str(form).endswith('.pdf'):
            reader = PdfReader(form)
            
            with open('arquivo1.txt', 'w', encoding="utf-8") as f:
                for i in range(len(reader.pages)):
                    f.write(reader.pages[i].extract_text())
                    texto1+=reader.pages[i].extract_text()
        if  str(form2).endswith('.pdf'):
            reader = PdfReader(form2)
            with open('arquivo2.txt', 'w', encoding="utf-8") as f:
                for i in range(len(reader.pages)):
                    f.write(reader.pages[i].extract_text())
                    texto2+=reader.pages[i].extract_text()

        if  str(form).endswith('.docx'):
            # Create a Document object
            document = Document()
            # Load a Word document
            document.LoadFromFile(form)

            # Extract the text of the document
            document_text = document.GetText()
            texto1= document.GetText()
            # Write the extracted text into a text file
            with open("arquivo1.txt", "w", encoding="utf-8") as file:
                file.write(document_text)
        if  str(form2).endswith('.docx'):
            # Create a Document object
            document = Document()
            # Load a Word document
            document.LoadFromFile(str(form))

            # Extract the text of the document
            document_text = document.GetText()
            texto2= document.GetText()
            print(texto2)
            # Write the extracted text into a text file
            with open("arquivo1.txt", "w", encoding="utf-8") as file:
                file.write(document_text)
        
        d = difflib.HtmlDiff()
        html_diff = d.make_file(texto1.splitlines(), texto2.splitlines()) # a,b were defined earlier
        with open("diff.html", "w", encoding="utf-8") as f:
            f.write(html_diff)  
        
    return render(request,'index.html')


def plenario(request):
    lista = []
    if request.method=="POST":
        print("ok")
        data = request.POST
        action = data.get("plenariodata")
        ano = action.split('-')
        action = action.replace("-","")
        api_end_point = "https://legis.senado.leg.br/dadosabertos/plenario/lista/votacao/"+str(action)
        joke = requests.get(api_end_point)
        xpars = xmltodict.parse(joke.text)
        votos = xpars['ListaVotacoes']

        if 'Votacoes' not in votos:
            print("Não teve votação nesse dia")

        else:
            

            votos = xpars['ListaVotacoes']['Votacoes']
            cont =1

            for i in votos['Votacao']:
                api_end_point2 = "https://legis.senado.leg.br/dadosabertos/materia/"+str(i['CodigoMateria'])
                joke = requests.get(api_end_point2)
                xpars = xmltodict.parse(joke.text)
                materia =  xpars['DetalheMateria']
                sim = 0
                nao = 0
                presidente  = 0 
                abss = 0 
                pnrv=0
                desc = ""
                mtr= "Sem Ementa"
                res = ""
                secreta=""
                d= ""
                l = [] 
                orientada = []
                id = ""
                

                if 'Materia' in materia:
                    materia =  xpars['DetalheMateria']['Materia']['DadosBasicosMateria']['EmentaMateria']
                    mtr = materia
                    desc= i['DescricaoVotacao']
                    d = i['DataSessao']

                    id = i['DescricaoIdentificacaoMateria']
                    if i['Resultado']=="A":
                            res ="Aprovada"
                    else:
                        res = "Reprovada"

                    if i['Secreta']=="S":
                        secreta ="Sim"
                    else:
                        secreta = "Não"

                    for j in i['Votos']['VotoParlamentar']:
                        
                        if j['Voto']=='Sim':
                            sim+=1
                        elif j['Voto']=='Não':
                            nao+=1
                        elif j['Voto']=='P-NRV':
                            pnrv+=1
                        elif j['Voto']=='Presidente (art. 51 RISF)':
                            presidente+=1
                        else:
                            abss+=1
                        

                        
                        l.append([j['NomeParlamentar'],j['SiglaPartido'],j['SiglaUF'],j['Voto']])


                     
                   

                else:

                    desc= i['DescricaoVotacao']
                    d = i['DataSessao']
                    id = i['DescricaoIdentificacaoMateria']
                    if i['Resultado']=="A":
                            res ="Aprovada"
                    else:
                        res = "Reprovada"

                    if i['Secreta']=="S":
                        secreta ="Sim"
                    else:
                        secreta = "Não"
                    
                    for j in i['Votos']['VotoParlamentar']:
                        
                        if j['Voto']=='Sim':
                            sim+=1
                        elif j['Voto']=='Não':
                            nao+=1
                        elif j['Voto']=='P-NRV':
                            pnrv+=1
                        elif j['Voto']=='Presidente (art. 51 RISF)':
                            pnrv+=1
                        else:
                            abss+=1
                
                       
                        l.append([j['NomeParlamentar'],j['SiglaPartido'],j['SiglaUF'],j['Voto']])

                api_end_point3 = "https://legis.senado.leg.br/dadosabertos/plenario/votacao/orientacaoBancada/"+action
                joke = requests.get(api_end_point3)
                xpars = xmltodict.parse(joke.text)
                ori =  xpars['OrientacaoBancada']
                
                if 'votacoes' in ori:
                        ori = xpars['OrientacaoBancada']['votacoes']
                        flag = 0
                        for i  in  ori:
                            
                            if 'orientacoesLideranca' in i:
                                
                            
                                for j in i['orientacoesLideranca']:
                                    z = j['partido']
                                    if z=="Governo":
                                        print("teste")
                                        flag =1
                                        total = sim+nao+presidente+abss+pnrv
                                        orientada.append([d,desc,mtr,sim,nao,presidente,abss,pnrv,total,res,secreta, j['voto']])
                                        break
                                if flag==1:
                                    break
                        if flag==0:
                            total = sim+nao+presidente+abss+pnrv
                            orientada.append([d,desc,mtr,sim,nao,presidente,abss,pnrv,total,res,secreta,"SEM ORIENTAÇÃO"])

                print(cont)
                z = open("Votação "+str(cont)+ ".csv",'w+')
                print(orientada)   
                l.sort(key=lambda x:x[1])     
                with open("Votação "+str(cont)+ ".csv",'w', newline='') as csvfile:
                        writer = csv.writer(csvfile,delimiter =';')

                        # Write data for table 1
                        writer.writerow(["DataSessao",orientada[0][0]])
                      

                        # Add an empty line between tables
                        writer.writerow([])
                        
                        writer.writerow([id])
                        # Write data for table 1
                        writer.writerow([orientada[0][2]])
                        writer.writerow([orientada[0][1]])

                        # Add an empty line between tables
                        writer.writerow([])

                        # Add an empty line between tables
                        writer.writerow(["Secreta",orientada[0][-2]])

                    
                        # Add an empty line between tables
                        writer.writerow([])
                        writer.writerow(["Votos"])
                        writer.writerow(["Votos Sim",orientada[0][3]])
                        writer.writerow(["Votos Não",orientada[0][4]])
                        writer.writerow(["Abstenção",orientada[0][6]])
                        writer.writerow(["Votos do Presindente",orientada[0][5]])
                        writer.writerow(["PNRV",orientada[0][7]])
                        writer.writerow(["Total",orientada[0][8]])

                        # Add an empty line between tables
                        writer.writerow([])
                        
                        writer.writerow(["Resultado",orientada[0][-3]])
                        writer.writerow(["Orientação do Governo",orientada[0][-1]])

                        # Add an empty line between tables
                        writer.writerow([])

                        # Write data for table 2
                        writer.writerow(['NomeParlamentar','SiglaPartido','SiglaUF','Voto'])
                        writer.writerows(l)
                
                lista.append(os.path.join(settings.MEDIA_ROOT,  "Votação "+str(cont)+ ".csv"))
                cont+=1
                csvfile.close()
                z.close()
            
                
              
            return  download_zip(lista,"Plenario") 
                
    return render(request,'plenario.html')


def comissao(request):

    lista=[]
    if request.method=="POST":
       
        data = request.POST
        ini = data.get("data1")
        fim = data.get("data2")
        
        ini = ini.replace("-","")
        fim = fim.replace("-","")
        cont=1    
        print(ini,fim)

        api_end_point = "https://legis.senado.leg.br/dadosabertos/votacaoComissao/comissao/CCJ?dataInicio="+ini+"&"+"dataFim="+fim
        joke = requests.get(api_end_point)
        xpars = xmltodict.parse(joke.text)
        votos = xpars['VotacoesComissao']

        if "Votacoes" not in votos:
            print("Não teve votação nesse intervalo")

        else:
            votos = xpars['VotacoesComissao']['Votacoes']
            
            DataHoraInicioReuniao = ""
            NumeroReuniaoColegiado = ""
            TipoReuniao = ""
            NomeColegiado = ""
            IdentificacaoMateria = ""
            DescricaoIdentificacaoMateria =""
            DescricaoVotacao = ""
            
            
            for i in range(len(votos['Votacao'])):
               
                
                sim = 0
                nao = 0
                presidente  = 0 
                abss = 0 
                pnrv=0
                total = 0
                header = []
                DataHoraInicioReuniao = votos['Votacao'][i]['DataHoraInicioReuniao']
                NumeroReuniaoColegiado = votos['Votacao'][i]['NumeroReuniaoColegiado']
                TipoReuniao = votos['Votacao'][i]['TipoReuniao']
                NomeColegiado =  votos['Votacao'][i]['NomeColegiado']
                IdentificacaoMateria =  votos['Votacao'][i]['IdentificacaoMateria']
                DescricaoIdentificacaoMateria = votos['Votacao'][i]['DescricaoIdentificacaoMateria']
                DescricaoVotacao = votos['Votacao'][i]['DescricaoVotacao']

                t = votos['Votacao'][i]['IdentificacaoMateria']
                t = t.split(" ")

                sigla = t[0]

                r = t[1].split('/')
                
                codigo = r[0]
                ano = r[1]


                api_end_point2 = "https://legis.senado.leg.br/dadosabertos/materia/"+sigla+"/"+codigo+"/"+ano
                joke = requests.get(api_end_point2)
                xpars = xmltodict.parse(joke.text)
                materia = xpars['DetalheMateria']

                ementa = "Sem ementa"

                if "Materia" in  materia:
      
                    ementa = materia['Materia']['DadosBasicosMateria']['EmentaMateria']



                body = []
                

                for j in votos['Votacao'][i]['Votos']['Voto']:
                    
                    body.append([j['NomeParlamentar'],j['SiglaPartidoParlamentar'],j['QualidadeVoto']])
                horas = DataHoraInicioReuniao.split('T')
                header.append([horas[0],NumeroReuniaoColegiado,TipoReuniao,NomeColegiado,IdentificacaoMateria,DescricaoIdentificacaoMateria,DescricaoVotacao,votos['Votacao'][i]['TotalVotosSim'],votos['Votacao'][i]['TotalVotosNao'],votos['Votacao'][i]['TotalVotosAbstencao'],int(votos['Votacao'][i]['TotalVotosSim'])+int(votos['Votacao'][i]['TotalVotosNao'])+int(votos['Votacao'][i]['TotalVotosAbstencao'])])
    
                z = open("Votação "+str(cont)+ ".csv",'w+')
                body.sort(key=lambda x:x[1])    

                with open("Votação "+str(cont)+ ".csv",'w', newline='') as csvfile:
                        writer = csv.writer(csvfile,delimiter =';')

                        # Write data for table 1
                        writer.writerow([header[0][3]])
                        writer.writerow([header[0][0]])

                        # Add an empty line between tables
                        writer.writerow([])


                      
                        writer.writerow([header[0][5]])
                      
                        writer.writerow([ementa])
                       
                        writer.writerow([header[0][6]])

                        # Add an empty line between tables
                        writer.writerow([])

                        
                        writer.writerow(['Votos'])
                        writer.writerow(['Votos Sim',header[0][7]])
                        writer.writerow(['Votos Não',header[0][8]])
                        writer.writerow(['Abstenção',header[0][9]])
                        writer.writerow(['Total',header[0][10]])

                        # Add an empty line between tables
                        writer.writerow([])

                        # Write data for table 2
                        writer.writerow(['Parlamentar','Partido','Voto'])
                        writer.writerows(body)
                lista.append(os.path.join(settings.MEDIA_ROOT,  "Votação "+str(cont)+ ".csv"))
                cont+=1
                csvfile.close()
                z.close()
        return  download_zip(lista,"Comissão")
    
    return render(request,'comissao.html')