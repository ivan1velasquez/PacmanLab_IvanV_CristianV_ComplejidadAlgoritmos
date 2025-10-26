import pygame, time, random, os
from collections import deque

def ejecutar_juego_ia_con_fantasmas():
    pygame.init()
    ANCHO, ALTO, TAM = 560, 620, 20
    NEGRO, AZUL, AMARILLO, BLANCO, ROJO = (0,0,0),(33,33,255),(255,255,0),(255,255,255),(255,0,0)
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Pac-Man - IA con 2 fantasmas")

    # --- Ruta de reportes ---
    ruta_base = os.path.dirname(os.path.dirname(__file__))  # .../PacmanLab
    ruta_performance = os.path.join(ruta_base, "results", "performance")
    os.makedirs(ruta_performance, exist_ok=True)

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
    reloj = pygame.time.Clock()
    inicio = time.time()

    def vecinos(x, y):
        dirs = [(1,0),(-1,0),(0,1),(0,-1)]
        return [(x+dx, y+dy) for dx,dy in dirs
                if 0<=x+dx<len(mapa[0]) and 0<=y+dy<len(mapa) and mapa[y+dy][x+dx] != "1"]

    def bfs(origen, destino):
        cola = deque([origen]); vis = {origen: None}
        while cola:
            act = cola.popleft()
            if act == destino:
                camino = []
                while act:
                    camino.append(act); act = vis[act]
                return camino[::-1]
            for v in vecinos(*act):
                if v not in vis:
                    vis[v] = act; cola.append(v)
        return None

    def punto_mas_cercano(x, y):
        from collections import deque
        cola = deque([(x,y)]); vis = {(x,y)}
        while cola:
            cx, cy = cola.popleft()
            if mapa[cy][cx] == "0":
                return (cx, cy)
            for nx, ny in vecinos(cx, cy):
                if (nx, ny) not in vis:
                    vis.add((nx, ny)); cola.append((nx, ny))
        return None

    # Celdas libres aleatorias para fantasmas
    def celda_libre():
        while True:
            x = random.randint(1, len(mapa[0]) - 2)
            y = random.randint(1, len(mapa) - 2)
            if mapa[y][x] != "1" and (x, y) != (pacman_x, pacman_y):
                return (x, y)

    fantasmas = [celda_libre(), celda_libre()]

    camino = []; idx = 0
    vivo = True

    while True:
        reloj.tick(10)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.display.quit()
                return

        # --- IA Pac-Man hacia el punto más cercano ---
        if not camino:
            destino = punto_mas_cercano(pacman_x, pacman_y)
            if destino:
                camino = bfs((pacman_x, pacman_y), destino); idx = 0
            else:
                # Sin puntos restantes: victoria
                duracion = time.time() - inicio
                guardar_reporte("ia_2fantasmas", puntos, puntos_totales, pasos, duracion, "Completado", ruta_performance)
                mostrar_resultado(pantalla, puntos, puntos_totales, pasos, duracion, vivo=True)
                return

        if camino and idx < len(camino):
            pacman_x, pacman_y = camino[idx]; idx += 1; pasos += 1
            if mapa[pacman_y][pacman_x] == "0":
                mapa[pacman_y][pacman_x] = " "; puntos += 1
        else:
            camino = []

        # --- Movimiento de fantasmas: persecución BFS ---
        for i, (gx, gy) in enumerate(fantasmas):
            c = bfs((gx, gy), (pacman_x, pacman_y))
            if c and len(c) > 1:
                fantasmas[i] = c[1]

        # Colisión con fantasmas
        for gx, gy in fantasmas:
            if (gx, gy) == (pacman_x, pacman_y):
                vivo = False
                duracion = time.time() - inicio
                guardar_reporte("ia_2fantasmas", puntos, puntos_totales, pasos, duracion, "Atrapado", ruta_performance)
                mostrar_resultado(pantalla, puntos, puntos_totales, pasos, duracion, vivo=False)
                return

        # --- Dibujo frame ---
        pantalla.fill(NEGRO)
        for y, fila in enumerate(mapa):
            for x, c in enumerate(fila):
                if c == "1": pygame.draw.rect(pantalla, AZUL, (x*TAM, y*TAM, TAM, TAM))
                elif c == "0": pygame.draw.circle(pantalla, BLANCO, (x*TAM+TAM//2, y*TAM+TAM//2), 3)
        pygame.draw.circle(pantalla, AMARILLO, (pacman_x*TAM+TAM//2, pacman_y*TAM+TAM//2), TAM//2-2)
        for gx, gy in fantasmas:
            pygame.draw.circle(pantalla, ROJO, (gx*TAM+TAM//2, gy*TAM+TAM//2), TAM//2-2)

        # Contador en tiempo real
        fuente = pygame.font.SysFont("arial", 24)
        texto = fuente.render(f"Puntos: {puntos}/{puntos_totales}", True, BLANCO)
        pantalla.blit(texto, (10, ALTO - 30))
        pygame.display.flip()

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
        "¡Pac-Man ganó! 🎉" if vivo else "Pac-Man fue atrapado 😵",
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
            pantalla.blit(txt, (60, 180 + i*30))
        pygame.display.flip()
