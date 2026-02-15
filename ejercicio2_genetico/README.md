# Ejercicio 2: Algoritmo Genético para Planificación de Horarios

## Descripción

Este ejercicio implementa un algoritmo genético completo para resolver el problema de planificación de horarios universitarios, cumpliendo con restricciones duras y maximizando preferencias.

## Contenido

### Implementación Principal
- `ejercicio_genetico_horarios.py` - Código completo del algoritmo genético
  - Representación de cromosomas
  - Función de fitness con restricciones duras y blandas
  - Operadores genéticos (selección, cruce, mutación)
  - Elitismo
  - Análisis detallado de resultados

### Experimentos
- `experimentos_genetico.py` - 7 experimentos diferentes
  1. Tamaño de población (20, 50, 100, 200)
  2. Número de generaciones (50, 100, 200, 300)
  3. Tasa de mutación (0.01, 0.05, 0.1, 0.2, 0.3)
  4. Tasa de cruce (0.5, 0.7, 0.8, 0.9, 1.0)
  5. Elitismo (0, 1, 2, 5, 10)
  6. Escalabilidad del problema
  7. Convergencia temporal

### Resultados
- `resultado_genetico.txt` - Salida del ejercicio principal
- `resultados_experimentos_genetico.txt` - Salida de todos los experimentos

### Documentación
- `README.md` - Este archivo
- `EXPLICACION_COMPLETA.txt` - Explicación detallada del código
- `DOCUMENTACION_EXPERIMENTOS.txt` - Análisis completo de experimentos

## Problema a Resolver

Asignar horarios a cursos universitarios considerando:

**Restricciones Duras (deben cumplirse):**
- Capacidad del salón debe ser suficiente para los estudiantes
- No puede haber dos cursos en el mismo salón al mismo tiempo
- Un profesor no puede estar en dos lugares simultáneamente

**Restricciones Blandas (preferencias a maximizar):**
- Preferencias de días de los profesores
- Uso apropiado de salones según tipo de curso
- Uso eficiente de la capacidad de los salones

## Datos de Prueba

El ejercicio principal incluye:
- 8 cursos diferentes
- 6 salones (diferentes capacidades y tipos)
- 14 franjas horarias (Lunes a Viernes)
- Preferencias de horario para cada profesor

## Cómo Ejecutar

### Ejercicio Principal
```bash
python3 ejercicio_genetico_horarios.py
```

Esto ejecutará el algoritmo genético con 200 generaciones y mostrará:
- Evolución del fitness
- Mejor solución encontrada
- Análisis de restricciones
- Horario completo

### Experimentos
```bash
python3 experimentos_genetico.py
```

Esto ejecutará los 7 experimentos y mostrará:
- Comparación de diferentes configuraciones
- Análisis de cada parámetro
- Conclusiones y recomendaciones

## Requisitos

- Python 3.6 o superior
- No requiere librerías externas (solo biblioteca estándar)

## Características del Código

- **Completamente comentado** en español
- **Nombres descriptivos** de variables y funciones
- **Estructura clara** con clases bien definidas
- **Fácil de modificar** y extender

## Resultados Esperados

### Ejercicio Principal
El algoritmo encuentra un horario que:
- No viola ninguna restricción dura
- Cumple el 100% de las preferencias
- Usa eficientemente los recursos
- Fitness típico: 1235

### Experimentos
Los experimentos demuestran que:
- Población óptima: 100 individuos
- Generaciones óptimas: 200
- Tasa de mutación óptima: 0.1 (10%)
- Tasa de cruce óptima: 0.8 (80%)
- Elitismo óptimo: 2 individuos

## Estructura del Algoritmo

1. **Inicialización**: Genera 100 soluciones aleatorias
2. **Evaluación**: Calcula fitness de cada solución
3. **Selección**: Elige padres por torneo (los mejores tienen más probabilidad)
4. **Cruce**: Combina dos padres para crear dos hijos
5. **Mutación**: Introduce variación aleatoria
6. **Elitismo**: Preserva los 2 mejores
7. **Reemplazo**: Nueva generación reemplaza a la anterior
8. **Repetir**: Pasos 2-7 por 200 generaciones

## Función de Fitness

```
Fitness inicial = 1000

Penalizaciones (restricciones duras):
  - Capacidad excedida: -100 por estudiante extra
  - Conflicto de salón: -200
  - Conflicto de profesor: -200

Bonificaciones (restricciones blandas):
  - Día preferido del profesor: +10
  - Tipo de salón apropiado: +15
  - Uso eficiente (70-95%): +5

Fitness final = valor resultante (mayor es mejor)
```

