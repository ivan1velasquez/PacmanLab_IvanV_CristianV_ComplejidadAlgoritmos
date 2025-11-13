import os
import sys
import time

import pygame


RUTA_BASE = os.path.dirname(os.path.dirname(__file__))
if RUTA_BASE not in sys.path:
    sys.path.append(RUTA_BASE)

from data import mapas as mapas_data


RUTA_IMAGENES = os.path.join(RUTA_BASE, "images")

PACMAN_VELOCIDAD_ANIM = 5  # Fotogramas de animación por segundo

MAPA_DEFAULT_CONFIG = mapas_data.mapa_facil
MAPA_DEFAULT = MAPA_DEFAULT_CONFIG["layout"]
COLOR_MUROS_DEFAULT = MAPA_DEFAULT_CONFIG["color"]


def crear_animador(frames, velocidad_fps):
    return {
        "frames": frames,
        "velocidad": velocidad_fps,
        "indice": 0,
        "tiempo": 0.0,
    }


def avanzar_animacion(animador, dt_ms):
    frames = animador["frames"]
    if not frames:
        return pygame.Surface((0, 0), pygame.SRCALPHA)

    velocidad = animador["velocidad"]
    if velocidad > 0:
        intervalo = 1000 / velocidad
        animador["tiempo"] += dt_ms
        while animador["tiempo"] >= intervalo:
            animador["tiempo"] -= intervalo
            animador["indice"] = (animador["indice"] + 1) % len(frames)

    return frames[animador["indice"]]


def cargar_animacion(nombre_archivo, tam, frames=8):
    sheet = pygame.image.load(os.path.join(RUTA_IMAGENES, nombre_archivo)).convert_alpha()
    ancho_frame = sheet.get_width() // frames
    alto_frame = sheet.get_height()
    animacion = []
    for i in range(frames):
        frame = pygame.Surface((ancho_frame, alto_frame), pygame.SRCALPHA)
        frame.blit(sheet, (0, 0), (i * ancho_frame, 0, ancho_frame, alto_frame))
        animacion.append(pygame.transform.scale(frame, (tam, tam)))
    return animacion


def orientar_frame(frame, direccion):
    if direccion == "L":
        return pygame.transform.flip(frame, True, False)
    if direccion == "U":
        return pygame.transform.rotate(frame, 90)
    if direccion == "D":
        return pygame.transform.rotate(frame, -90)
    return frame

