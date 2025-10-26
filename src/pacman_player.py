import pygame, os, time

def ejecutar_juego_player():
    pygame.init()
    ANCHO, ALTO, TAM = 560, 620, 20
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

    pacman_x, pacman_y = 1, 1
    puntos_totales = sum(f.count("0") for f in mapa)
    puntos = 0
    pasos = 0
    direccion = None
    reloj = pygame.time.Clock()
    inicio = time.time()

    def dibujar_mapa():
        for y, fila in enumerate(mapa):
            for x, c in enumerate(fila):
                if c == "1":
                    pygame.draw.rect(pantalla, AZUL, (x*TAM, y*TAM, TAM, TAM))
                elif c == "0":
                    pygame.draw.circle(pantalla, BLANCO, (x*TAM+TAM//2, y*TAM+TAM//2), 3)

    # --- Juego principal ---
    while True:
        reloj.tick(12)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.display.quit()
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
            pacman_x, pacman_y = nx, ny
            pasos += 1
            if mapa[ny][nx] == "0":
                mapa[ny][nx] = " "
                puntos += 1

        # --- Dibujo frame ---
        pantalla.fill(NEGRO)
        dibujar_mapa()
        pygame.draw.circle(pantalla, AMARILLO, (pacman_x*TAM+TAM//2, pacman_y*TAM+TAM//2), TAM//2-2)
        # Contador en tiempo real
        fuente = pygame.font.SysFont("arial", 24)
        texto = fuente.render(f"Puntos: {puntos}/{puntos_totales}", True, BLANCO)
        pantalla.blit(texto, (10, ALTO - 30))
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
    reporte = f"""REPORTE DE RENDIMIENTO - PACMAN {modo.upper()}

Estado: {estado}
Puntos recolectados: {puntos}/{totales}
Pasos totales: {pasos}
Duración total: {duracion:.2f} segundos
Velocidad promedio: {puntos/duracion:.2f} puntos/segundo
Fecha de ejecución: {fecha_hum}
"""
    ruta = os.path.join(ruta_base, f"reporte_pacman_{modo}_{fecha_file}.txt")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(reporte)

def mostrar_resultado(pantalla, puntos, totales, pasos, duracion, vivo):
    fuente = pygame.font.SysFont("arial", 24)
    lineas = [
        "¡Nivel completado! 🎉" if vivo else "Pac-Man fue atrapado 😵",
        f"Puntos recolectados: {puntos}/{totales}",
        f"Pasos totales: {pasos}",
        f"Duración total: {duracion:.2f} seg",
        f"Velocidad promedio: {puntos/duracion:.2f} pts/s",
        "Presiona ENTER para volver al menú"
    ]
    esperando = True
    while esperando:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.display.quit()
                return
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                esperando = False
                pygame.display.quit()
                return

        pantalla.fill((0,0,0))
        for i, t in enumerate(lineas):
            txt = fuente.render(t, True, (255,255,0))
            pantalla.blit(txt, (60, 200 + i*30))
        pygame.display.flip()
