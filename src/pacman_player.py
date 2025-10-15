import pygame
import sys

# Inicialización de pygame
pygame.init()

# Constantes
ANCHO, ALTO = 560, 620  # tamaño de la ventana (similar al clásico)
TAM_CELDA = 20
FPS = 10

# Colores
NEGRO = (0, 0, 0)
AZUL = (33, 33, 255)
AMARILLO = (255, 255, 0)
BLANCO = (255, 255, 255)

# Crear ventana
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Pac-Man Jugador :v")

# Reloj
reloj = pygame.time.Clock()

# Mapa simple con paredes (1) y caminos (0)
# 28 columnas x 31 filas ≈ 868 celdas, con puntos en los 244 caminos
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

# Convertir mapa a lista de listas
mapa = [list(fila) for fila in mapa]

# Posición inicial del Pac-Man
pacman_x, pacman_y = 1, 1

# Contador de puntos
puntos_totales = 0
for fila in mapa:
    puntos_totales += fila.count('0')  # puntos disponibles

puntos_restantes = puntos_totales

# Función para dibujar el mapa
def dibujar_mapa():
    for y, fila in enumerate(mapa):
        for x, celda in enumerate(fila):
            if celda == '1':  # pared
                pygame.draw.rect(pantalla, AZUL, (x*TAM_CELDA, y*TAM_CELDA, TAM_CELDA, TAM_CELDA))
            elif celda == '0':  # punto
                pygame.draw.circle(pantalla, BLANCO, (x*TAM_CELDA+TAM_CELDA//2, y*TAM_CELDA+TAM_CELDA//2), 3)

# Bucle principal del juego
direccion = None
puntos_recolectados = 0

ejecutando = True
while ejecutando:
    reloj.tick(FPS)
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_UP:
                direccion = "UP"
            elif evento.key == pygame.K_DOWN:
                direccion = "DOWN"
            elif evento.key == pygame.K_LEFT:
                direccion = "LEFT"
            elif evento.key == pygame.K_RIGHT:
                direccion = "RIGHT"

    # Movimiento
    nueva_x, nueva_y = pacman_x, pacman_y
    if direccion == "UP": nueva_y -= 1
    if direccion == "DOWN": nueva_y += 1
    if direccion == "LEFT": nueva_x -= 1
    if direccion == "RIGHT": nueva_x += 1

    # Verificar colisiones con paredes
    if mapa[nueva_y][nueva_x] != '1':
        pacman_x, pacman_y = nueva_x, nueva_y

        # Comer punto
        if mapa[pacman_y][pacman_x] == '0':
            mapa[pacman_y][pacman_x] = ' '  # celda vacía
            puntos_recolectados += 1
            puntos_restantes -= 1

    # Dibujar todo
    pantalla.fill(NEGRO)
    dibujar_mapa()
    pygame.draw.circle(pantalla, AMARILLO,
                       (pacman_x*TAM_CELDA+TAM_CELDA//2, pacman_y*TAM_CELDA+TAM_CELDA//2),
                       TAM_CELDA//2 - 2)

    # Mostrar puntaje
    fuente = pygame.font.SysFont("arial", 24)
    texto = fuente.render(f"Puntos: {puntos_recolectados}/{puntos_totales}", True, BLANCO)
    pantalla.blit(texto, (10, ALTO - 30))

    # Verificar victoria
    if puntos_restantes == 0:
        mensaje = fuente.render("¡Has recolectado los 244 puntos! 🎉", True, AMARILLO)
        pantalla.blit(mensaje, (ANCHO//2 - 220, ALTO//2))
        pygame.display.flip()
        pygame.time.wait(3000)
        ejecutando = False

    pygame.display.flip()
