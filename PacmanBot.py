import pygame
import sys
import os
import time
import random
from collections import deque

pygame.init()

# Parámetros del juego
ANCHO, ALTO = 560, 620
TAM_CELDA = 20
FPS = 10

# Colores
NEGRO = (0, 0, 0)
AZUL = (33, 33, 255)
AMARILLO = (255, 255, 0)
BLANCO = (255, 255, 255)
ROJO = (255, 0, 0)

# Carpeta de rendimiento
ruta_performance = 'PacmanLab/performance'
os.makedirs(ruta_performance, exist_ok=True)

# Crear ventana
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Pac-Man IA con 2 Fantasmas Aleatorios")
reloj = pygame.time.Clock()

# Cargar imagen de Pac-Man (frames de la animación)
nombre_imagen = 'Pacman.png'
sheet = pygame.image.load(os.path.join('images', nombre_imagen)).convert_alpha()
w, h = sheet.get_width() // 8, sheet.get_height()
frames = []
for i in range(8):
    f = pygame.Surface((w, h), pygame.SRCALPHA)
    f.blit(sheet, (0, 0), (i * w, 0, w, h))
    frames.append(pygame.transform.scale(f, (TAM_CELDA, TAM_CELDA)))

frame, cont, vel = 0, 0, -8

# Cargar imagen de Fantasma
fantasma_imagen = 'redGhost.png'
sheet_fantasma = pygame.image.load(os.path.join('images', fantasma_imagen)).convert_alpha()
# Suponiendo que la hoja de sprites tiene 4 frames de animación (uno para cada dirección)
w_fantasma, h_fantasma = sheet_fantasma.get_width() // 8, sheet_fantasma.get_height()
frames_fantasma = []

# Cortar los frames de la hoja de sprites
for i in range(8):
    f = pygame.Surface((w_fantasma, h_fantasma), pygame.SRCALPHA)
    f.blit(sheet_fantasma, (0, 0), (i * w_fantasma, 0, w_fantasma, h_fantasma))
    frames_fantasma.append(pygame.transform.scale(f, (TAM_CELDA, TAM_CELDA)))


mapa_facil = [
"1111111111111111111",
"1000000000000000001",
"1011110111110111101",
"1011110111110111101",
"1000000000000000001",
"1110111111111110111",
"1000100000000010001",
"1011101110111011101",
"1000001000001000001",
"1111101110111011111",
"1111100000000011111",
"1000001110111000001",
"1011100000000011101",
"1011111110111111101",
"1000000000000000001",
"1111111111111111111"
]

mapa = [list(fila) for fila in mapa_facil]
FILAS, COLUMNAS = len(mapa), len(mapa[0])

# Posiciones iniciales
pacman_x, pacman_y = 1, 1
pacman_dir = "R"  # dirección inicial de Pac-Man (derecha)
dir_fantasma = "R"

# Generar fantasmas en posiciones aleatorias válidas
def generar_fantasma():
    while True:
        x = random.randint(1, COLUMNAS - 2)
        y = random.randint(1, FILAS - 2)
        if mapa[y][x] != '1' and (x, y) != (pacman_x, pacman_y):
            return (x, y)

fantasmas = [generar_fantasma() for _ in range(2)]  # solo 2 fantasmas

# Contadores
puntos_totales = sum(f.count('0') for f in mapa)
puntos_recolectados = 0
muertes = 0
zonas_peligrosas = set()

