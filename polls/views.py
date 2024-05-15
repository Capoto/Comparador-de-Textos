from django.shortcuts import render

from django.http import HttpResponse
#from PyPDF2 import PdfReader
from PyPDF2 import PdfReader
import ollama
import difflib
from spire.doc import *
from spire.doc.common import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
import requests
import json 
import xml.etree.ElementTree as ET
import xmltodict
import seaborn as sns
from operator import itemgetter
from collections import OrderedDict
import fpdf
from fpdf import FPDF, HTMLMixin
import plotly.figure_factory as ff
from IPython.display import HTML
import csv


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
                l = [] 
                orientada = []
                

                if 'Materia' in materia:
                    materia =  xpars['DetalheMateria']['Materia']['DadosBasicosMateria']['EmentaMateria']
                    mtr = materia
                    desc= i['DescricaoVotacao']
                    d = i['DataSessao']
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
                        

                        
                        l.append([d,j['NomeParlamentar'],j['SiglaPartido'],j['SiglaUF'],j['Voto']])


                     
                   

                else:

                    desc= i['DescricaoVotacao']
                    d = i['DataSessao']
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
                
                       
                        l.append([d,j['NomeParlamentar'],j['SiglaPartido'],j['SiglaUF'],j['Voto']])

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
                                        orientada.append([desc,mtr,sim,nao,presidente,abss,pnrv,total,res,secreta, j['voto']])
                                        break
                                if flag==1:
                                    break
                        if flag==0:
                            total = sim+nao+presidente+abss+pnrv
                            orientada.append([desc,mtr,sim,nao,presidente,abss,pnrv,total,res,secreta,"SEM ORIENTAÇÃO"])

                print(cont)
                z = open("Votação "+str(cont)+ ".csv",'w+')
                        
                with open("Votação "+str(cont)+ ".csv",'w', newline='') as csvfile:
                        writer = csv.writer(csvfile,delimiter =';')

                        # Write data for table 1
                        writer.writerow(['Descricao Votacao','Ementa','Votos Sim','Votos Não',"Votos do Presindente","Abstenção","PNRV","Total","Resultado","Secreta","Orientação do Governo"])
                        writer.writerows(orientada)

                        # Add an empty line between tables
                        writer.writerow([])

                        # Write data for table 2
                        writer.writerow(['DataSessao','NomeParlamentar','SiglaPartido','SiglaUF','Voto'])
                        writer.writerows(l)
                cont+=1
                csvfile.close()
                z.close()

             
                
    return render(request,'plenario.html')


def comissao(request):

    if request.method=="POST":
        print("ok")
        
    return render(request,'comissao.html')