def ejecutar_juego_player(mapa_layout=None):
    pygame.init()
    pygame.font.init()
    TAM = 20
    NEGRO, AMARILLO, BLANCO = (0,0,0),(255,255,0),(255,255,255)
    configuracion_mapa = mapa_layout if mapa_layout is not None else MAPA_DEFAULT_CONFIG
    layout_base = configuracion_mapa["layout"]
    color_muros = configuracion_mapa.get("color", COLOR_MUROS_DEFAULT)
    ancho_mapa_px = len(layout_base[0]) * TAM
    alto_mapa_px = len(layout_base) * TAM
    ESPACIO_INFO = 80
    ANCHO = max(ancho_mapa_px, 400)
    ALTO = alto_mapa_px + ESPACIO_INFO
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Pac-Man - Modo Jugador")

    # --- Ruta de reportes ---
    ruta_base = os.path.dirname(os.path.dirname(__file__))  # .../PacmanLab
    ruta_performance = os.path.join(ruta_base, "log", "performance")
    os.makedirs(ruta_performance, exist_ok=True)

    # --- Mapa ---
    mapa = [list(f) for f in layout_base]

    pacman_frames = cargar_animacion("Pacman.png", TAM)
    animacion_pacman = crear_animador(pacman_frames, PACMAN_VELOCIDAD_ANIM)
    pacman_dir = "R"

    pacman_frames = cargar_animacion("Pacman.png", TAM)
    animacion_pacman = crear_animador(pacman_frames, PACMAN_VELOCIDAD_ANIM)
    pacman_dir = "R"

    pacman_x, pacman_y = 1, 1
    puntos_totales = sum(f.count("0") for f in mapa)
    puntos = 0
    pasos = 0
    direccion = None
    reloj = pygame.time.Clock()
    inicio = time.time()
    fuente_contador = pygame.font.SysFont("arial", 24)
    altura_mapa = alto_mapa_px

    def dibujar_mapa():
        for y, fila in enumerate(mapa):
            for x, c in enumerate(fila):
                if c == "1":
                    pygame.draw.rect(pantalla, color_muros, (x*TAM, y*TAM, TAM, TAM))
                elif c == "0":
                    pygame.draw.circle(pantalla, BLANCO, (x*TAM+TAM//2, y*TAM+TAM//2), 3)

    # --- Juego principal ---
    while True:
        dt = reloj.tick(12)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                duracion = time.time() - inicio
                guardar_reporte("jugador", puntos, puntos_totales, pasos, duracion, "Cancelado", ruta_performance)
                return
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP: direccion = "UP"
                elif e.key == pygame.K_DOWN: direccion = "DOWN"
                elif e.key == pygame.K_LEFT: direccion = "LEFT"
                elif e.key == pygame.K_RIGHT: direccion = "RIGHT"

        nx, ny = pacman_x, pacman_y
        if direccion == "UP": ny -= 1
        if direccion == "DOWN": ny += 1
        if direccion == "LEFT": nx -= 1
        if direccion == "RIGHT": nx += 1

        if mapa[ny][nx] != "1":
            if nx > pacman_x:
                pacman_dir = "R"
            elif nx < pacman_x:
                pacman_dir = "L"
            elif ny > pacman_y:
                pacman_dir = "D"
            elif ny < pacman_y:
                pacman_dir = "U"
            pacman_x, pacman_y = nx, ny
            pasos += 1
            if mapa[ny][nx] == "0":
                mapa[ny][nx] = " "
                puntos += 1

        # --- Dibujo frame ---
        pantalla.fill(NEGRO)
        dibujar_mapa()
        frame_base = avanzar_animacion(animacion_pacman, dt)
        frame_actual = orientar_frame(frame_base, pacman_dir)
        rect_pacman = frame_actual.get_rect(center=(pacman_x*TAM+TAM//2, pacman_y*TAM+TAM//2))
        pantalla.blit(frame_actual, rect_pacman)

        # Contadores en tiempo real
        duracion_actual = time.time() - inicio
        texto_puntos = fuente_contador.render(f"Puntos: {puntos}/{puntos_totales}", True, BLANCO)
        texto_tiempo = fuente_contador.render(f"Tiempo: {duracion_actual:.2f} s", True, BLANCO)
        barra_y = altura_mapa + 10
        pantalla.blit(texto_puntos, (10, barra_y))
        pantalla.blit(texto_tiempo, (10, barra_y + 30))
        pygame.display.flip()

        # Victoria
        if puntos == puntos_totales:
            duracion = time.time() - inicio
            guardar_reporte("jugador", puntos, puntos_totales, pasos, duracion, "Completado", ruta_performance)
            mostrar_resultado(pantalla, puntos, puntos_totales, pasos, duracion, vivo=True)
            return

def guardar_reporte(modo, puntos, totales, pasos, duracion, estado, ruta_base):
    fecha_file = time.strftime("%Y-%m-%d_%H-%M-%S")
    fecha_hum = time.strftime("%Y-%m-%d %H:%M:%S")
    velocidad = puntos / duracion if duracion > 0 else 0
    reporte = f"""REPORTE DE RENDIMIENTO - PACMAN {modo.upper()}

Estado: {estado}
Puntos recolectados: {puntos}/{totales}
Pasos totales: {pasos}
Duración total: {duracion:.2f} segundos
Velocidad promedio: {velocidad:.2f} puntos/segundo
Fecha de ejecución: {fecha_hum}
"""
    ruta = os.path.join(ruta_base, f"reporte_pacman_{modo}_{fecha_file}.txt")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(reporte)

def mostrar_resultado(pantalla, puntos, totales, pasos, duracion, vivo):
    fuente = pygame.font.SysFont("arial", 24)
    reloj = pygame.time.Clock()
    velocidad = puntos / duracion if duracion > 0 else 0
    lineas = [
        "¡Nivel completado!" if vivo else "Pac-Man fue atrapado",
        f"Puntos recolectados: {puntos}/{totales}",
        f"Pasos totales: {pasos}",
        f"Duración total: {duracion:.2f} seg",
        f"Velocidad promedio: {velocidad:.2f} pts/s",
        "Presiona ENTER para volver al menú"
    ]
    esperando = True
    while esperando:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return
            elif e.type == pygame.KEYDOWN and e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                esperando = False
                return

        pantalla.fill((0,0,0))
        ancho, alto = pantalla.get_size()
        espaciado = 32
        textos = [fuente.render(t, True, (255,255,0)) for t in lineas]
        max_ancho = max((txt.get_width() for txt in textos), default=0)
        alto_total = len(textos) * espaciado
        inicio_y = (alto - alto_total) // 2
        inicio_x = (ancho - max_ancho) // 2
        for i, txt in enumerate(textos):
            pantalla.blit(txt, (inicio_x, inicio_y + i * espaciado))
        pygame.display.flip()
        reloj.tick(30)
