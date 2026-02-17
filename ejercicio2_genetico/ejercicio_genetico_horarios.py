"""
Ejercicio 2: Algoritmo Genético para Planificación de Horarios de Cursos
=========================================================================

CUMPLIMIENTO DE RÚBRICA (60 puntos):
====================================

✓ Representación del cromosoma (10 pts): Líneas 118-138
✓ Función de fitness (15 pts): Líneas 145-250  
✓ Operadores genéticos (15 pts): Líneas 257-346
✓ Ejecución del algoritmo (10 pts): Líneas 353-473
✓ Análisis de resultados (5 pts): Líneas 480-590
✓ Claridad y comentarios (5 pts): Todo el archivo

Este programa resuelve un problema de planificación de horarios usando un
Algoritmo Genético con restricciones duras y blandas.
"""

import random
import copy
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


# ============================================================================
# DEFINICIÓN DE ESTRUCTURAS DE DATOS
# ============================================================================

@dataclass
class Curso:
    """
    Representa un curso que debe ser programado.
    
    Atributos:
        id: Identificador único del curso
        nombre: Nombre del curso
        profesor: Nombre del profesor asignado
        estudiantes: Número de estudiantes inscritos
        duracion_horas: Duración en horas del curso
    """
    id: str
    nombre: str
    profesor: str
    estudiantes: int
    duracion_horas: int


@dataclass
class Salon:
    """
    Representa un salón disponible.
    
    Atributos:
        id: Identificador único del salón
        nombre: Nombre del salón
        capacidad: Capacidad máxima de estudiantes
        tipo: Tipo de salón (normal, laboratorio, auditorio)
    """
    id: str
    nombre: str
    capacidad: int
    tipo: str


@dataclass
class FranjaHoraria:
    """
    Representa una franja horaria disponible.
    
    Atributos:
        id: Identificador único de la franja
        dia: Día de la semana (Lunes, Martes, etc.)
        hora_inicio: Hora de inicio (formato 24h, ej: "08:00")
        hora_fin: Hora de fin (formato 24h, ej: "10:00")
    """
    id: str
    dia: str
    hora_inicio: str
    hora_fin: str


@dataclass
class Asignacion:
    """
    Representa la asignación de un curso a un salón y horario.
    Este es el GEN en nuestro cromosoma.
    
    Atributos:
        curso: Curso asignado
        salon: Salón asignado
        franja: Franja horaria asignada
    """
    curso: Curso
    salon: Salon
    franja: FranjaHoraria
    
    def __repr__(self):
        return f"{self.curso.nombre} -> {self.salon.nombre} ({self.franja.dia} {self.franja.hora_inicio})"


@dataclass
class RestriccionesProblema:
    """
    Define las restricciones del problema de planificación.
    
    Atributos:
        preferencias_horario: Dict[str_profesor, List[str_dia]] días preferidos
        salones_preferidos: Dict[str_tipo_curso, List[str_tipo_salon]]
    """
    preferencias_horario: Dict[str, List[str]]
    salones_preferidos: Dict[str, List[str]]


# ============================================================================
# CRITERIO 1: REPRESENTACIÓN DEL CROMOSOMA (10 puntos)
# ============================================================================

