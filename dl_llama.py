import urllib.request, zipfile, os
url = 'https://github.com/ggml-org/llama.cpp/releases/download/b9664/llama-b9664-bin-win-cuda-cu13.1-x64.zip'
print('DL llama.cpp...', flush=True)
urllib.request.urlretrieve(url, 'C:/NeuraNode/llama.zip')
print('Extracting...', flush=True)
with zipfile.ZipFile('C:/NeuraNode/llama.zip') as z:
    z.extractall('C:/NeuraNode/llama/')
os.remove('C:/NeuraNode/llama.zip')
bins = [f for f in os.listdir('C:/NeuraNode/llama/') if f.endswith('.exe')]
print('OK:', bins, flush=True)
