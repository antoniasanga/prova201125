from PIL import Image
import os

def converter_cor_gimp_para_rgb(gimp_r, gimp_g, gimp_b):
    """
    Converte valores do GIMP (0-100) para RGB (0-255)
    """
    r = int((gimp_r / 100) * 255)
    g = int((gimp_g / 100) * 255)
    b = int((gimp_b / 100) * 255)
    return (r, g, b)

def encontrar_faixa_cruz(imagem, cor_alvo=(35, 31, 32), tolerancia=15, x_inicio=1028, x_fim=1043):
    """
    Encontra posições onde há uma cruz formada por uma faixa horizontal do x_inicio ao x_fim
    e uma faixa vertical de mesma dimensão perpendicular ao centro da faixa horizontal.
    """
    largura_img, altura_img = imagem.size
    pixels = imagem.load()
    
    largura_faixa = x_fim - x_inicio + 1  # 16 pixels (1028 a 1043 inclusive)
    altura_faixa = largura_faixa          # Mesma quantidade da largura
    x_centro = x_inicio + (largura_faixa // 2) # Centro da faixa horizontal para a haste vertical
    
    posicoes_corte = []
    
    def cor_valida(pixel):
        if len(pixel) == 4:
            r, g, b, a = pixel
        else:
            r, g, b = pixel[:3]
        return (abs(r - cor_alvo[0]) <= tolerancia and 
                abs(g - cor_alvo[1]) <= tolerancia and 
                abs(b - cor_alvo[2]) <= tolerancia)

    # Percorre a imagem de cima para baixo
    y = 0
    while y < altura_img - altura_faixa:
        cruz_encontrada = True
        
        # 1. Verifica se a faixa HORIZONTAL completa (x de 1028 a 1043) é da cor alvo
        y_horizontal = y + (altura_faixa // 2)
        for x in range(x_inicio, x_fim + 1):
            if not cor_valida(pixels[x, y_horizontal]):
                cruz_encontrada = False
                break
        
        # 2. Verifica se a faixa VERTICAL completa (centro x_centro, de y a y + altura_faixa) é da cor alvo
        if cruz_encontrada:
            for dy in range(altura_faixa):
                if not cor_valida(pixels[x_centro, y + dy]):
                    cruz_encontrada = False
                    break
        
        if cruz_encontrada:
            # Corta 20 pixels ACIMA do início do padrão visual
            posicao_corte = y - 20
            if posicao_corte < 0:
                posicao_corte = 0
                
            posicoes_corte.append(posicao_corte)
            print(f"Cruz encontrada começando em y={y}, cortando em y={posicao_corte}")
            # Pula a altura da cruz para evitar detecções duplicadas
            y += altura_faixa
        else:
            y += 1
    
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_alvo):
    """
    Divide a imagem verticalmente cortando 20px antes da cruz encontrada
    """
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    # Encontra as posições das cruzes no intervalo x=1028 a 1043
    posicoes_corte = encontrar_faixa_cruz(imagem, cor_alvo)
    
    if not posicoes_corte:
        print("Nenhum padrão de cruz encontrado na imagem!")
        return
    
    print(f"Encontradas {len(posicoes_corte)} ocorrências do padrão para corte")
    
    os.makedirs(pasta_saida, exist_ok=True)
    
    posicao_anterior = 0
    
    for i, posicao_corte in enumerate(posicoes_corte):
        if posicao_corte <= posicao_anterior:
            continue
            
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        posicao_anterior = posicao_corte
    
    # Corta a seção final após o último corte
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{len(posicoes_corte)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    caminho_imagem = "colunas_concatenadas_verticalmente.png"  # Substitua pelo caminho da sua imagem
    pasta_saida = "questões divididas"          # Substitua pelo nome da pasta de saída
    
    # Define diretamente a cor RGB (35, 31, 32)
    cor_do_padrao = (35, 31, 32)
    print(f"Buscando padrão na cor RGB: {cor_do_padrao}")
    
    # Executa a divisão
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_do_padrao)
    
    print("Divisão concluída!")