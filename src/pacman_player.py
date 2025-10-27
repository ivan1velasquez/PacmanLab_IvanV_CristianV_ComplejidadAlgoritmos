import pygame, os, time


RUTA_BASE = os.path.dirname(os.path.dirname(__file__))
RUTA_IMAGENES = os.path.join(RUTA_BASE, "images")

PACMAN_VELOCIDAD_ANIM = 5  # Fotogramas de animación por segundo


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

def ejecutar_juego_player():
    pygame.init()
    pygame.font.init()
    ANCHO, ALTO, TAM = 560, 400, 20
    NEGRO, AZUL, AMARILLO, BLANCO = (0,0,0),(33,33,255),(255,255,0),(255,255,255)
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Pac-Man - Modo Jugador")

    # --- Ruta de reportes ---
    ruta_base = os.path.dirname(os.path.dirname(__file__))  # .../PacmanLab
    ruta_performance = os.path.join(ruta_base, "results", "performance")
    os.makedirs(ruta_performance, exist_ok=True)

    # --- Mapa ---
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
    mapa = [list(f) for f in mapa]

    pacman_frames = cargar_animacion("Pacman.png", TAM)
    pacman_frame_idx = 0
    pacman_anim_contador = 0
    PACMAN_VELOCIDAD_ANIM = 18
    pacman_dir = "R"

    pacman_x, pacman_y = 1, 1
    puntos_totales = sum(f.count("0") for f in mapa)
    puntos = 0
    pasos = 0
    direccion = None
    reloj = pygame.time.Clock()
    inicio = time.time()
    fuente_contador = pygame.font.SysFont("arial", 24)
    altura_mapa = len(mapa) * TAM

    def dibujar_mapa():
        for y, fila in enumerate(mapa):
            for x, c in enumerate(fila):
                if c == "1":
                    pygame.draw.rect(pantalla, AZUL, (x*TAM, y*TAM, TAM, TAM))
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
        intervalo_pacman = 1000 / PACMAN_VELOCIDAD_ANIM if PACMAN_VELOCIDAD_ANIM > 0 else 1000
        pacman_anim_tiempo += dt
        while pacman_anim_tiempo >= intervalo_pacman:
            pacman_anim_tiempo -= intervalo_pacman
            pacman_frame_idx = (pacman_frame_idx + 1) % len(pacman_frames)

        frame_actual = orientar_frame(pacman_frames[pacman_frame_idx], pacman_dir)
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
        for i, t in enumerate(lineas):
            txt = fuente.render(t, True, (255,255,0))
            pantalla.blit(txt, (60, 80 + i*30))
        pygame.display.flip()
        reloj.tick(30)
