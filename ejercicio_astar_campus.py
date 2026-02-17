import math
import heapq
from operator import contains


class Campus:
    """
    Mapa de celdas. Cada celda en self.main_map[i][j] es un dict:
        {
            "locacion": <valor original de init_map[i][j]>,
            "pisos": <int>,         # cantidad de pisos válidos (>=1)
            "coordenadas": (i, j),
            "ascensor": <bool>      # se puede sobrescribir por reglas
        }
    """
    def __init__(self, init_map, start, end):
        # Tamaño del mapa
        self.rows = len(init_map)
        self.cols = len(init_map[0]) if self.rows > 0 else 0

        # Inicializa la matriz de celdas
        self.main_map = [[None for _ in range(self.cols)] for _ in range(self.rows)]

        self.point = None        # (i, j, piso_actual)
        self.end_point = None    # (i, j, piso_objetivo)

        for i in range(self.rows):
            for j in range(self.cols):
                location = init_map[i][j]

                # Determinar pisos:
                # - si location es tupla (simbolo, pisos) úsalo
                # - si es transitable (incluido " ")

                pisos = 0
                ascensor = False

                if isinstance(location, tuple) and len(location) >= 2 and isinstance(location[1], int):
                    pisos = max(0, location[1])  # por seguridad, no negativos
                    simbolo = location[0]
                    if len(location) > 2: # Si se llegara (por alguna razon) a colocar una nueva propiedad a los edificios pues tocaria colocar mejor otro metodo
                        ascensor = True
                else:
                    simbolo = location

                # Estructura base de la celda
                self.main_map[i][j] = {
                    "locacion": simbolo,
                    "pisos": pisos,
                    "ascensor": ascensor
                }

                # Reglas específicas a tomar en cuenta por símbolo (si aplica)
                # Ejemplo: specific_rules = { "B31": [("ascensor", True), ("pisos", 5)], ... }
                """
                Idea antigua, no usable para nuevo modelo
                if simbolo in specific_rules:
                    for prop, val in specific_rules[simbolo]:
                        self.main_map[i][j][prop] = val
                        # Si cambian "pisos" vía regla, aseguremos consistencia
                        if prop == "pisos":
                            self.main_map[i][j]["pisos"] = max(0, int(val))
                """

                # Punto inicial (coincide el símbolo)
                if isinstance(start, tuple) and len(start) >= 2:
                    if simbolo == start[0]:
                        # clamp piso a rango válido
                        piso_ini = max(0, min(start[1], self.main_map[i][j]["pisos"] - 1)) if self.main_map[i][j]["pisos"] > 0 else 0
                        self.start_point = (j, i, piso_ini)

                # Punto final (coincide el símbolo)
                if isinstance(end, tuple) and len(end) >= 2:
                    if simbolo == end[0]:
                        piso_fin = max(0, min(end[1], self.main_map[i][j]["pisos"] - 1)) if self.main_map[i][j]["pisos"] > 0 else 0
                        self.end_point = (j, i, piso_fin)

        # Validaciones básicas
        if self.start_point is None:
            raise ValueError("No se encontró el punto inicial en el mapa con el símbolo dado en 'start'.")
        if self.end_point is None:
            raise ValueError("No se encontró el punto final en el mapa con el símbolo dado en 'end'.")

    def en_limites(self, i, j):
        return 0 <= i < self.rows and 0 <= j < self.cols

    def check_end(self, position):
        return position == self.end_point

    def h(self, n):
        """
        Heurística: distancia euclidiana en planta (ignora variación de pisos).
        n es una tupla (i, j, piso) o (i, j).
        """
        ni, nj = n[0], n[1]
        return math.hypot(ni - self.end_point[0], nj - self.end_point[1])

#Objeto para representar los estados y que el heapyfy funcione
class State:
    def __init__(self, cost, coords):
        self.cost = cost
        self.coords = coords

    def __lt__(self, other):
        return self.cost < other.cost

# Solucionador A*
class AStarSolver:
    def __init__(self, campus):
        self.campus = campus

    #Logica para definir como obtener los vecinos del estado x
    def vecinos(self, state):
        """Genera (estado_vecino, costo_paso)."""
        i, j, p = state
        directions = [(0, 1, 0), (1, 0, 0), (0, -1, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1)]

        ret_directions = []

        for di, dj, dp in directions:
            ni, nj, np = i + di, j + dj, p + dp

            # límites
            if not self.campus.en_limites(nj, ni):
                continue

            destino = self.campus.main_map[nj][ni]

            # muro
            if destino["locacion"] == "#":
                continue

            # piso válido
            if np < 0 or np > destino["pisos"]:
                continue

            # costo
            if dp == 0:
                step_cost = 1
            else:
                step_cost = 3 if destino["ascensor"] else (7 if dp > 0 else 5)

            ret_directions.append(((ni, nj, np), step_cost))

        # Devuelve los lugares de movimiento posible y sus costos
        return ret_directions

    def solve(self):
        start = self.campus.start_point
        goal  = self.campus.end_point

        # open set como min-heap: (f, tie_breaker, state)
        open_heap = []

        # costos y padres
        f = {start: 0}
        came_from = {}

        f0 = 0 # g[start] + self.campus.h(start)
        heapq.heappush(open_heap, State(f0, start))

        # closed = set()

        # Se empieza la creacion del arbol
        while open_heap:
            # Se obtiene el estado de menor costo con respecto a f
            state = heapq.heappop(open_heap)

            current = state.coords
            cost_current = state.cost

            # if current in closed:
                # continue

            # Si es el final reconstruimos la ruta y paramos
            if current == goal:
                # reconstruir ruta
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                return path, cost_current

            # closed.add(current) # Añadir los nodos visitados/cerrados

            # Si no entonces obtenemos los estados vecinos y añadimos a la cola
            for neighbor, step_cost in self.vecinos(current):
                #if neighbor in closed:
                    #continue
                #    f  =  g(x) + h(x)
                tentative_f = cost_current + step_cost + self.campus.h(neighbor)

                if tentative_f < f.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    f[neighbor] = tentative_f
                    heapq.heappush(open_heap, State(tentative_f, neighbor))
                    heapq.heapify(open_heap)

        return None, float('inf')






