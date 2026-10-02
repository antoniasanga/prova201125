from PIL import Image
import os

def encontrar_faixa_alvo(imagem, cor_alvo, tolerancia=15, altura_faixa=1):
    """
    Encontra posições onde há uma faixa horizontal da cor especificada entre os pixels X 1028 e 1043.
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    posicoes_corte = []
    
    # Intervalo do eixo X conforme especificado
    x_inicio = 1028
    x_fim = 1043
    
    # Garantir que o intervalo de X não ultrapasse os limites da imagem
    if x_fim >= largura:
        x_fim = largura - 1
    
    # Percorre a imagem de cima para baixo
    y = 0
    while y < altura - altura_faixa:
        # Verifica se todos os pixels na faixa horizontal (x_inicio até x_fim) possuem a cor alvo
        faixa_encontrada = True
        
        for x in range(x_inicio, x_fim + 1):
            pixel = pixels[x, y]
            
            if len(pixel) == 4:  # RGBA
                r, g, b, a = pixel
            else:  # RGB
                r, g, b = pixel[:3]
            
            # Verifica se a cor está dentro da tolerância
            if (abs(r - cor_alvo[0]) > tolerancia or 
                abs(g - cor_alvo[1]) > tolerancia or 
                abs(b - cor_alvo[2]) > tolerancia):
                faixa_encontrada = False
                break
        
        if faixa_encontrada:
            # Corta 20 pixels ACIMA da faixa encontrada
            posicao_corte = y - 20
            if posicao_corte < 0:  # Evita posições negativas
                posicao_corte = 0
                
            posicoes_corte.append(posicao_corte)
            print(f"Faixa encontrada em y={y}, cortando em y={posicao_corte}")
            
            # Pula alguns pixels para evitar detecções múltiplas do mesmo padrão
            y += max(altura_faixa, 10)
        else:
            y += 1
    
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_alvo):
    """
    Divide a imagem verticalmente cortando nas posições identificadas
    """
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    posicoes_corte = encontrar_faixa_alvo(imagem, cor_alvo)
    
    if not posicoes_corte:
        print("Nenhuma faixa da cor informada foi encontrada no intervalo especificado!")
        return
    
    print(f"Encontradas {len(posicoes_corte)} faixas para corte")
    
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
    
    # Corta a seção final (após a última faixa)
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{len(posicoes_corte)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    caminho_imagem = "colunas_concatenadas_verticalmente.png"  # Substitua pelo nome da sua imagem
    pasta_saida = "questões dividas"           # Substitua pela pasta de saída desejada

    # Cor RGB (35, 31, 32) diretamente especificada
    cor_do_padrao = (35, 31, 32)
    print(f"Procurando pela cor RGB: {cor_do_padrao}")
    
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_do_padrao)
    
    print("Divisão concluída!")