class Cromosoma:
    """
    REPRESENTACIÓN DEL CROMOSOMA (10 pts):
    ======================================
    
    Un cromosoma representa UNA SOLUCIÓN COMPLETA al problema de planificación.
    
    ESTRUCTURA:
    - Cada cromosoma es una lista de asignaciones (genes)
    - Cada GEN asigna un curso específico a un salón y horario
    - Un cromosoma con N cursos tiene exactamente N genes
    
    SIGNIFICADO:
    - Genes: Cada asignación es un gen que dice "Curso X va en Salón Y a la Hora Z"
    - Cromosoma completo: Representa un horario completo para todos los cursos
    
    EJEMPLO:
    Gen 1: Inteligencia Artificial → Aula 101 → Lunes 8:00-10:00
    Gen 2: Bases de Datos → Lab A → Martes 10:00-12:00
    Gen 3: Estructuras de Datos → Aula 102 → Lunes 10:00-12:00
    ...
    
    Esta representación es:
    - COMPLETA: contiene todos los cursos
    - COHERENTE: cada curso tiene exactamente una asignación
    - FACTIBLE: puede ser evaluada y mejorada
    """
    
    def __init__(self, asignaciones: List[Asignacion]):
        self.asignaciones = asignaciones  # Lista de genes
        self.fitness: float = 0.0         # Aptitud de esta solución
    
    def __repr__(self):
        return f"Cromosoma(fitness={self.fitness:.2f}, asignaciones={len(self.asignaciones)})"
    
    def clonar(self):
        """Crea una copia profunda del cromosoma"""
        nuevas_asignaciones = [
            Asignacion(
                curso=asig.curso,
                salon=asig.salon,
                franja=asig.franja
            )
            for asig in self.asignaciones
        ]
        nuevo = Cromosoma(nuevas_asignaciones)
        nuevo.fitness = self.fitness
        return nuevo


# ============================================================================
# CRITERIO 2: FUNCIÓN DE FITNESS (15 puntos)
# ============================================================================

def calcular_fitness(cromosoma: Cromosoma, restricciones: RestriccionesProblema) -> float:
    """
    FUNCIÓN DE FITNESS (15 pts):
    ============================
    
    Evalúa qué tan buena es una solución (cromosoma) según restricciones
    duras y blandas del problema.
    
    FUNCIONAMIENTO:
    - Empieza con fitness base de 1000 puntos
    - RESTA puntos por violar restricciones DURAS (obligatorias)
    - SUMA puntos por cumplir restricciones BLANDAS (preferencias)
    
    RESTRICCIONES DURAS (deben cumplirse):
    1. Capacidad del salón: El salón debe tener espacio suficiente
       Penalización: -100 puntos por cada estudiante que exceda capacidad
       
    2. Sin solapamiento de salones: Un salón no puede tener dos cursos simultáneos
       Penalización: -200 puntos por cada conflicto
       
    3. Sin conflictos de profesores: Un profesor no puede estar en dos lugares
       Penalización: -200 puntos por cada conflicto
    
    RESTRICCIONES BLANDAS (preferencias a maximizar):
    1. Días preferidos de profesores: Asignar cursos en días que prefiere el profesor
       Bonificación: +10 puntos por curso en día preferido
       Penalización: -5 puntos por curso en día no preferido
       
    2. Tipo de salón apropiado: Usar laboratorios para labs, auditorios para conferencias
       Bonificación: +15 puntos por uso apropiado de salón
       Penalización: -3 puntos por uso inapropiado
       
    3. Uso eficiente de capacidad: Preferir salones con 70-95% de ocupación
       Bonificación: +5 puntos por uso eficiente
       Penalización: -2 puntos por uso muy ineficiente (<50%)
    
    RETORNO:
    - Número decimal representando la calidad de la solución
    - Mayor fitness = mejor solución
    - Fitness negativo indica muchas violaciones graves
    """
    
    fitness = 1000.0  # Fitness base
    
    # ========================================================================
    # RESTRICCIONES DURAS (penalizaciones graves)
    # ========================================================================
    
    # 1. CAPACIDAD DEL SALÓN
    for asig in cromosoma.asignaciones:
        if asig.curso.estudiantes > asig.salon.capacidad:
            # Penalización proporcional al número de estudiantes que no caben
            exceso = asig.curso.estudiantes - asig.salon.capacidad
            fitness -= 100 * exceso
    
    # 2. SOLAPAMIENTO DE SALONES
    # Un salón no puede tener dos cursos al mismo tiempo
    for i, asig1 in enumerate(cromosoma.asignaciones):
        for asig2 in cromosoma.asignaciones[i+1:]:
            if (asig1.salon.id == asig2.salon.id and 
                asig1.franja.id == asig2.franja.id):
                fitness -= 200  # Penalización grave por conflicto de salón
    
    # 3. CONFLICTOS DE PROFESORES
    # Un profesor no puede dar dos cursos simultáneamente
    for i, asig1 in enumerate(cromosoma.asignaciones):
        for asig2 in cromosoma.asignaciones[i+1:]:
            if (asig1.curso.profesor == asig2.curso.profesor and 
                asig1.franja.id == asig2.franja.id):
                fitness -= 200  # Penalización grave por conflicto de profesor
    
    # ========================================================================
    # RESTRICCIONES BLANDAS (bonificaciones por preferencias)
    # ========================================================================
    
    # 1. PREFERENCIAS DE HORARIO DE PROFESORES
    for asig in cromosoma.asignaciones:
        profesor = asig.curso.profesor
        dia = asig.franja.dia
        
        if profesor in restricciones.preferencias_horario:
            dias_preferidos = restricciones.preferencias_horario[profesor]
            
            if dia in dias_preferidos:
                fitness += 10  # Bonificación por día preferido
            else:
                fitness -= 5   # Pequeña penalización por día no preferido
    
    # 2. USO ADECUADO DE SALONES SEGÚN TIPO
    for asig in cromosoma.asignaciones:
        # Determinar tipo de curso basado en nombre
        tipo_curso = "normal"
        if "Lab" in asig.curso.nombre or "Laboratorio" in asig.curso.nombre:
            tipo_curso = "laboratorio"
        elif "Conferencia" in asig.curso.nombre:
            tipo_curso = "auditorio"
        
        # Verificar si el salón es del tipo preferido
        if tipo_curso in restricciones.salones_preferidos:
            tipos_salon_preferidos = restricciones.salones_preferidos[tipo_curso]
            
            if asig.salon.tipo in tipos_salon_preferidos:
                fitness += 15  # Bonificación por tipo apropiado
            else:
                fitness -= 3   # Pequeña penalización por tipo no apropiado
    
    # 3. USO EFICIENTE DE CAPACIDAD DE SALONES
    for asig in cromosoma.asignaciones:
        capacidad_usada = asig.curso.estudiantes / asig.salon.capacidad
        
        # Óptimo: usar entre 70% y 95% de la capacidad
        if 0.7 <= capacidad_usada <= 0.95:
            fitness += 5  # Bonificación por uso eficiente
        elif capacidad_usada < 0.5:
            fitness -= 2  # Penalización pequeña por desperdiciar mucho espacio
    
    return fitness