m = [
    [" ", "#", " ",  " ", "#",  " ",  " ", "#", " ",  " ", "#", " ",  " ", "#", " ",  " ", " "],  # y=0
    [" ", "#", " ",  " ", "#",  " ",  " ", "#", " ",  " ", "#", " ",  " ", "#", " ",  " ", " "],  # y=1

    [" ", " ", "B30"," ", " ", "B31"," ", " ", "B32"," ", " ", ("B33", 3, True)," ", " ", ("B34", 3, True)," ", " "],  # y=2

    [" ", "#", " ",  "#", "#", " ",  "#", " ", "#",  "#", " ", "#",  " ", "#", " ",  "#", " "],  # y=3
    [" ", "#", " ",  " ", " ", " ",  "#", " ", "#",  " ", " ", "#",  " ", "#", " ",  "#", " "],  # y=4

    [" ", " ", " ",  "#", " ", " ",  " ", " ", " ",  "#", " ", " ",  " ", " ", " ",  "#", " "],  # y=5

    [" ", "#", " ",  " ", ("B35", 3, True)," ",  "#", " ", "B36"," ", "#", " ",  ("B37", 3, True)," ", "#", " ", ("B38", 3, True)], # y=6

    [" ", "#", "#",  " ", "#", " ",  "#", " ", "#",  " ", "#", " ",  "#", " ", "#",  " ", " "],  # y=7
    [" ", " ", " ",  " ", "#", " ",  " ", " ", "#",  " ", " ", " ",  "#", " ", " ",  " ", " "],  # y=8

    ["#", "#", " ",  "#", "#", " ",  "#", " ", " ",  " ", "#", " ",  "#", " ", "#",  "#", " "],  # y=9

    [" ", " ", " ",  " ", "#", " ",  "C", " ", "#",  " ", "#", " ",  " ", " ", "B",  " ", " "],  # y=10

    [" ", "#", "#",  " ", "#", " ",  "#", " ", "#",  " ", "#", " ",  "#", " ", "#",  " ", " "],  # y=11
    [" ", " ", " ",  " ", " ", " ",  " ", " ", " ",  " ", " ", " ",  " ", " ", " ",  " ", " "],  # y=12

    [" ", "#", " ",  "#", " ", "#",  " ", "#", " ",  "#", " ", "#",  " ", "#", " ",  "#", " "],  # y=13
    [" ", "#", " ",  " ", " ", " ",  " ", " ", " ",  " ", " ", " ",  " ", " ", " ",  "#", " "],  # y=14

    [" ", " ", " ",  "#", "#", "#",  " ", "#", "#",  "#", " ", "#",  "#", "#", " ",  " ", " "],  # y=15
]

print( AStarSolver(Campus(m, ("B30", 0), ("B37", 2))).solve() )

# Notas de experimentacion:
"""
    Intento 1: Realize una clase para el campus la cual manejara los movimientos, el mapa y el checkeo de llegada al final
    Para luego realizar una clase de Agentes los cuales estaran buscando en el mapa la llegada.
    
    En el mapa de campus la forma general es que se tiene un lugar y para decidir si tiene pisos y/o ascensor se usa un parametro llamada "specific_rules" para saber que cambiar y que tomar en cuenta
    
    Intento 2-5: El sistema de navegacion en el campus es malisimo porque se me olvidaron los costos y la heuristica al igual que el subir
    y bajar dentro de un edificio
    
    Intento 5-12: No son agentes, es una funcion de expansion de arbol asique cambie los agentes a la clase AStarSolver
    
    Intento 12-14: El movimiento sigue siendo horrible porque para hacer la expansion necesito que los movimientos se den en AStarSolver y no en el mapa
    
    Intento 14-18: El movimiento es mejor pero la cola esta mal no se porque???
    
    Intento 18-27: adskasakfjldkfjlskjfsl PERO QUE ESTA MAAAAALL
    
    Intento 27-35: Resulta que se me olvido hacer un objeto para representar los estados con una funcion lt definida para el heapqfy :/
    
    Intento 36: Programa terminado
"""