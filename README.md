"PAC BOT" LAB COMPLEJIDAD DE ALGORITMOS (10-2025)
por Iván Velásquez y Cristián Vega 
---------------------------------------
Para ejecutar primero debe descomprimir el archivo .zip del programa completo, luego abrir el archi en Pycharm y luego solo basta con ejecutar el archivo main.py ubicado en el directorio "gui", ádemas de contar con 
Pycharm actualizado a su última versión, luego debe configurar "VCS root" de "Git" a "none", luego debe instalar el interprete de Python, ademas de instalar Pygame, ya sea por consola, 
o directamente por Pycharm por medio de "InstallPackage" que es una funcion disponible al correr el main.py por primera vez.

------------- PAC - BOT ----------------
RESUMEN GENERAL
El proyecto Pac-Bot Lab ofrece un menú principal en Pygame que permite lanzar tres escenarios (jugador humano, IA sin fantasmas e IA con dos fantasmas) y 
seleccionar entre varios mapas predefinidos cargados dinámicamente.

ESTRUCTURA PRINCIPAL
"main.py" contiene el menú interactivo, la carga dinámica de módulos de juego y la pantalla de selección de mapas; tras ejecutar un modo, 
reinicia la interfaz para permitir nuevas partidas, definiendo los layouts de laberinto que comparten los tres modos, reutilizados 
como tuplas de cadenas en las instancias de juego.

Cada modo de juego reside en "src"; con "pacman_player.py" para el jugador humano, "pacman_ia_no_fantasma.py" para la IA sin enemigos y 
"pacman_ia_2_fantasmas.py" para la IA avanzada con dos fantasmas, compartiendo utilidades de animación y reporte de desempeño.

MODO JUGADOR
El control humano registra la última dirección pulsada, valida el movimiento contra muros y avanza paso a paso recolectando puntos; cada 
actualización refresca HUD de puntuación/tiempo y al completar todos los puntos se genera un reporte de rendimiento y una pantalla de victoria.

IA SIN FANTASMAS
La IA busca siempre la píldora más cercana mediante BFS sobre la grilla accesible (punto_mas_cercano) y genera el camino óptimo con otro BFS (bfs); 
al agotar los puntos registra estadísticas y muestra un resumen en pantalla.

IA CON 2 FANTASMAS
El agente combina A* con penalizaciones dinámicas para evitar a los fantasmas: calcula la heurística Manhattan a la píldora más próxima (heuristica_punto) 
y añade costos según la proximidad de cada fantasma (penalizacion_dinamica), ajustados por un “factor de miedo” que aumenta tras cada muerte.

Los fantasmas persiguen a Pac-Man con BFS directo en cada fotograma, actualizando su orientación para la animación y provocando reinicios 
cuando colisionan; las estadísticas incluyen muertes acumuladas.

REPORTES Y VISUALIZACION

Los tres modos registran archivos de desempeño con puntos, pasos y duración en results/performance, y emplean pantallas finales interactivas 
para mostrar los mismos indicadores dentro del juego.


------------Versión MVP 1.2----------------