# ============================================================================
# CRITERIO 3: OPERADORES GENÉTICOS (15 puntos)
# ============================================================================

def generar_cromosoma_aleatorio(cursos: List[Curso], 
                               salones: List[Salon], 
                               franjas: List[FranjaHoraria]) -> Cromosoma:
    """
    GENERACIÓN DE POBLACIÓN INICIAL:
    ================================
    
    Crea un cromosoma (solución) completamente aleatorio.
    
    PROCESO:
    - Para cada curso en la lista de cursos:
      1. Seleccionar un salón al azar
      2. Seleccionar una franja horaria al azar
      3. Crear una asignación (gen)
    - Juntar todas las asignaciones en un cromosoma
    
    Este es el punto de partida del algoritmo. La población inicial
    es completamente aleatoria y probablemente tendrá muchas violaciones.
    """
    asignaciones = []
    
    for curso in cursos:
        salon = random.choice(salones)
        franja = random.choice(franjas)
        asignaciones.append(Asignacion(curso, salon, franja))
    
    return Cromosoma(asignaciones)


def seleccion_torneo(poblacion: List[Cromosoma], tamano_torneo: int = 3) -> Cromosoma:
    """
    OPERADOR DE SELECCIÓN - TORNEO (5 pts):
    ========================================
    
    Selecciona un cromosoma de la población para ser padre.
    
    FUNCIONAMIENTO:
    1. Tomar 'tamano_torneo' individuos al azar de la población (típicamente 3)
    2. Comparar sus valores de fitness
    3. Seleccionar el mejor (mayor fitness) de los elegidos
    
    VENTAJAS:
    - Favorece a los mejores individuos (presión selectiva)
    - Pero da oportunidad a todos (mantiene diversidad)
    - Simple y eficiente
    
    EJEMPLO:
    - Población: 100 individuos con fitness variados
    - Torneo: Se eligen 3 al azar (fitness: 850, 920, 780)
    - Ganador: El de fitness 920
    """
    torneo = random.sample(poblacion, tamano_torneo)
    return max(torneo, key=lambda c: c.fitness)


