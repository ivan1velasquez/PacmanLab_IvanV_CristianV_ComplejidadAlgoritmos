import pygame, time, random, os, heapq
from collections import deque

def ejecutar_juego_ia_con_fantasmas():
    pygame.init()
    pygame.font.init()
    ANCHO, ALTO, TAM = 560, 400, 20
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
    spawn_inicial = (pacman_x, pacman_y)
    puntos_restantes = {(x, y) for y, fila in enumerate(mapa) for x, celda in enumerate(fila) if celda == "0"}
    puntos_totales = len(puntos_restantes)
    puntos = 0
    pasos = 0
    muertes = 0
    factor_miedo = 1.0
    reloj = pygame.time.Clock()
    inicio = time.time()
    fuente_contador = pygame.font.SysFont("arial", 24)
    altura_mapa = len(mapa) * TAM

    def vecinos(x, y):
        dirs = [(1,0),(-1,0),(0,1),(0,-1)]
        return [(x+dx, y+dy) for dx,dy in dirs
                if 0<=x+dx<len(mapa[0]) and 0<=y+dy<len(mapa) and mapa[y+dy][x+dx] != "1"]

    def bfs(origen, destino):
        cola = deque([origen])
        vis = {origen: None}
        while cola:
            act = cola.popleft()
            if act == destino:
                camino = []
                while act:
                    camino.append(act)
                    act = vis[act]
                return camino[::-1]
            for v in vecinos(*act):
                if v not in vis:
                    vis[v] = act
                    cola.append(v)
        return None

    def heuristica_punto(pos):
        if not puntos_restantes:
            return 0
        return min(abs(pos[0] - px) + abs(pos[1] - py) for px, py in puntos_restantes)

    def penalizacion_dinamica(pos, fantasmas_locales, factor):
        penalizacion = 0
        for gx, gy in fantasmas_locales:
            dist = abs(pos[0] - gx) + abs(pos[1] - gy)
            if dist == 0:
                penalizacion += 100
            else:
                proximidad = max(0, 4 - dist)
                penalizacion += proximidad * proximidad
        return penalizacion * factor

    def a_star_penalizado(origen, fantasmas_locales):
        if not puntos_restantes:
            return []
        abiertos = []
        g_costos = {origen: 0}
        came_from = {}
        heur = heuristica_punto(origen)
        heapq.heappush(abiertos, (heur, 0, origen))
        visitados = set()

        while abiertos:
            f_actual, g_actual, actual = heapq.heappop(abiertos)
            if actual in visitados:
                continue
            visitados.add(actual)

            if actual in puntos_restantes:
                camino = []
                while actual != origen:
                    camino.append(actual)
                    actual = came_from[actual]
                camino.reverse()
                return camino

            for vecino in vecinos(*actual):
                costo_mov = 1 + penalizacion_dinamica(vecino, fantasmas_locales, factor_miedo)
                tentativo = g_actual + costo_mov
                if tentativo < g_costos.get(vecino, float('inf')):
                    g_costos[vecino] = tentativo
                    came_from[vecino] = actual
                    heuristica_vecino = heuristica_punto(vecino)
                    heapq.heappush(abiertos, (tentativo + heuristica_vecino, tentativo, vecino))
        return []

    # Celdas libres aleatorias para fantasmas
    def celda_libre():
        while True:
            x = random.randint(1, len(mapa[0]) - 2)
            y = random.randint(1, len(mapa) - 2)
            if mapa[y][x] != "1" and (x, y) != (pacman_x, pacman_y):
                return (x, y)

    fantasmas = [celda_libre(), celda_libre()]

    camino = []
    vivo = True

    while True:
        reloj.tick(10)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                duracion = time.time() - inicio
                guardar_reporte("ia_2fantasmas", puntos, puntos_totales, pasos, duracion, "Cancelado", ruta_performance, muertes)
                return

        if not puntos_restantes:
            duracion = time.time() - inicio
            guardar_reporte("ia_2fantasmas", puntos, puntos_totales, pasos, duracion, "Completado", ruta_performance, muertes)
            mostrar_resultado(pantalla, puntos, puntos_totales, pasos, duracion, muertes, vivo=True)
            return

        if (pacman_x, pacman_y) in puntos_restantes:
            mapa[pacman_y][pacman_x] = " "
            puntos += 1
            puntos_restantes.discard((pacman_x, pacman_y))
            camino = []

        if not camino:
            camino = a_star_penalizado((pacman_x, pacman_y), fantasmas)

        if camino:
            pacman_x, pacman_y = camino.pop(0)
            pasos += 1
            if mapa[pacman_y][pacman_x] == "0":
                mapa[pacman_y][pacman_x] = " "
                puntos += 1
                puntos_restantes.discard((pacman_x, pacman_y))
                camino = []
        else:
            pasos += 1

        # --- Movimiento de fantasmas: persecución BFS ---
        for i, (gx, gy) in enumerate(fantasmas):
            c = bfs((gx, gy), (pacman_x, pacman_y))
            if c and len(c) > 1:
                fantasmas[i] = c[1]

        # Colisión con fantasmas
        atrapado = False
        for gx, gy in fantasmas:
            if (gx, gy) == (pacman_x, pacman_y):
                atrapado = True
                break

        if atrapado:
            vivo = False
            muertes += 1
            factor_miedo = 1.0 + muertes * 0.5
            pacman_x, pacman_y = spawn_inicial
            camino = []
            for i, (gx, gy) in enumerate(fantasmas):
                if (gx, gy) == (pacman_x, pacman_y):
                    fantasmas[i] = celda_libre()
            continue
        else:
            vivo = True

        # --- Dibujo frame ---
        pantalla.fill(NEGRO)
        for y, fila in enumerate(mapa):
            for x, c in enumerate(fila):
                if c == "1":
                    pygame.draw.rect(pantalla, AZUL, (x*TAM, y*TAM, TAM, TAM))
                elif c == "0":
                    pygame.draw.circle(pantalla, BLANCO, (x*TAM+TAM//2, y*TAM+TAM//2), 3)
        pygame.draw.circle(pantalla, AMARILLO, (pacman_x*TAM+TAM//2, pacman_y*TAM+TAM//2), TAM//2-2)
        for gx, gy in fantasmas:
            pygame.draw.circle(pantalla, ROJO, (gx*TAM+TAM//2, gy*TAM+TAM//2), TAM//2-2)

        # Contadores en tiempo real
        duracion_actual = time.time() - inicio
        texto_puntos = fuente_contador.render(f"Puntos: {puntos}/{puntos_totales}", True, BLANCO)
        texto_tiempo = fuente_contador.render(f"Tiempo: {duracion_actual:.2f} s", True, BLANCO)
        texto_muertes = fuente_contador.render(f"Muertes: {muertes}", True, BLANCO)
        barra_y = altura_mapa + 10
        pantalla.blit(texto_puntos, (10, barra_y))
        pantalla.blit(texto_tiempo, (10, barra_y + 30))
        pantalla.blit(texto_muertes, (260, barra_y))
        pygame.display.flip()

def guardar_reporte(modo, puntos, totales, pasos, duracion, estado, ruta_base, muertes):
    fecha_file = time.strftime("%Y-%m-%d_%H-%M-%S")
    fecha_hum = time.strftime("%Y-%m-%d %H:%M:%S")
    velocidad = puntos / duracion if duracion > 0 else 0
    reporte = f"""REPORTE DE RENDIMIENTO - PACMAN {modo.upper()}

Estado: {estado}
Puntos recolectados: {puntos}/{totales}
Pasos totales: {pasos}
Duración total: {duracion:.2f} segundos
Velocidad promedio: {velocidad:.2f} puntos/segundo
Muertes totales: {muertes}
Fecha de ejecución: {fecha_hum}
"""
    ruta = os.path.join(ruta_base, f"reporte_pacman_{modo}_{fecha_file}.txt")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(reporte)

def mostrar_resultado(pantalla, puntos, totales, pasos, duracion, muertes, vivo):
    fuente = pygame.font.SysFont("arial", 24)
    reloj = pygame.time.Clock()
    velocidad = puntos / duracion if duracion > 0 else 0
    lineas = [
        "¡Pac-Man ganó!" if vivo else "Pac-Man fue atrapado",
        f"Puntos recolectados: {puntos}/{totales}",
        f"Pasos totales: {pasos}",
        f"Duración total: {duracion:.2f} seg",
        f"Velocidad promedio: {velocidad:.2f} pts/s",
        f"Muertes totales: {muertes}",
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
