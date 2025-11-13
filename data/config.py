"""Parámetros compartidos de configuración para los modos de juego."""

# Dimensiones y layout
TAM_CELDA = 20
ESPACIO_INFO = 80
ANCHO_MINIMO_VENTANA = 400

# Animaciones
PACMAN_ANIMACION_FPS = 5
FANTASMA_ANIMACION_FPS = 7

# Velocidades de actualización (FPS lógicos)
PLAYER_TICK_RATE = 12
IA_PACMAN_TICK_RATE = 10  # Utilizado por los modos IA para el movimiento del Pac-Man
MENU_TICK_RATE = 15
RESULTADO_TICK_RATE = 30

# Parámetros de comportamiento IA
FACTOR_MIEDO_BASE = 1.0
FACTOR_MIEDO_INCREMENTO = 0.5

# Posición inicial por defecto de Pac-Man
PACMAN_SPAWN_DEFAULT = (1, 1)