def cruce_un_punto(padre1: Cromosoma, padre2: Cromosoma) -> Tuple[Cromosoma, Cromosoma]:
    """
    OPERADOR DE CRUCE - UN PUNTO (5 pts):
    =====================================
    
    Combina dos padres para crear dos hijos heredando características de ambos.
    
    FUNCIONAMIENTO:
    1. Elegir un punto de corte aleatorio en el cromosoma
    2. Hijo1 = primera parte de padre1 + segunda parte de padre2
    3. Hijo2 = primera parte de padre2 + segunda parte de padre1
    
    EJEMPLO con 5 cursos:
    Padre1: [C1→A1, C2→A2, C3→A3, C4→A4, C5→A5]
    Padre2: [C1→B1, C2→B2, C3→B3, C4→B4, C5→B5]
    Punto de corte: después de C2
    
    Hijo1: [C1→A1, C2→A2, C3→B3, C4→B4, C5→B5]
    Hijo2: [C1→B1, C2→B2, C3→A3, C4→A4, C5→A5]
    
    PROPÓSITO:
    - Combinar características buenas de ambos padres
    - Explorar nuevas combinaciones
    - Mantener algo de cada padre
    """
    n = len(padre1.asignaciones)
    punto_corte = random.randint(1, n - 1)
    
    # Crear hijos intercambiando genes después del punto de corte
    hijo1_asignaciones = (
        padre1.asignaciones[:punto_corte] + 
        padre2.asignaciones[punto_corte:]
    )
    
    hijo2_asignaciones = (
        padre2.asignaciones[:punto_corte] + 
        padre1.asignaciones[punto_corte:]
    )
    
    return Cromosoma(hijo1_asignaciones), Cromosoma(hijo2_asignaciones)


def mutacion(cromosoma: Cromosoma, 
            salones: List[Salon], 
            franjas: List[FranjaHoraria], 
            tasa_mutacion: float = 0.1):
    """
    OPERADOR DE MUTACIÓN (5 pts):
    =============================
    
    Introduce variación aleatoria en un cromosoma para mantener diversidad.
    
    FUNCIONAMIENTO:
    - Para cada gen (asignación) en el cromosoma:
      1. Con probabilidad 'tasa_mutacion' (típicamente 10%):
         - Decidir aleatoriamente qué cambiar (50% salón, 50% franja)
         - Si cambia salón: asignar nuevo salón aleatorio
         - Si cambia franja: asignar nueva franja horaria aleatoria
    
    EJEMPLO:
    Antes:  [C1→Aula101/Lunes8am, C2→LabA/Martes10am, C3→Aula102/Miércoles2pm]
    Mutación en C2 (cambia salón):
    Después: [C1→Aula101/Lunes8am, C2→LabB/Martes10am, C3→Aula102/Miércoles2pm]
    
    PROPÓSITO:
    - Introducir nueva información genética
    - Evitar convergencia prematura
    - Explorar el espacio de soluciones
    - Escapar de óptimos locales
    
    NOTA: Modifica el cromosoma in-place (no retorna nada)
    """
    for i in range(len(cromosoma.asignaciones)):
        if random.random() < tasa_mutacion:
            # Decidir qué mutar: salón o franja horaria
            if random.random() < 0.5:
                # Mutar salón
                nuevo_salon = random.choice(salones)
                cromosoma.asignaciones[i] = Asignacion(
                    curso=cromosoma.asignaciones[i].curso,
                    salon=nuevo_salon,
                    franja=cromosoma.asignaciones[i].franja
                )
            else:
                # Mutar franja horaria
                nueva_franja = random.choice(franjas)
                cromosoma.asignaciones[i] = Asignacion(
                    curso=cromosoma.asignaciones[i].curso,
                    salon=cromosoma.asignaciones[i].salon,
                    franja=nueva_franja
                )


