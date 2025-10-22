import pygame
import sys
import os
import time
from collections import deque
import random

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
ruta_performance = r"C:\Users\scozi\PycharmProjects\PacmanLab_IvanV_CristianV_ComplejidadAlgoritmos\performance"
os.makedirs(ruta_performance, exist_ok=True)

# Crear ventana
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Pac-Man IA con 2 Fantasmas Aleatorios")

reloj = pygame.time.Clock()

# --- MAPA ---
mapa = [
"1111111111111111111111111111",
"1000000000110000000000000001",
"1011111110110111111111111101",
"1011111110110111111111111101",
"1000000000000000000000000001",
"1011110111111111110111111101",
"1000000100000000000100000001",
"1111110110111111010111111111",
"1000000000001111000000000001",
"1011111111111111111111111101",
"1000000000000000000000000001",
"1111111111111111111111111111",
]
mapa = [list(fila) for fila in mapa]
FILAS, COLUMNAS = len(mapa), len(mapa[0])

# Posiciones iniciales
pacman_x, pacman_y = 1, 1

# Generar fantasmas en posiciones aleatorias válidas
def generar_fantasma():
    while True:
        x = random.randint(1, COLUMNAS-2)
        y = random.randint(1, FILAS-2)
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
                pygame.draw.rect(pantalla, AZUL, (x*TAM_CELDA, y*TAM_CELDA, TAM_CELDA, TAM_CELDA))
            elif celda == '0':
                pygame.draw.circle(pantalla, BLANCO, (x*TAM_CELDA+TAM_CELDA//2, y*TAM_CELDA+TAM_CELDA//2), 3)

def vecinos(x, y, evitar_peligro=True):
    posibles = [(x+1,y), (x-1,y), (x,y+1), (x,y-1)]
    validos = []
    for nx, ny in posibles:
        if 0 <= nx < COLUMNAS and 0 <= ny < FILAS and mapa[ny][nx] != '1':
            if not evitar_peligro or (nx, ny) not in zonas_peligrosas:
                validos.append((nx, ny))
    # Si no hay vecinos válidos y se estaba evitando peligros, permite atravesar zonas peligrosas
    if evitar_peligro and not validos:
        return vecinos(x, y, evitar_peligro=False)
    return validos

def bfs(origen, destino, evitar_peligro=True):
    cola = deque([origen])
    visitados = {origen: None}
    while cola:
        actual = cola.popleft()
        if actual == destino:
            camino = []
            while actual:
                camino.append(actual)
                actual = visitados[actual]
            return camino[::-1]
        for v in vecinos(*actual, evitar_peligro):
            if v not in visitados:
                visitados[v] = actual
                cola.append(v)
    return None

def encontrar_punto_mas_cercano(x, y):
    cola = deque([(x, y)])
    visitados = {(x, y)}
    while cola:
        cx, cy = cola.popleft()
        if mapa[cy][cx] == '0':
            return (cx, cy)
        for nx, ny in vecinos(cx, cy):
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

    # Detectar colisiones
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
    pygame.draw.circle(pantalla, AMARILLO, (pacman_x*TAM_CELDA+TAM_CELDA//2, pacman_y*TAM_CELDA+TAM_CELDA//2), TAM_CELDA//2 - 2)
    for fx, fy in fantasmas:
        pygame.draw.circle(pantalla, ROJO, (fx*TAM_CELDA+TAM_CELDA//2, fy*TAM_CELDA+TAM_CELDA//2), TAM_CELDA//2 - 2)

    fuente = pygame.font.SysFont("arial", 22)
    texto = fuente.render(f"Puntos: {puntos_recolectados}/{puntos_totales} | Muertes: {muertes}", True, BLANCO)
    pantalla.blit(texto, (10, ALTO - 30))

    if puntos_recolectados == puntos_totales:
        mensaje = fuente.render("¡Pac-Man completó el nivel!", True, AMARILLO)
        pantalla.blit(mensaje, (ANCHO//2 - 200, ALTO//2))
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