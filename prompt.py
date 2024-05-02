import ollama
modelfile='''
FROM llama3
SYSTEM Você um revisor de texto que procura as diferenças entre dois textos caso ache você que tem que informa quais linhas forma mudadas
'''

ollama.create(model='example2', modelfile=modelfile)
