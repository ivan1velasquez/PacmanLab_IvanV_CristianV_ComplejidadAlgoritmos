import pygame
import sys
import os
import time
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

# Crear carpeta de rendimiento si no existe
ruta_performance = r"C:\Users\ivan.velasquez\PycharmProjects\PacmanLab\performance"
os.makedirs(ruta_performance, exist_ok=True)

# Crear ventana
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Pac-Man IA sin fantasmas")

reloj = pygame.time.Clock()

# Mapa
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

# Posición inicial
pacman_x, pacman_y = 1, 1

# Contar puntos
puntos_totales = sum(f.count('0') for f in mapa)
puntos_recolectados = 0

# --- FUNCIONES ---

def dibujar_mapa():
    for y, fila in enumerate(mapa):
        for x, celda in enumerate(fila):
            if celda == '1':
                pygame.draw.rect(pantalla, AZUL, (x*TAM_CELDA, y*TAM_CELDA, TAM_CELDA, TAM_CELDA))
            elif celda == '0':
                pygame.draw.circle(pantalla, BLANCO, (x*TAM_CELDA+TAM_CELDA//2, y*TAM_CELDA+TAM_CELDA//2), 3)

def vecinos(x, y):
    posibles = [(x+1,y), (x-1,y), (x,y+1), (x,y-1)]
    return [(nx,ny) for nx,ny in posibles if 0 <= nx < COLUMNAS and 0 <= ny < FILAS and mapa[ny][nx] != '1']

def bfs(origen, destino):
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
        for v in vecinos(*actual):
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

# --- MÉTRICAS DE RENDIMIENTO ---
inicio_tiempo = time.time()
pasos_totales = 0

# --- BUCLE PRINCIPAL ---
camino_actual = []
indice_camino = 0
ejecutando = True

while ejecutando:
    reloj.tick(FPS)
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    if not camino_actual:
        objetivo = encontrar_punto_mas_cercano(pacman_x, pacman_y)
        if objetivo:
            camino_actual = bfs((pacman_x, pacman_y), objetivo)
            indice_camino = 0
        else:
            ejecutando = False

    if camino_actual and indice_camino < len(camino_actual):
        pacman_x, pacman_y = camino_actual[indice_camino]
        indice_camino += 1
        pasos_totales += 1  # contador de pasos

        if mapa[pacman_y][pacman_x] == '0':
            mapa[pacman_y][pacman_x] = ' '
            puntos_recolectados += 1
    else:
        camino_actual = []

    pantalla.fill(NEGRO)
    dibujar_mapa()
    pygame.draw.circle(pantalla, AMARILLO,
                       (pacman_x*TAM_CELDA+TAM_CELDA//2, pacman_y*TAM_CELDA+TAM_CELDA//2),
                       TAM_CELDA//2 - 2)

    fuente = pygame.font.SysFont("arial", 24)
    texto = fuente.render(f"Puntos: {puntos_recolectados}/{puntos_totales}", True, BLANCO)
    pantalla.blit(texto, (10, ALTO - 30))

    if puntos_recolectados == puntos_totales:
        mensaje = fuente.render("¡Pac-Man recolectó todos los puntos! 🎉", True, AMARILLO)
        pantalla.blit(mensaje, (ANCHO//2 - 240, ALTO//2))
        pygame.display.flip()
        pygame.time.wait(2000)
        ejecutando = False

    pygame.display.flip()

# --- FIN DEL JUEGO: GUARDAR REPORTE ---
fin_tiempo = time.time()
duracion = fin_tiempo - inicio_tiempo

reporte = f"""
📊 REPORTE DE RENDIMIENTO - PACMAN IA sin fantasmas

Puntos recolectados: {puntos_recolectados}/{puntos_totales}
Pasos totales: {pasos_totales}
Duración total: {duracion:.2f} segundos
Velocidad promedio: {puntos_recolectados/duracion:.2f} puntos por segundo

Fecha de ejecución: {time.strftime("%Y-%m-%d %H:%M:%S")}
"""

# Guardar en carpeta performance
fecha_ejecucion = time.strftime("%Y-%m-%d_%H-%M-%S")
ruta_reporte = os.path.join(ruta_performance, f"reporte_pacman_{fecha_ejecucion}.txt")
with open(ruta_reporte, "w", encoding="utf-8") as f:
    f.write(reporte)

print(f"\n✅ Reporte guardado en: {ruta_reporte}")
print(reporte)