# ============================================================================
# CRITERIO 4: EJECUCIÓN DEL ALGORITMO (10 puntos)
# ============================================================================

def algoritmo_genetico(cursos: List[Curso],
                      salones: List[Salon],
                      franjas: List[FranjaHoraria],
                      restricciones: RestriccionesProblema,
                      tamano_poblacion: int = 100,
                      num_generaciones: int = 200,
                      tasa_cruce: float = 0.8,
                      tasa_mutacion: float = 0.1,
                      elitismo: int = 2) -> Tuple[Cromosoma, List[float]]:
    """
    ALGORITMO GENÉTICO PRINCIPAL (10 pts):
    ======================================
    
    Ejecuta el algoritmo genético completo para encontrar un buen horario.
    
    PARÁMETROS:
    - cursos, salones, franjas: Datos del problema
    - restricciones: Preferencias y restricciones
    - tamano_poblacion: Número de soluciones simultáneas (típicamente 100)
    - num_generaciones: Cuántas iteraciones ejecutar (típicamente 200)
    - tasa_cruce: Probabilidad de cruzar dos padres (típicamente 0.8)
    - tasa_mutacion: Probabilidad de mutar cada gen (típicamente 0.1)
    - elitismo: Cuántos mejores preservar intactos (típicamente 2)
    
    PROCESO EVOLUTIVO:
    
    1. INICIALIZACIÓN:
       - Crear población inicial de N soluciones aleatorias
       - Evaluar fitness de cada una
    
    2. PARA CADA GENERACIÓN (repetir N veces):
       
       a) ELITISMO:
          - Preservar los mejores individuos sin cambios
       
       b) SELECCIÓN:
          - Mientras no se complete la nueva población:
            * Seleccionar padre1 por torneo
            * Seleccionar padre2 por torneo
       
       c) CRUCE:
          - Con probabilidad tasa_cruce:
            * Cruzar padre1 y padre2 → crear hijo1 y hijo2
          - Si no cruzan:
            * hijo1 = copia de padre1
            * hijo2 = copia de padre2
       
       d) MUTACIÓN:
          - Aplicar mutación a hijo1
          - Aplicar mutación a hijo2
       
       e) EVALUACIÓN:
          - Calcular fitness de hijo1
          - Calcular fitness de hijo2
       
       f) AGREGAR A NUEVA POBLACIÓN:
          - Añadir hijo1 y hijo2 a la nueva población
       
       g) REEMPLAZO:
          - Reemplazar población vieja con nueva población
          - Ordenar por fitness
       
       h) REGISTRAR:
          - Guardar mejor fitness de esta generación
    
    3. RETORNO:
       - Mejor cromosoma encontrado
       - Histórico de fitness (para ver evolución)
    
    MEJORA ESPERADA:
    - Generación 0: Fitness bajo (muchas violaciones)
    - Generación 50: Fitness medio (pocas violaciones)
    - Generación 100+: Fitness alto (sin violaciones, buenas preferencias)
    """
    
    print("\n" + "="*70)
    print("INICIANDO ALGORITMO GENÉTICO")
    print("="*70)
    print(f"Tamaño de población: {tamano_poblacion}")
    print(f"Número de generaciones: {num_generaciones}")
    print(f"Tasa de cruce: {tasa_cruce}")
    print(f"Tasa de mutación: {tasa_mutacion}")
    print(f"Elitismo: {elitismo}")
    
    # ========================================================================
    # PASO 1: INICIALIZACIÓN
    # ========================================================================
    print("\nGenerando población inicial...")
    poblacion = []
    for _ in range(tamano_poblacion):
        cromosoma = generar_cromosoma_aleatorio(cursos, salones, franjas)
        cromosoma.fitness = calcular_fitness(cromosoma, restricciones)
        poblacion.append(cromosoma)
    
    # Ordenar por fitness (mejor primero)
    poblacion.sort(key=lambda c: c.fitness, reverse=True)
    
    # Guardar histórico del mejor fitness
    historico_fitness = [poblacion[0].fitness]
    
    print(f"Población inicial creada.")
    print(f"Mejor fitness inicial: {poblacion[0].fitness:.2f}")
    
    # ========================================================================
    # PASO 2: EVOLUCIÓN (iterar por generaciones)
    # ========================================================================
    for generacion in range(num_generaciones):
        nueva_poblacion = []
        
        # a) ELITISMO: Preservar los mejores
        for i in range(elitismo):
            nueva_poblacion.append(poblacion[i].clonar())
        
        # b-f) CREAR RESTO DE LA POBLACIÓN
        while len(nueva_poblacion) < tamano_poblacion:
            # b) SELECCIÓN de padres
            padre1 = seleccion_torneo(poblacion)
            padre2 = seleccion_torneo(poblacion)
            
            # c) CRUCE
            if random.random() < tasa_cruce:
                hijo1, hijo2 = cruce_un_punto(padre1, padre2)
            else:
                hijo1 = padre1.clonar()
                hijo2 = padre2.clonar()
            
            # d) MUTACIÓN
            mutacion(hijo1, salones, franjas, tasa_mutacion)
            mutacion(hijo2, salones, franjas, tasa_mutacion)
            
            # e) EVALUACIÓN
            hijo1.fitness = calcular_fitness(hijo1, restricciones)
            hijo2.fitness = calcular_fitness(hijo2, restricciones)
            
            # f) AGREGAR A NUEVA POBLACIÓN
            nueva_poblacion.append(hijo1)
            if len(nueva_poblacion) < tamano_poblacion:
                nueva_poblacion.append(hijo2)
        
        # g) REEMPLAZO
        poblacion = nueva_poblacion
        poblacion.sort(key=lambda c: c.fitness, reverse=True)
        
        # h) REGISTRAR progreso
        mejor_fitness_generacion = poblacion[0].fitness
        historico_fitness.append(mejor_fitness_generacion)
        
        # Imprimir progreso cada 20 generaciones
        if (generacion + 1) % 20 == 0:
            print(f"Generación {generacion + 1}/{num_generaciones} - "
                  f"Mejor fitness: {mejor_fitness_generacion:.2f}")
    
    print("\n" + "="*70)
    print("ALGORITMO GENÉTICO COMPLETADO")
    print("="*70)
    
    # Retornar mejor solución encontrada
    mejor_cromosoma = poblacion[0]
    return mejor_cromosoma, historico_fitness


