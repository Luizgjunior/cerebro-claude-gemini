from PIL import Image, ImageDraw, ImageFont
import math
import struct
import io
import os

def create_nexus_icon(size):
    # Fundo transparente
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    padding = int(size * 0.1)
    center = (size // 2, size // 2)
    radius = (size // 2) - padding
    
    # Hexágono de fundo
    def get_hex_points(center, radius):
        points = []
        for i in range(6):
            angle = math.radians(60 * i - 30)
            points.append((
                center[0] + radius * math.cos(angle),
                center[1] + radius * math.sin(angle)
            ))
        return points

    hex_points = get_hex_points(center, radius)
    draw.polygon(hex_points, fill=(20, 20, 28, 255)) # Azul Profundo Quase Preto
    
    # Desenhar contorno do hexágono
    draw.polygon(hex_points, outline=(0, 200, 255, 255), width=int(size*0.02))

    # Desenhar o "N" estilizado
    n_padding_x = size * 0.3
    n_padding_y = size * 0.28
    stroke = int(size * 0.08)
    
    # Pontos do N
    p1 = (n_padding_x, size - n_padding_y) # BL
    p2 = (n_padding_x, n_padding_y)        # TL
    p3 = (size - n_padding_x, size - n_padding_y) # BR
    p4 = (size - n_padding_x, n_padding_y)        # TR
    
    # Linhas
    draw.line([p1, p2], fill=(255, 255, 255, 255), width=stroke)
    draw.line([p2, p3], fill=(0, 180, 255, 255), width=stroke)
    draw.line([p3, p4], fill=(255, 255, 255, 255), width=stroke)

    return img

def save_ico(img, path):
    sizes = [(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)]
    img.save(path, format="ICO", sizes=sizes)

base = create_nexus_icon(512)
output = r"C:\Users\Luiz\nexus.ico"
save_ico(base, output)
print(f"Icone salvo em: {output}")
