import sys
import os
import importlib.util

# --- IMPORTAÇÕES FANTASMAS ---
# Isso serve apenas para avisar o PyInstaller que ele PRECISA 
# incluir essas bibliotecas no EXE final.
import taichi 
import numpy 
import PIL 
import tkinter 

def resource_path(relative_path):
    """ Retorna o caminho absoluto do recurso, funcione em Dev ou EXE """
    try:
        # PyInstaller cria uma pasta temporária em _MEIxxxx
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def carregar_motor():
    # O arquivo motor_fisico.py será empacotado JUNTOS com o exe
    script_path = resource_path("phisics_engine.py")
    
    print(f">> Inicializando Motor Taichi a partir de: {script_path}")
    
    # Carregamento Dinâmico (A Mágica)
    # Isso faz o Python ler o ARQUIVO DE TEXTO, permitindo que o Taichi
    # acesse o código fonte para compilar os kernels da GPU.
    spec = importlib.util.spec_from_file_location("motor_modulo", script_path)
    if spec and spec.loader:
        modulo = importlib.util.module_from_spec(spec)
        sys.modules["motor_modulo"] = modulo
        spec.loader.exec_module(modulo)
    else:
        print("ERRO CRÍTICO: Não foi possível carregar motor_fisico.py")
        input("Enter para sair...")

if __name__ == "__main__":
    # Proteção para multiprocessing (obrigatório em Windows)
    import multiprocessing
    multiprocessing.freeze_support()
    carregar_motor()