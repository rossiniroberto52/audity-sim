# 🚀 Acoustic Simulator v3.1 - GPU Turbo Edition

> **"De 5 FPS chorando na CPU para 60+ FPS voando na GPU"**

Esta versão marca uma reescrita completa do motor de física. Deixamos para trás o `matplotlib` e adotamos o **Taichi Lang**, permitindo que a simulação da equação da onda rode diretamente na placa de vídeo (GPU).

Agora, o simulador é **Universal**: ele detecta automaticamente o seu hardware e escolhe o melhor backend (CUDA, Vulkan ou OpenGL), garantindo compatibilidade tanto para NVIDIA quanto para AMD (e até Intel integrada).

---

## ✨ Novidades Principais

### 🏎️ Aceleração via GPU (Taichi)
- **Performance Extrema:** O cálculo físico (FDTD) agora é paralelo. O que antes travava um i7 agora nem faz cócegas numa RX 580.
- **Backend Híbrido:**
  - 🟢 **NVIDIA:** Usa CUDA automaticamente.
  - 🔴 **AMD:** Usa Vulkan (testado e aprovado na RX 580).
  - 🔵 **CPU Fallback:** Se não houver GPU, ele roda na CPU de forma otimizada.

### 🎨 Visualização & Renderização
- **Novo Renderizador RGB:** Visualização de pressão acústica em tempo real (Vermelho = Pressão Alta, Azul = Pressão Baixa).
- **GUI Nativa:** Substituição da janela do Matplotlib pela GUI do Taichi (muito mais rápida e responsiva).

### 🏗️ Importação de Plantas Inteligente
- **Auto-Contraste:** Importe desenhos a lápis ou plantas claras e o sistema converte para binário (Parede/Ar) automaticamente.
- **Espessamento de Paredes:** Filtro de erosão aplicado automaticamente para evitar que o som "vaze" por paredes desenhadas muito finas.

---

## 🛠️ Correções Técnicas & Fixes

- **⚡ Carregamento Instantâneo:** Implementação de uma "Ponte NDArray" para transferir a imagem da planta (CPU) para a memória da GPU sem travar a inicialização.
- **🐛 Fix do PyInstaller + Taichi JIT:**
  - Resolvido o problema crítico onde o executável crashava com `OSError: could not get source code`.
  - **Solução:** Arquitetura de "Launcher" (`main.py`) que carrega o motor físico (`motor_fisico.py`) dinamicamente, permitindo que o compilador JIT acesse o código fonte mesmo dentro de um ambiente congelado.

---

## 📦 Como Usar (Para Devs)

Certifique-se de ter as dependências instaladas:

```bash
pip install taichi numpy pillow
```
## 🔧 Build (Gerando o Executável)
Se você deseja compilar este projeto, utilize o seguinte comando para garantir que o motor de física seja empacotado corretamente:
```bash
pyinstaller --noconfirm --onefile --windowed --collect-all taichi --add-data "phisics_engine.py;." --icon "ico.ico" --name "audity_sim_v4.1" main.py
```

## ❤️ Agradecimentos
Um agradecimento especial à minha RX 580 por aguentar os testes de estresse e à documentação do Taichi por existir.

Desenvolvido com muito café e álgebra linear. ☕📐
