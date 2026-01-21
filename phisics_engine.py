import taichi as ti
import numpy as np
from PIL import Image, ImageOps, ImageFilter
import os
import tkinter as tk
from tkinter import filedialog
import sys

# --- 1. SISTEMA DE DETECÇÃO ---
def iniciar_motor_grafico():
    print(">> Detectando Hardware...")
    try:
        ti.init(arch=ti.gpu, offline_cache=True)
        print(">> SUCESSO: GPU Detectada e Ativada!")
    except Exception as e:
        print(f">> AVISO: Falha na GPU ({e}). Tentando CPU...")
        try:
            ti.init(arch=ti.cpu)
        except:
            sys.exit(1)

iniciar_motor_grafico()

# --- SEGURADOR DE ERRO ---
def show_exception_and_exit(exc_type, exc_value, tb):
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    input("\nPressione ENTER para fechar...")
    sys.exit(-1)
sys.excepthook = show_exception_and_exit

# --- 2. CONFIGURAÇÕES ---
RES_X = 600
RES_Y = 600
C = 340
DX = 0.15            
DT = 0.00025         
DAMPING = 0.995      
VISUAL_GAIN = 5.0

# --- 3. CAMPOS DE DADOS ---
u = ti.field(dtype=ti.f32, shape=(RES_X, RES_Y))
u_prev = ti.field(dtype=ti.f32, shape=(RES_X, RES_Y))
u_temp = ti.field(dtype=ti.f32, shape=(RES_X, RES_Y)) 
pixels = ti.Vector.field(3, dtype=ti.f32, shape=(RES_X, RES_Y)) 

# MUDANÇA CRÍTICA: 'walls' agora é um ndarray (Memória Bruta)
# Isso permite carregar do Numpy sem compilar kernel (evita crash e lentidão)
walls = ti.ndarray(dtype=ti.f32, shape=(RES_X, RES_Y))

# --- 4. CARREGAMENTO ULTRA-RÁPIDO ---
def carregar_planta_numpy():
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        caminho = filedialog.askopenfilename(
            title="Selecione Planta Baixa",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.bmp")]
        )
        root.destroy()
        
        if not caminho: return None
        
        print(f"Carregando: {caminho}")
        img = Image.open(caminho).convert("L")
        img = ImageOps.autocontrast(img, cutoff=5)
        img = img.resize((RES_Y, RES_X), resample=Image.Resampling.LANCZOS)
        img = img.filter(ImageFilter.MinFilter(3))
        
        data = np.asarray(img, dtype=np.float32) / 255.0
        data = data.T 
        
        # Processa na CPU
        processed = np.where(data < 0.7, 0.0, 1.0).astype(np.float32)
        return processed
    except Exception as e:
        print(f"Erro ao carregar: {e}")
        return None

# Carregamento
dados_parede = carregar_planta_numpy()

if dados_parede is not None:
    print(">> Transferindo para GPU (Direto)...")
    # Copia direta de memória C++ (Instantâneo e sem Crash)
    walls.from_numpy(dados_parede)
    print(">> Pronto!")
else:
    # Preenche com 1.0 (Ar) manualmente se falhar
    import numpy as np
    dummy = np.ones((RES_X, RES_Y), dtype=np.float32)
    walls.from_numpy(dummy)

# --- 5. KERNELS DE FÍSICA ---
# Precisamos passar 'walls' como argumento pois agora é ndarray
@ti.kernel
def update_physics(walls_arr: ti.types.ndarray(ndim=2)):
    courant_sq = (C * DT / DX)**2
    for i, j in u:
        if i > 0 and i < RES_X - 1 and j > 0 and j < RES_Y - 1:
            laplacian = (u[i+1, j] + u[i-1, j] + u[i, j+1] + u[i, j-1] - 4 * u[i, j])
            val = (2.0 * u[i, j] - u_prev[i, j] + courant_sq * laplacian) * DAMPING
            # Acessa o ndarray passado como argumento
            u_temp[i, j] = val * walls_arr[i, j]

@ti.kernel
def apply_update():
    for i, j in u:
        u_prev[i, j] = u[i, j]
        u[i, j] = u_temp[i, j]

@ti.kernel
def render_field(walls_arr: ti.types.ndarray(ndim=2)):
    for i, j in pixels:
        if walls_arr[i, j] == 0.0:
            pixels[i, j] = ti.Vector([0.3, 0.3, 0.3])
        else:
            val = u[i, j] * VISUAL_GAIN
            color = ti.Vector([0.0, 0.0, 0.0])
            if val > 0:
                color[0] = ti.min(val, 1.0) 
                if val > 0.8:
                     color[1] = ti.min((val - 0.8)*2, 1.0)
                     color[2] = ti.min((val - 0.8)*2, 1.0)
            elif val < 0:
                color[2] = ti.min(-val, 1.0)
                if val < -0.8:
                     color[0] = ti.min((-val - 0.8)*2, 1.0)
                     color[1] = ti.min((-val - 0.8)*2, 1.0)
            pixels[i, j] = color

@ti.kernel
def click_event(x: ti.f32, y: ti.f32):
    ix = int(x * RES_X)
    iy = int(y * RES_Y)
    for i in range(ix-3, ix+3):
        for j in range(iy-3, iy+3):
             if i > 0 and i < RES_X and j > 0 and j < RES_Y:
                 u[i, j] = 10.0
                 u_prev[i, j] = 10.0

# --- 6. GUI LOOP ---
gui = ti.GUI("Simulador Acústico (Final v4)", res=(RES_X, RES_Y), fast_gui=True)
print(">> Simulador Pronto.")

while gui.running:
    if gui.get_event(ti.GUI.PRESS):
        if gui.event.key == ti.GUI.LMB:
            x, y = gui.get_cursor_pos()
            click_event(x, y)
        elif gui.event.key == ti.GUI.ESCAPE:
            gui.running = False

    for _ in range(20):
        # Passamos 'walls' como argumento aqui
        update_physics(walls)
        apply_update()
    
    # Passamos 'walls' como argumento aqui também
    render_field(walls)
    gui.set_image(pixels)
    gui.show()