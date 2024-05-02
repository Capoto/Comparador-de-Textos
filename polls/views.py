from django.shortcuts import render

from django.http import HttpResponse
#from PyPDF2 import PdfReader
from PyPDF2 import PdfReader
import ollama


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
        
        
        f1 = open("arquivo1.txt", "r")  
        f2 = open("arquivo2.txt", "r")  
 
        f1_data = f1.readlines()
        f2_data = f2.readlines()


        if len(f1_data) > len(f2_data):

            for i in range(len(f2_data)):
                if f1_data[i]==f2_data[i]:
                    print("same")
                else:
                    print("Line "+str(i))
                    print(f1_data[i])
                    print(f2_data[i])
                    

            for i in range(len(f2_data),len(f1_data)):
                
                print("Line "+str(i))
                print(f1_data[i])
        else:
            for i in range(len(f1_data)):
                if f1_data[i]==f2_data[i]:
                    print("same")
            
            for i in range(len(f1_data),len(f2_data)):
                
                print("Line "+str(i))
                print(f2_data[i])
                print(f1_data[i])

        
        f1.close()                                       
        f2.close()
        
        '''
        i = 0
 
        for line1 in f1_data:
            i += 1
     
            for line2 in f2_data:
         
                # matching line1 from both files
                if line1 == line2:  
                    # print IDENTICAL if similar
                    print("Line ", i, ": IDENTICAL")       
                else:
                    print("Line ", i, ":")
                    # else print that line from both files
                    print("\tFile 1:", line1, end='')
                    print("\tFile 2:", line2, end='')
       
 
   
        f1.close()                                       
        f2.close()
        '''  
        
    return render(request,'index.html')