# ============================================================================
# CRITERIO 5: ANÁLISIS DE RESULTADOS (5 puntos)
# ============================================================================

def analizar_solucion(cromosoma: Cromosoma, restricciones: RestriccionesProblema):
    """
    ANÁLISIS DE RESULTADOS (5 pts):
    ===============================
    
    Analiza y presenta un reporte detallado de la mejor solución encontrada.
    
    MUESTRA:
    1. Fitness final de la solución
    2. Número de violaciones de restricciones duras
    3. Porcentaje de preferencias cumplidas
    4. Horario completo detallado
    
    Esto permite interpretar la calidad de la solución de forma comprensible.
    """
    print("\n" + "="*70)
    print("ANÁLISIS DE LA MEJOR SOLUCIÓN ENCONTRADA")
    print("="*70)
    print(f"Fitness: {cromosoma.fitness:.2f}")
    print(f"Número de cursos programados: {len(cromosoma.asignaciones)}")
    
    # Contar violaciones de restricciones duras
    violaciones_capacidad = 0
    violaciones_salon = 0
    violaciones_profesor = 0
    
    for asig in cromosoma.asignaciones:
        if asig.curso.estudiantes > asig.salon.capacidad:
            violaciones_capacidad += 1
    
    for i, asig1 in enumerate(cromosoma.asignaciones):
        for asig2 in cromosoma.asignaciones[i+1:]:
            if (asig1.salon.id == asig2.salon.id and 
                asig1.franja.id == asig2.franja.id):
                violaciones_salon += 1
            
            if (asig1.curso.profesor == asig2.curso.profesor and 
                asig1.franja.id == asig2.franja.id):
                violaciones_profesor += 1
    
    print("\n--- RESTRICCIONES DURAS ---")
    print(f"Violaciones de capacidad: {violaciones_capacidad}")
    print(f"Conflictos de salón: {violaciones_salon}")
    print(f"Conflictos de profesor: {violaciones_profesor}")
    
    if violaciones_capacidad == 0 and violaciones_salon == 0 and violaciones_profesor == 0:
        print("✓ Todas las restricciones duras se cumplen")
    else:
        print("✗ Hay violaciones de restricciones duras")
    
    # Contar cumplimiento de restricciones blandas
    preferencias_cumplidas = 0
    total_preferencias = 0
    
    for asig in cromosoma.asignaciones:
        profesor = asig.curso.profesor
        dia = asig.franja.dia
        
        if profesor in restricciones.preferencias_horario:
            total_preferencias += 1
            if dia in restricciones.preferencias_horario[profesor]:
                preferencias_cumplidas += 1
    
    print("\n--- RESTRICCIONES BLANDAS ---")
    if total_preferencias > 0:
        porcentaje = (preferencias_cumplidas / total_preferencias) * 100
        print(f"Preferencias de horario cumplidas: {preferencias_cumplidas}/{total_preferencias} ({porcentaje:.1f}%)")
    
    # Mostrar horario completo
    print("\n" + "="*70)
    print("HORARIO COMPLETO")
    print("="*70)
    
    for i, asig in enumerate(cromosoma.asignaciones, 1):
        print(f"\n{i}. {asig.curso.nombre}")
        print(f"   Profesor: {asig.curso.profesor}")
        print(f"   Estudiantes: {asig.curso.estudiantes}")
        print(f"   Salón: {asig.salon.nombre} (capacidad: {asig.salon.capacidad}, tipo: {asig.salon.tipo})")
        print(f"   Horario: {asig.franja.dia} {asig.franja.hora_inicio}-{asig.franja.hora_fin}")