## Operadores Genéticos

### Selección por Torneo
- Toma 3 individuos al azar
- Elige el mejor de los 3
- Favorece buenos individuos sin eliminar diversidad

### Cruce de Un Punto
- Elige punto de corte aleatorio
- Hijo1 = primera parte padre1 + segunda parte padre2
- Hijo2 = primera parte padre2 + segunda parte padre1
- Probabilidad: 80%

### Mutación
- Cada gen tiene 10% de probabilidad de mutar
- Si muta: cambia salón O franja horaria
- Introduce exploración del espacio

### Elitismo
- Los 2 mejores pasan intactos a la siguiente generación
- Asegura no perder buenas soluciones

## Experimentos Realizados

### 1. Tamaño de Población
**Objetivo**: Evaluar balance entre diversidad y tiempo de ejecución

**Configuración**: 
- Tamaños: 20, 50, 100, 200
- Generaciones fijas: 100

**Resultado**: 
- 100 es óptimo (buen balance)
- <50 es insuficiente
- >100 mejora marginal

### 2. Número de Generaciones
**Objetivo**: Determinar cuándo converge el algoritmo

**Configuración**:
- Generaciones: 50, 100, 200, 300
- Población fija: 100

**Resultado**:
- 200 generaciones suficientes
- >200 no mejora significativamente

### 3. Tasa de Mutación
**Objetivo**: Encontrar balance exploración/explotación

**Configuración**:
- Tasas: 0.01, 0.05, 0.1, 0.2, 0.3

**Resultado**:
- 0.1 es óptimo
- <0.05 muy conservador
- >0.2 muy disruptivo

### 4. Tasa de Cruce
**Objetivo**: Evaluar importancia del cruce

**Configuración**:
- Tasas: 0.5, 0.7, 0.8, 0.9, 1.0

**Resultado**:
- 0.8 funciona bien
- Menos crítico que mutación

### 5. Elitismo
**Objetivo**: Balancear preservación y diversidad

**Configuración**:
- Valores: 0, 1, 2, 5, 10

**Resultado**:
- 2 es óptimo (2% población)
- 0 puede perder buenas soluciones
- >5 reduce diversidad

### 6. Escalabilidad
**Objetivo**: Verificar que funciona con problemas más grandes

**Configuración**:
- Problema simple: 5 cursos
- Problema complejo: 8 cursos

**Resultado**:
- Escala bien
- Mismos parámetros funcionan

### 7. Convergencia Temporal
**Objetivo**: Ver cómo evoluciona generación por generación

**Resultado**:
- 70% mejora en primeras 50 generaciones
- Convergencia alrededor de generación 100

## Parámetros Óptimos Encontrados

```
Tamaño población: 100
Generaciones: 200
Tasa cruce: 0.8
Tasa mutación: 0.1
Elitismo: 2
```

## Análisis de Resultados

El programa muestra:
- Fitness inicial y final
- Mejora lograda
- Violaciones de restricciones (debe ser 0)
- Porcentaje de preferencias cumplidas
- Horario completo detallado
- Gráfica de evolución del fitness

## Modificar el Problema

Para cambiar los datos del problema, edita en `ejercicio_genetico_horarios.py`:

```python
# Agregar cursos
cursos.append(Curso("C9", "Nuevo Curso", "Profesor", 40, 2))

# Agregar salones
salones.append(Salon("S7", "Nuevo Salón", 45, "normal"))

# Agregar franjas
franjas.append(FranjaHoraria("F15", "Viernes", "14:00", "16:00"))

# Agregar preferencias
preferencias["Profesor"] = ["Lunes", "Miércoles"]
```

## Documentación Adicional

Para entender a fondo cómo funciona:
- Lee `EXPLICACION_COMPLETA.txt` - Explicación detallada del código
- Lee `DOCUMENTACION_EXPERIMENTOS.txt` - Análisis completo de experimentos

## Contribuciones del Ejercicio

Este ejercicio demuestra:
1. Implementación completa de algoritmo genético
2. Manejo de restricciones duras y blandas
3. Operadores genéticos bien diseñados
4. Experimentación sistemática con parámetros
5. Análisis riguroso de resultados
6. Código de producción (comentado, estructurado, robusto)
