import pygame
import sys
import os
import importlib.util

pygame.init()

# --- Ventana ---
ANCHO, ALTO = 600, 400

# --- Colores ---
NEGRO = (0, 0, 0)
AMARILLO = (255, 255, 0)
GRIS = (150, 150, 150)
BLANCO = (255, 255, 255)


def inicializar_menu():
    """Recrea la ventana y las fuentes del menú principal."""
    global pantalla, fuente_titulo, fuente_opcion, fuente_creditos

    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("PAC-MAN LAB - MENÚ PRINCIPAL")

    fuente_titulo = pygame.font.SysFont("arial", 48, bold=True)
    fuente_opcion = pygame.font.SysFont("arial", 28)
    fuente_creditos = pygame.font.SysFont("arial", 18)

# --- Rutas ---
ruta_src = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")

def cargar_modulo(nombre_archivo):
    ruta = os.path.join(ruta_src, nombre_archivo)
    spec = importlib.util.spec_from_file_location("modulo", ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo

# --- Escenarios disponibles ---
ESCENARIOS = [
    ("Pac-Man (Jugador)", "pacman_player.py", "ejecutar_juego_player"),
    ("Pac-Man IA (sin fantasmas)", "pacman_ia_no_fantasma.py", "ejecutar_juego_ia_sin_fantasmas"),
    ("Pac-Man IA (con 2 fantasmas)", "pacman_ia_2_fantasmas.py", "ejecutar_juego_ia_con_fantasmas"),
    ("Salir", None, None),
]

inicializar_menu()

opcion_seleccionada = 0

def ejecutar_juego(nombre_archivo, nombre_funcion):
    if not nombre_archivo:
        pygame.quit()
        sys.exit()

    modulo = cargar_modulo(nombre_archivo)
    funcion = getattr(modulo, nombre_funcion)

    pygame.event.clear()
    funcion()

    pygame.display.quit()
    pygame.display.init()
    inicializar_menu()

def main():
    global opcion_seleccionada
    reloj = pygame.time.Clock()

    while True:
        pantalla.fill(NEGRO)
        titulo = fuente_titulo.render("PAC-MAN LAB", True, AMARILLO)
        pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 40))

        for i, (nombre, _, _) in enumerate(ESCENARIOS):
            color = AMARILLO if i == opcion_seleccionada else GRIS
            texto = fuente_opcion.render(nombre, True, color)
            pantalla.blit(texto, (ANCHO // 2 - texto.get_width() // 2, 150 + i * 50))

        creditos = fuente_creditos.render("2025 Proyecto Pac-Man IA - Iván V. - Cristian V.", True, BLANCO)
        pantalla.blit(creditos, (ANCHO - creditos.get_width() - 10, ALTO - 25))

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP:
                    opcion_seleccionada = (opcion_seleccionada - 1) % len(ESCENARIOS)
                elif evento.key == pygame.K_DOWN:
                    opcion_seleccionada = (opcion_seleccionada + 1) % len(ESCENARIOS)
                elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    _, archivo, funcion = ESCENARIOS[opcion_seleccionada]
                    ejecutar_juego(archivo, funcion)

        pygame.display.flip()
        reloj.tick(15)

if __name__ == "__main__":
    main()