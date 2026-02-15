"""
Ejercicio 2: Algoritmo Genético para Planificación de Horarios de Cursos
=========================================================================

Este programa resuelve un problema de planificación de horarios usando un
Algoritmo Genético.

El problema incluye:
- Restricciones duras (capacidad, solapamientos, profesores)
- Restricciones blandas (preferencias de horario y uso de salones)
- Diseño de cromosomas, función de fitness y operadores genéticos
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


# ============================================================================
# RESTRICCIONES Y PREFERENCIAS
# ============================================================================

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
# CROMOSOMA (SOLUCIÓN)
# ============================================================================

class Cromosoma:
    """
    Representa una solución al problema de planificación.
    
    Un cromosoma es una lista de asignaciones (genes), donde cada gen
    asigna un curso a un salón y horario específico.
    
    Atributos:
        asignaciones: Lista de asignaciones curso-salón-horario
        fitness: Valor de fitness (calidad de la solución)
    """
    
    def __init__(self, asignaciones: List[Asignacion]):
        self.asignaciones = asignaciones
        self.fitness: float = 0.0
    
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
# FUNCIÓN DE FITNESS
# ============================================================================

def calcular_fitness(cromosoma: Cromosoma, restricciones: RestriccionesProblema) -> float:
    """
    Calcula el fitness de un cromosoma (solución).
    
    El fitness se calcula como:
    - Penalización por violar restricciones DURAS (muy alto)
    - Bonificación por cumplir restricciones BLANDAS
    
    Un fitness más alto indica una mejor solución.
    
    Restricciones duras:
    1. Capacidad del salón debe ser suficiente
    2. No puede haber solapamientos de salones
    3. Un profesor no puede estar en dos lugares al mismo tiempo
    
    Restricciones blandas (preferencias):
    1. Preferencias de horario de profesores
    2. Uso adecuado de salones según tipo de curso
    
    Retorna:
        fitness: Valor numérico (mayor es mejor)
    """
    
    fitness = 1000.0  # Comenzar con fitness alto
    
    # ========================================================================
    # RESTRICCIONES DURAS (penalizaciones graves)
    # ========================================================================
    
    # 1. Verificar capacidad de salones
    for asig in cromosoma.asignaciones:
        if asig.curso.estudiantes > asig.salon.capacidad:
            # Penalización proporcional al exceso
            exceso = asig.curso.estudiantes - asig.salon.capacidad
            fitness -= 100 * exceso
    
    # 2. Verificar solapamientos de salones
    # Un salón no puede tener dos cursos al mismo tiempo
    for i, asig1 in enumerate(cromosoma.asignaciones):
        for asig2 in cromosoma.asignaciones[i+1:]:
            # Si es el mismo salón y la misma franja horaria
            if (asig1.salon.id == asig2.salon.id and 
                asig1.franja.id == asig2.franja.id):
                fitness -= 200  # Penalización grave
    
    # 3. Verificar conflictos de profesores
    # Un profesor no puede dar dos cursos al mismo tiempo
    for i, asig1 in enumerate(cromosoma.asignaciones):
        for asig2 in cromosoma.asignaciones[i+1:]:
            # Si es el mismo profesor y la misma franja horaria
            if (asig1.curso.profesor == asig2.curso.profesor and 
                asig1.franja.id == asig2.franja.id):
                fitness -= 200  # Penalización grave
    
    # ========================================================================
    # RESTRICCIONES BLANDAS (bonificaciones)
    # ========================================================================
    
    # 1. Preferencias de horario de profesores
    for asig in cromosoma.asignaciones:
        profesor = asig.curso.profesor
        dia = asig.franja.dia
        
        # Si el profesor tiene preferencias
        if profesor in restricciones.preferencias_horario:
            dias_preferidos = restricciones.preferencias_horario[profesor]
            
            # Bonificación si coincide con día preferido
            if dia in dias_preferidos:
                fitness += 10
            else:
                # Pequeña penalización si no es día preferido
                fitness -= 5
    
    # 2. Uso adecuado de salones
    # Bonificar si el tipo de salón es apropiado para el curso
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
                fitness += 15
            else:
                fitness -= 3
    
    # 3. Bonificación por uso eficiente de salones
    # Preferir salones con capacidad cercana al número de estudiantes
    for asig in cromosoma.asignaciones:
        capacidad_usada = asig.curso.estudiantes / asig.salon.capacidad
        
        # Óptimo: usar entre 70% y 95% de la capacidad
        if 0.7 <= capacidad_usada <= 0.95:
            fitness += 5
        elif capacidad_usada < 0.5:
            # Penalización pequeña por desperdiciar espacio
            fitness -= 2
    
    return fitness


# ============================================================================
# OPERADORES GENÉTICOS
# ============================================================================

def generar_cromosoma_aleatorio(cursos: List[Curso], 
                               salones: List[Salon], 
                               franjas: List[FranjaHoraria]) -> Cromosoma:
    """
    Genera un cromosoma aleatorio (solución inicial).
    
    Para cada curso, se asigna aleatoriamente:
    - Un salón
    - Una franja horaria
    """
    asignaciones = []
    
    for curso in cursos:
        # Seleccionar salón y franja aleatoriamente
        salon = random.choice(salones)
        franja = random.choice(franjas)
        
        asignaciones.append(Asignacion(curso, salon, franja))
    
    return Cromosoma(asignaciones)


def seleccion_torneo(poblacion: List[Cromosoma], tamano_torneo: int = 3) -> Cromosoma:
    """
    Selecciona un cromosoma usando selección por torneo.
    
    Se eligen aleatoriamente 'tamano_torneo' individuos y se selecciona
    el mejor de ellos.
    
    Parámetros:
        poblacion: Lista de cromosomas
        tamano_torneo: Número de individuos en el torneo
    
    Retorna:
        El mejor cromosoma del torneo
    """
    torneo = random.sample(poblacion, tamano_torneo)
    return max(torneo, key=lambda c: c.fitness)


def cruce_un_punto(padre1: Cromosoma, padre2: Cromosoma) -> Tuple[Cromosoma, Cromosoma]:
    """
    Realiza cruce de un punto entre dos cromosomas padres.
    
    Se elige un punto de corte aleatorio y se intercambian los genes
    después de ese punto.
    
    Parámetros:
        padre1: Primer cromosoma padre
        padre2: Segundo cromosoma padre
    
    Retorna:
        Tupla con dos cromosomas hijos
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
    Aplica mutación a un cromosoma.
    
    Con probabilidad 'tasa_mutacion', cada gen puede mutar:
    - Cambiar el salón asignado
    - Cambiar la franja horaria asignada
    
    La mutación modifica el cromosoma in-place.
    
    Parámetros:
        cromosoma: Cromosoma a mutar
        salones: Lista de salones disponibles
        franjas: Lista de franjas horarias disponibles
        tasa_mutacion: Probabilidad de mutación por gen
    """
    for i in range(len(cromosoma.asignaciones)):
        # Decidir si este gen muta
        if random.random() < tasa_mutacion:
            # Decidir qué mutar: salón (50%) o franja (50%)
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
# ALGORITMO GENÉTICO PRINCIPAL
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
    Ejecuta el algoritmo genético para encontrar un buen horario.
    
    Parámetros:
        cursos: Lista de cursos a programar
        salones: Lista de salones disponibles
        franjas: Lista de franjas horarias disponibles
        restricciones: Restricciones y preferencias del problema
        tamano_poblacion: Número de individuos en la población
        num_generaciones: Número de generaciones a evolucionar
        tasa_cruce: Probabilidad de cruce entre padres
        tasa_mutacion: Probabilidad de mutación por gen
        elitismo: Número de mejores individuos a preservar
    
    Retorna:
        Tupla con:
        - mejor_cromosoma: La mejor solución encontrada
        - historico_fitness: Lista con el mejor fitness de cada generación
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
    # INICIALIZACIÓN: Generar población inicial
    # ========================================================================
    print("\nGenerando población inicial...")
    poblacion = []
    for _ in range(tamano_poblacion):
        cromosoma = generar_cromosoma_aleatorio(cursos, salones, franjas)
        cromosoma.fitness = calcular_fitness(cromosoma, restricciones)
        poblacion.append(cromosoma)
    
    # Ordenar por fitness
    poblacion.sort(key=lambda c: c.fitness, reverse=True)
    
    # Guardar histórico del mejor fitness
    historico_fitness = [poblacion[0].fitness]
    
    print(f"Población inicial creada.")
    print(f"Mejor fitness inicial: {poblacion[0].fitness:.2f}")
    
    # ========================================================================
    # EVOLUCIÓN: Iterar por generaciones
    # ========================================================================
    for generacion in range(num_generaciones):
        nueva_poblacion = []
        
        # Elitismo: Preservar los mejores individuos
        for i in range(elitismo):
            nueva_poblacion.append(poblacion[i].clonar())
        
        # Generar resto de la población
        while len(nueva_poblacion) < tamano_poblacion:
            # Selección de padres
            padre1 = seleccion_torneo(poblacion)
            padre2 = seleccion_torneo(poblacion)
            
            # Cruce
            if random.random() < tasa_cruce:
                hijo1, hijo2 = cruce_un_punto(padre1, padre2)
            else:
                # Sin cruce, los hijos son copias de los padres
                hijo1 = padre1.clonar()
                hijo2 = padre2.clonar()
            
            # Mutación
            mutacion(hijo1, salones, franjas, tasa_mutacion)
            mutacion(hijo2, salones, franjas, tasa_mutacion)
            
            # Evaluar fitness de los hijos
            hijo1.fitness = calcular_fitness(hijo1, restricciones)
            hijo2.fitness = calcular_fitness(hijo2, restricciones)
            
            # Agregar a nueva población
            nueva_poblacion.append(hijo1)
            if len(nueva_poblacion) < tamano_poblacion:
                nueva_poblacion.append(hijo2)
        
        # Reemplazar población
        poblacion = nueva_poblacion
        
        # Ordenar por fitness
        poblacion.sort(key=lambda c: c.fitness, reverse=True)
        
        # Guardar mejor fitness de esta generación
        mejor_fitness_generacion = poblacion[0].fitness
        historico_fitness.append(mejor_fitness_generacion)
        
        # Imprimir progreso cada 20 generaciones
        if (generacion + 1) % 20 == 0:
            print(f"Generación {generacion + 1}/{num_generaciones} - "
                  f"Mejor fitness: {mejor_fitness_generacion:.2f}")
    
    print("\n" + "="*70)
    print("ALGORITMO GENÉTICO COMPLETADO")
    print("="*70)
    
    # Retornar mejor solución
    mejor_cromosoma = poblacion[0]
    return mejor_cromosoma, historico_fitness


# ============================================================================
# ANÁLISIS Y VISUALIZACIÓN DE RESULTADOS
# ============================================================================

def analizar_solucion(cromosoma: Cromosoma, restricciones: RestriccionesProblema):
    """
    Analiza y muestra un reporte detallado de la solución.
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
    Muestra la evolución del fitness a lo largo de las generaciones.
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