# --- FUNCIONES ---
def dibujar_mapa():
    for y, fila in enumerate(mapa):
        for x, celda in enumerate(fila):
            if celda == '1':
                pygame.draw.rect(pantalla, AZUL, (x * TAM_CELDA, y * TAM_CELDA, TAM_CELDA, TAM_CELDA))
            elif celda == '0':
                pygame.draw.circle(pantalla, BLANCO, (x * TAM_CELDA + TAM_CELDA // 2, y * TAM_CELDA + TAM_CELDA // 2), 3)



def vecinos(x, y, evitar_peligro=True):
    candidatos = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]

    def es_valido(nx, ny):
        if not (0 <= nx < COLUMNAS and 0 <= ny < FILAS):
            return False
        if mapa[ny][nx] == '1':
            return False
        if evitar_peligro and (nx, ny) in zonas_peligrosas:
            return False
        return True

    validos = [(nx, ny) for nx, ny in candidatos if es_valido(nx, ny)]

    # Reintentar sin evitar peligros si no hay caminos válidos
    if evitar_peligro and not validos:
        return vecinos(x, y, evitar_peligro=False)

    return validos


def bfs(origen, destino, evitar_peligro=True):
    cola = deque([origen])
    visitados = {origen: None}

    while cola:
        actual = cola.popleft()
        if actual == destino:
            # Reconstruir camino hacia atrás
            camino = []
            while actual:
                camino.append(actual)
                actual = visitados[actual]
            return camino[::-1]

        for vecino in vecinos(*actual, evitar_peligro):
            if vecino not in visitados:
                visitados[vecino] = actual
                cola.append(vecino)

    return None


def encontrar_punto_mas_cercano(x, y):
    cola = deque([(x, y)])
    visitados = {(x, y)}

    while cola:
        cx, cy = cola.popleft()
        if mapa[cy][cx] == '0':
            return (cx, cy)

        for nx, ny in vecinos(cx, cy, evitar_peligro=False):
            if (nx, ny) not in visitados:
                visitados.add((nx, ny))
                cola.append((nx, ny))

    return None




# --- MÉTRICAS ---
inicio_tiempo = time.time()
pasos_totales = 0
camino_actual = []
indice_camino = 0
tick_fantasma = 0

# --- LOOP PRINCIPAL ---
ejecutando = True

while ejecutando:
    reloj.tick(FPS)
    tick_fantasma += 1
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


    # Movimiento Pac-Man
    if not camino_actual:
        objetivo = encontrar_punto_mas_cercano(pacman_x, pacman_y)
        if objetivo:
            camino_actual = bfs((pacman_x, pacman_y), objetivo)
            if camino_actual is None:
                camino_actual = bfs((pacman_x, pacman_y), objetivo, evitar_peligro=False)
            indice_camino = 0
        else:
            continue  # espera un tick y vuelve a intentar



    if camino_actual and indice_camino < len(camino_actual):
        pacman_x, pacman_y = camino_actual[indice_camino]
        indice_camino += 1
        pasos_totales += 1

        if mapa[pacman_y][pacman_x] == '0':
            mapa[pacman_y][pacman_x] = ' '
            puntos_recolectados += 1

    # Asegúrate de que `indice_camino` esté dentro del rango del camino
    if indice_camino < len(camino_actual):
        siguiente_x, siguiente_y = camino_actual[indice_camino]

        # Actualizar la dirección de Pac-Man según la diferencia de posiciones
        if pacman_x < siguiente_x:
            pacman_dir = "R"  # Movimiento a la derecha
        elif pacman_x > siguiente_x:
            pacman_dir = "L"  # Movimiento a la izquierda
        elif pacman_y < siguiente_y:
            pacman_dir = "D"  # Movimiento hacia abajo
        elif pacman_y > siguiente_y:
            pacman_dir = "U"  # Movimiento hacia arriba

    else:
        camino_actual = []

    # Movimiento fantasmas cada 5 ticks
    if tick_fantasma % 5 == 0:
        nuevos_fantasmas = []
        for fx, fy in fantasmas:
            camino_f = bfs((fx, fy), (pacman_x, pacman_y), evitar_peligro=False)
            if camino_f and len(camino_f) > 1:
                fx, fy = camino_f[1]
            nuevos_fantasmas.append((fx, fy))
        fantasmas = nuevos_fantasmas

    # Detectar colisiones con fantasmas
    for fx, fy in fantasmas:
        if (fx, fy) == (pacman_x, pacman_y):
            muertes += 1
            zonas_peligrosas.add((pacman_x, pacman_y))
            pacman_x, pacman_y = 1, 1
            camino_actual = []
            print(f"Pac-Man fue atrapado! Muertes: {muertes}")
            break  # solo manejar una colisión por tick

    # --- DIBUJAR ---
    pantalla.fill(NEGRO)
    dibujar_mapa()

    # Animar Pac-Man según su dirección

    cont += 1
    if cont >= vel:
        frame = (frame + 1) % len(frames)  # Avanzar al siguiente fotograma
        cont = 0

    img = frames[frame]
    if pacman_dir == "L":
        img = pygame.transform.flip(img, True, False)  # Voltear horizontalmente (izquierda)
    elif pacman_dir == "U":
        img = pygame.transform.rotate(img, 90)  # Rotar 90 grados (arriba)
    elif pacman_dir == "D":
        img = pygame.transform.rotate(img, -90)  # Rotar -90 grados (abajo)



    # Mostrar imagen de Pac-Man
    rect = img.get_rect(center=(pacman_x * TAM_CELDA + TAM_CELDA // 2, pacman_y * TAM_CELDA + TAM_CELDA // 2))
    pantalla.blit(img, rect)


    # Función para animar y mover un fantasma

    """Actualizar la animación del fantasma según su dirección de movimiento"""
    # Elegir el frame basado en la dirección
    if dir_fantasma == "R":
        frame_fantasma = frames_fantasma[0]  # Imagen para la derecha
    elif dir_fantasma == "L":
        frame_fantasma = pygame.transform.flip(frames_fantasma[0], True, False)  # Flip horizontal para izquierda
    elif dir_fantasma == "U":
        frame_fantasma = pygame.transform.rotate(frames_fantasma[0], 90)  # Rotar para arriba
    elif dir_fantasma == "D":
        frame_fantasma = pygame.transform.rotate(frames_fantasma[0], -90)  # Rotar para abajo

        # Dibujar el fantasma en la pantalla

    for fx, fy in fantasmas:
        rect_fantasma = frame_fantasma.get_rect(
            center=(fx * TAM_CELDA + TAM_CELDA // 2, fy * TAM_CELDA + TAM_CELDA // 2))
        pantalla.blit(frame_fantasma, rect_fantasma)


    # Mostrar información
    fuente = pygame.font.SysFont("arial", 22)
    texto = fuente.render(f"Puntos: {puntos_recolectados}/{puntos_totales} | Muertes: {muertes}", True, BLANCO)
    pantalla.blit(texto, (10, ALTO - 30))

    if puntos_recolectados == puntos_totales:
        mensaje = fuente.render("¡Pac-Man completó el nivel!", True, AMARILLO)
        pantalla.blit(mensaje, (ANCHO // 2 - 200, ALTO // 2))
        pygame.display.flip()
        pygame.time.wait(2000)
        ejecutando = False

    pygame.display.flip()

# --- REPORTE ---
fin_tiempo = time.time()
duracion = fin_tiempo - inicio_tiempo
fecha = time.strftime("%Y-%m-%d_%H-%M-%S")
ruta_reporte = os.path.join(ruta_performance, f"reporte_pacman_ia_2_fantasmas_{fecha}.txt")

reporte = f"""
REPORTE DE RENDIMIENTO - PACMAN IA con 2 fantasmas aleatorios

Puntos recolectados: {puntos_recolectados}/{puntos_totales}
Muertes: {muertes}
Zonas peligrosas aprendidas: {len(zonas_peligrosas)}
Pasos totales: {pasos_totales}
Duración total: {duracion:.2f} segundos
Fecha de ejecución: {time.strftime("%Y-%m-%d %H:%M:%S")}
"""

with open(ruta_reporte, "w", encoding="utf-8") as f:
    f.write(reporte)

print(f"Reporte guardado en: {ruta_reporte}")
print(reporte)
