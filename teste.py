import ollama
x = ollama.chat(model='example2', messages=[{'role': 'user', 'content': 'Why is the sky blue?'}])
print(x)