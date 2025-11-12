import pygame, time, random, os, heapq
from collections import deque


RUTA_BASE = os.path.dirname(os.path.dirname(__file__))
RUTA_IMAGENES = os.path.join(RUTA_BASE, "images")

PACMAN_VELOCIDAD_ANIM = 5  # Fotogramas de animación por segundo
FANTASMA_VELOCIDAD_ANIM = 7  # Fotogramas de animación por segundo

MAPA_DEFAULT = (
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
)

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

def ejecutar_juego_ia_con_fantasmas(mapa_layout=None):
    pygame.init()
    pygame.font.init()
    TAM = 20
    NEGRO, AZUL, AMARILLO, BLANCO = (0, 0, 0), (33, 33, 255), (255, 255, 0), (255, 255, 255)
    ROJO = (220, 20, 60)
    layout_base = mapa_layout if mapa_layout is not None else MAPA_DEFAULT
    layout_tuple = tuple(layout_base)
    es_mapa_facil = layout_tuple == MAPA_DEFAULT
    es_mapa_dificil = layout_tuple == MAPA_DIFICIL_LAYOUT
    ancho_mapa_px = len(layout_base[0]) * TAM
    alto_mapa_px = len(layout_base) * TAM
    ESPACIO_INFO = 80
    ANCHO = max(ancho_mapa_px, 400)
    ALTO = alto_mapa_px + ESPACIO_INFO
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Pac-Man - IA con 2 fantasmas")

    #Ruta de reportes
    ruta_base = os.path.dirname(os.path.dirname(__file__))  # .../PacmanLab
    ruta_performance = os.path.join(ruta_base, "log", "performance")
    os.makedirs(ruta_performance, exist_ok=True)

    mapa = [list(f) for f in layout_base]
    ancho_celdas = len(mapa[0]) if mapa else 0
    alto_celdas = len(mapa)

    pacman_frames = cargar_animacion("Pacman.png", TAM)
    animacion_pacman = crear_animador(pacman_frames, PACMAN_VELOCIDAD_ANIM)
    pacman_dir = "R"

    fantasma_frames = cargar_animacion("redGhost.png", TAM)
    animacion_fantasma = crear_animador(fantasma_frames, FANTASMA_VELOCIDAD_ANIM)

    pacman_frames = cargar_animacion("Pacman.png", TAM)
    animacion_pacman = crear_animador(pacman_frames, PACMAN_VELOCIDAD_ANIM)
    pacman_dir = "R"

    fantasma_frames = cargar_animacion("redGhost.png", TAM)
    animacion_fantasma = crear_animador(fantasma_frames, FANTASMA_VELOCIDAD_ANIM)

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
    altura_mapa = alto_mapa_px

    def vecinos(x, y):
        dirs = [(1,0),(-1,0),(0,1),(0,-1)]
        return [(x+dx, y+dy) for dx,dy in dirs
                if 0<=x+dx<len(mapa[0]) and 0<=y+dy<len(mapa) and mapa[y+dy][x+dx] != "1"]

    def es_transitable(celda):
        x, y = celda
        return 0 <= x < len(mapa[0]) and 0 <= y < len(mapa) and mapa[y][x] != "1"

    def direccion_desde_delta(dx, dy):
        if dx > 0:
            return "R"
        if dx < 0:
            return "L"
        if dy > 0:
            return "D"
        if dy < 0:
            return "U"
        return "R"

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
    fantasmas_dir = ["R" for _ in fantasmas]

    camino = []
    vivo = True

    while True:
        dt = reloj.tick(10)
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
            nx, ny = camino.pop(0)
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
            if mapa[pacman_y][pacman_x] == "0":
                mapa[pacman_y][pacman_x] = " "
                puntos += 1
                puntos_restantes.discard((pacman_x, pacman_y))
                camino = []
        else:
            pasos += 1

        # --- Movimiento de fantasmas: persecución BFS ---
        fantasmas_prev = list(fantasmas)
        for i, (gx, gy) in enumerate(fantasmas):
            c = bfs((gx, gy), (pacman_x, pacman_y))
            nx, ny = gx, gy
            if c and len(c) > 1:
                nx, ny = c[1]
            if nx > gx:
                fantasmas_dir[i] = "R"
            elif nx < gx:
                fantasmas_dir[i] = "L"
            elif ny > gy:
                fantasmas_dir[i] = "D"
            elif ny < gy:
                fantasmas_dir[i] = "U"
            fantasmas[i] = (nx, ny)

        # Resolver colisiones entre fantasmas haciendo que se separen
        ocupadas = {}
        procesadas = set()
        for idx, posicion in enumerate(fantasmas):
            if posicion in ocupadas:
                otro = ocupadas[posicion]
                par = tuple(sorted((idx, otro)))
                if par in procesadas:
                    continue
                procesadas.add(par)

                prev_idx = fantasmas_prev[idx]
                prev_otro = fantasmas_prev[otro]
                nuevo_idx = fantasmas[idx]
                nuevo_otro = fantasmas[otro]

                dx_idx = nuevo_idx[0] - prev_idx[0]
                dy_idx = nuevo_idx[1] - prev_idx[1]
                dx_otro = nuevo_otro[0] - prev_otro[0]
                dy_otro = nuevo_otro[1] - prev_otro[1]

                fantasmas[idx] = prev_idx
                fantasmas[otro] = prev_otro

                retroceso_idx = (prev_idx[0] - dx_idx, prev_idx[1] - dy_idx)
                if (dx_idx != 0 or dy_idx != 0) and es_transitable(retroceso_idx) and retroceso_idx != prev_otro:
                    fantasmas[idx] = retroceso_idx

                retroceso_otro = (prev_otro[0] - dx_otro, prev_otro[1] - dy_otro)
                if (dx_otro != 0 or dy_otro != 0) and es_transitable(retroceso_otro) and retroceso_otro != fantasmas[idx]:
                    fantasmas[otro] = retroceso_otro

                fantasmas_dir[idx] = direccion_desde_delta(prev_idx[0] - nuevo_idx[0], prev_idx[1] - nuevo_idx[1])
                fantasmas_dir[otro] = direccion_desde_delta(prev_otro[0] - nuevo_otro[0], prev_otro[1] - nuevo_otro[1])
            else:
                ocupadas[posicion] = idx

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
            pacman_dir = "R"
            camino = []
            for i, (gx, gy) in enumerate(fantasmas):
                if (gx, gy) == (pacman_x, pacman_y):
                    fantasmas[i] = celda_libre()
                    fantasmas_dir[i] = "R"
            continue
        else:
            vivo = True

        # --- Dibujo frame ---
        pantalla.fill(NEGRO)
        for y, fila in enumerate(mapa):
            for x, c in enumerate(fila):
                if c == "1":
                    borde = x == 0 or y == 0 or x == ancho_celdas - 1 or y == alto_celdas - 1
                    color_pared = AZUL
                    if borde:
                        if es_mapa_facil:
                            color_pared = VERDE
                        elif es_mapa_dificil:
                            color_pared = ROJO
                    pygame.draw.rect(pantalla, color_pared, (x*TAM, y*TAM, TAM, TAM))
                elif c == "0":
                    pygame.draw.circle(pantalla, BLANCO, (x*TAM+TAM//2, y*TAM+TAM//2), 3)
        frame_base_pacman = avanzar_animacion(animacion_pacman, dt)
        frame_pacman = orientar_frame(frame_base_pacman, pacman_dir)
        rect_pacman = frame_pacman.get_rect(center=(pacman_x*TAM+TAM//2, pacman_y*TAM+TAM//2))
        pantalla.blit(frame_pacman, rect_pacman)

        frame_fantasma_base = avanzar_animacion(animacion_fantasma, dt)
        for (gx, gy), dir_fantasma in zip(fantasmas, fantasmas_dir):
            frame_fantasma = orientar_frame(frame_fantasma_base, dir_fantasma)
            rect_fantasma = frame_fantasma.get_rect(center=(gx*TAM+TAM//2, gy*TAM+TAM//2))
            pantalla.blit(frame_fantasma, rect_fantasma)

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
