from django.shortcuts import render

from django.http import HttpResponse
#from PyPDF2 import PdfReader
from PyPDF2 import PdfReader
import ollama
from ollama import Client
client = Client(host='http://localhost:11434')

def index(request):

    if request.method=="POST":
        form = request.FILES['myfile']
        form2 = request.FILES['myfile2']
        reader = PdfReader(form)
        texto1=""
        texto2=""
        with open('arquivo1.txt', 'w', encoding="utf-8") as f:
            for i in range(len(reader.pages)):
                f.write(reader.pages[i].extract_text())
                texto1+=reader.pages[i].extract_text()
        
        reader = PdfReader(form2)
        with open('arquivo2.txt', 'w', encoding="utf-8") as f:
            for i in range(len(reader.pages)):
                f.write(reader.pages[i].extract_text())
                texto2+=reader.pages[i].extract_text()
        
        response = client.chat(model='llama3', messages=[
        {
    'role': 'user',
    'content': 'Por favor encontre a disferenças entres esses dois textos : texto1:' + texto1 + " texto: " + texto2,
        },
        ])

        print(response['message']['content'])
        
    return render(request,'index.html')