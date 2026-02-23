from ejercicio_astar_campus import AStarSolver

# Ruta en Campus con A* (Resumen)

Este módulo implementa una búsqueda de ruta en un mapa de campus usando el algoritmo **A***. Permite calcular un camino entre dos ubicaciones (con piso) considerando paredes, ascensores y costos de movimiento.

## Estructura

- **`Campus`**:  
  - Construye el mapa interno (`main_map`) a partir de una matriz de símbolos.
  - Identifica **punto inicial** y **punto final** en función de un símbolo y un piso deseado.
  - Define utilidades: límites del mapa, verificación de fin, y **heurística** (distancia euclidiana en planta).

- **`State`**:  
  - Contenedor para usar en la **cola de prioridad** (`heapq`), con comparación por costo.

- **`AStarSolver`**:  
  - Resuelve el camino con **A***.
  - Genera **vecinos** (4 direcciones en planta + subir/bajar piso).
  - Asigna **costos** por movimiento:
    - Horizontal/vertical: `1`
    - Cambio de piso:
      - Con ascensor en destino: `3`
      - Sin ascensor: `5` al bajar, `7` al subir

## Mapa de Entrada

- Matriz `init_map` de tamaño `rows x cols`.
- Cada celda puede ser:
  - `" "` (transitable), `"#"` (muro),
  - Un **símbolo** (ej. `"B31"`) o una **tupla** `(simbolo, pisos[, ascensor_flag])`.
- Ejemplo de edificio con ascensor y 3 pisos:
  ```python
  ("B33", 3, True)
  ```

## Inicio y Destino

- Se pasan como tuplas: `(simbolo, piso)`
- El código busca en el mapa una celda cuyo **símbolo** coincida y ajusta el piso al rango `[0, pisos-1]`.

## Heurística

- Distancia euclidiana 2D entre la posición actual y el destino **ignorando** diferencias de piso.

## Flujo Básico

1. Crear el `Campus` con el mapa, inicio y fin.
2. Instanciar `AStarSolver(campus)`.
3. Llamar `solve()` → devuelve `(camino, costo_total)`:
   - **`camino`**: lista de tuplas `(x, y, piso)` desde inicio a fin.
   - **`costo_total`**: costo acumulado del último estado extraído al llegar al destino.

## Ejemplo de Uso

```python
import ejercicio_astar_campus as asc

m = [
  [" ", "#", " ", " ", "#", " ", " ", "#", " ", " ", "#", " ", " ", "#", " ", " ", " "],
  # ...
  [" ", " ", " ", " ", "#", " ", "C", " ", "#", " ", "#", " ", " ", " ", "B", " ", " "],
  # ...
]

path, cost = asc.AStarSolver(asc.Campus(m, ("B30", 0), ("B37", 2))).solve()
print(path, cost)
```

## Convenciones y Coordenadas

- Las posiciones se manejan como `(x, y, piso)` donde:
  - `x` es columna (j),
  - `y` es fila (i),
  - `piso` es entero (0 a `pisos-1`).
- `Campus.en_limites(i, j)` usa formato `(fila, columna)` internamente al validar límites.

## Consideraciones

- Si no se encuentra el simbolo de inicio/fin en el mapa, se lanza `ValueError`.
- La validación de pisos impide valores negativos o superiores al máximo permitido por celda.
- Se pide usar nombres diferentes para los pisos iniciales y finales

## Requisitos

- Python estándar (`math`, `heapq`). No requiere dependencias externas.

## Salida Típica

- **Camino**: lista ordenada de estados desde inicio a fin.
- **Costo**: número que refleja la función `f` acumulada de A* al momento de alcanzar el destino.