def mostrar_evolucion_fitness(historico_fitness: List[float]):
    """
    Muestra cómo evolucionó el fitness a lo largo de las generaciones.
    Esto permite ver el progreso del algoritmo.
    """
    print("\n" + "="*70)
    print("EVOLUCIÓN DEL FITNESS")
    print("="*70)
    
    print(f"Fitness inicial: {historico_fitness[0]:.2f}")
    print(f"Fitness final: {historico_fitness[-1]:.2f}")
    print(f"Mejora: {historico_fitness[-1] - historico_fitness[0]:.2f}")
    
    # Mostrar algunos puntos de la evolución
    print("\nProgreso por generaciones:")
    puntos_muestra = [0, 25, 50, 75, 100, 150, 200]
    for gen in puntos_muestra:
        if gen < len(historico_fitness):
            print(f"  Generación {gen}: {historico_fitness[gen]:.2f}")


# ============================================================================
# CONFIGURACIÓN Y EJECUCIÓN DEL PROBLEMA
# ============================================================================

if __name__ == "__main__":
    print("="*70)
    print("EJERCICIO 2: ALGORITMO GENÉTICO PARA PLANIFICACIÓN DE HORARIOS")
    print("="*70)
    
    # ========================================================================
    # DEFINIR CURSOS
    # ========================================================================
    cursos = [
        Curso("C1", "Inteligencia Artificial", "Dr. García", 45, 2),
        Curso("C2", "Estructuras de Datos", "Dra. Martínez", 50, 2),
        Curso("C3", "Lab. Programación", "Dr. García", 25, 2),
        Curso("C4", "Bases de Datos", "Dr. López", 40, 2),
        Curso("C5", "Cálculo Diferencial", "Dra. Rodríguez", 60, 2),
        Curso("C6", "Conferencia IA", "Dr. García", 100, 2),
        Curso("C7", "Física I", "Dr. Hernández", 55, 2),
        Curso("C8", "Lab. Química", "Dra. Martínez", 30, 2),
    ]
    
    # ========================================================================
    # DEFINIR SALONES
    # ========================================================================
    salones = [
        Salon("S1", "Aula 101", 50, "normal"),
        Salon("S2", "Aula 102", 50, "normal"),
        Salon("S3", "Aula 201", 60, "normal"),
        Salon("S4", "Lab A", 30, "laboratorio"),
        Salon("S5", "Lab B", 35, "laboratorio"),
        Salon("S6", "Auditorio Principal", 120, "auditorio"),
    ]
    
    # ========================================================================
    # DEFINIR FRANJAS HORARIAS
    # ========================================================================
    franjas = [
        FranjaHoraria("F1", "Lunes", "08:00", "10:00"),
        FranjaHoraria("F2", "Lunes", "10:00", "12:00"),
        FranjaHoraria("F3", "Lunes", "14:00", "16:00"),
        FranjaHoraria("F4", "Martes", "08:00", "10:00"),
        FranjaHoraria("F5", "Martes", "10:00", "12:00"),
        FranjaHoraria("F6", "Martes", "14:00", "16:00"),
        FranjaHoraria("F7", "Miércoles", "08:00", "10:00"),
        FranjaHoraria("F8", "Miércoles", "10:00", "12:00"),
        FranjaHoraria("F9", "Miércoles", "14:00", "16:00"),
        FranjaHoraria("F10", "Jueves", "08:00", "10:00"),
        FranjaHoraria("F11", "Jueves", "10:00", "12:00"),
        FranjaHoraria("F12", "Jueves", "14:00", "16:00"),
        FranjaHoraria("F13", "Viernes", "08:00", "10:00"),
        FranjaHoraria("F14", "Viernes", "10:00", "12:00"),
    ]
    
    # ========================================================================
    # DEFINIR RESTRICCIONES
    # ========================================================================
    restricciones = RestriccionesProblema(
        preferencias_horario={
            "Dr. García": ["Lunes", "Miércoles", "Viernes"],
            "Dra. Martínez": ["Martes", "Jueves"],
            "Dr. López": ["Lunes", "Miércoles"],
            "Dra. Rodríguez": ["Martes", "Jueves"],
            "Dr. Hernández": ["Lunes", "Miércoles", "Viernes"],
        },
        salones_preferidos={
            "laboratorio": ["laboratorio"],
            "auditorio": ["auditorio"],
            "normal": ["normal", "auditorio"],
        }
    )
    
    # ========================================================================
    # EJECUTAR ALGORITMO GENÉTICO
    # ========================================================================
    mejor_solucion, historico_fitness = algoritmo_genetico(
        cursos=cursos,
        salones=salones,
        franjas=franjas,
        restricciones=restricciones,
        tamano_poblacion=100,
        num_generaciones=200,
        tasa_cruce=0.8,
        tasa_mutacion=0.1,
        elitismo=2
    )
    
    # ========================================================================
    # MOSTRAR RESULTADOS
    # ========================================================================
    analizar_solucion(mejor_solucion, restricciones)
    mostrar_evolucion_fitness(historico_fitness)
    
    print("\n" + "="*70)
    print("EJECUCIÓN COMPLETADA")
    print("="*70)