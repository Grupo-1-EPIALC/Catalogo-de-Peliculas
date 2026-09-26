# Registro de Uso de Inteligencia Artificial

**Integrante:** Darío  
**Proyecto:** Catálogo de Películas  
**Módulo / Trabajo realizado:** Desarrollo, refactorización y pruebas del módulo `crud.py`, y adaptación de la interfaz en `main.py`.

---

## 1. Creación e Implementación Inicial de `crud.py`

* **Prompt / Consulta del usuario:**
  > Diseña e implementa las funciones para la lógica del módulo `crud.py` a partir de la estructura de funciones vacías (`pass`) provista en el repositorio.

* **Respuesta / Propuesta de la IA:**
  * Generación del código para las operaciones fundamentales de lectura, creación, actualización, eliminación y manejo de listas: `cargar_catalogo`, `guardar_catalogo`, `obtener_pelicula_por_id`, `crear_pelicula`, `actualizar_pelicula`, `eliminar_pelicula`, `agregar_valor_a_lista` y `quitar_valor_de_lista`.
  * Definición de tipos de datos (`type hints`) acordes a las especificaciones del dataset unificado JSON.

* **Decisión del usuario:** Aceptado.

* **Cómo se comprobó que funciona:** 
  * Se revisó que la lógica de manipulación de listas y diccionarios respetara los nombres de claves requeridos por el archivo `movies_unified.json`.

---

## 2. Implementación de Control de Excepciones (`try / except`)

* **Prompt / Consulta del usuario:**
  > Refactoriza la logica de manejo de errores con uso defensivo de condicionales `if/else` por un manejo de errores basado en excepciones nativas (`try/except`).

* **Respuesta / Propuesta de la IA:**
  * Reestructuración de las funciones bajo el principio idiomático de Python (EAFP: *Easier to ask for forgiveness than permission*).
  * Sustitución de búsquedas manuales previas por la captura de excepciones explícitas como `ValueError` (para IDs inexistentes o repetidos), `OSError` (para fallas de escritura en disco) y `json.JSONDecodeError` (ante lecturas de archivos corruptos), garantizando que las excepciones lancen mensajes claros sin detener abruptamente el programa.

* **Decisión del usuario:** Aceptado.

* **Cómo se comprobó que funciona:** 
  * Se ejecutaron pruebas aislando entradas inválidas para validar la elevación de los mensajes de error configurados.

---

## 3. Autosuficiencia del Módulo y su Impacto en `main.py`

* **Prompt / Consulta del usuario:**
  > Rediseña el flujo de persistencia para que `crud.py` no dependa de recibir constantemente la variable `catalogo` en memoria como parámetro obligatorio. Basate en el principio de responsabilidades de POO, donde la persistencia es competencia de la entidad que modifica y main solo invoca funcionalidades sin la responsabilidad de persistir. 

* **Respuesta / Propuesta de la IA:**
  * **Motivo:** Evitar la inconsistencia de datos entre la memoria RAM y el archivo físico. Al volver a las funciones autónomas, cada operación (alta, modificación o borrado) lee el estado actual del disco, aplica la operación y persiste inmediatamente los cambios de forma atómica.
  * **Efecto en `main.py`:** Se advierte que el contrato explicito en las normativas del proyecto especifica que le main pasa el catalogo como argumento inicial en las funciones del CRUD y que el CRUD no persite el archivo, por lo cual el cambio implica que se deberán alterar reglas de negocio.

* **Decisión del usuario:** Aceptado.

* **Cómo se comprobó que funciona:** 
  * Se constató que cada modificación realizada impactara de forma directa en el archivo JSON sin requerir pasos intermedios de guardado manual.

---

## 4. Agregado de la Función `obtener_id_por_titulo`

* **Prompt / Consulta del usuario:**
  > Incorpora una función utilitaria dentro del módulo CRUD para resolver la búsqueda de una película cuando el usuario no conoce su ID numérico. Recibira `titulo` y retornará `id`

* **Respuesta / Propuesta de la IA:**
  * Implementación de `obtener_id_por_titulo(titulo, ruta_json)` que realiza una comparación insensible a mayúsculas y minúsculas (*case-insensitive*) sobre el campo `title`, retornando el ID entero de la coincidencia o `None` si no existe.

* **Decisión del usuario:** Aceptado.

* **Cómo se comprobó que funciona:** 
  * Se probó enviando cadenas de texto en minúsculas y mayúsculas, confirmando el retorno correcto del entero ID asociado.

---

## 5. Refactorización e Integración Final en `main.py`

* **Prompt / Consulta del usuario:**
  > Actualiza el archivo `main.py` para sincronizar la interfaz de usuario con la nueva firma de las funciones de `crud.py`, documentando adecuadamente los cambios para el equipo y el responsable del modulo. Agrega como primera opcion al menu CRUD del main, el llamado a la nueva funcion "buscar_id_por_titulo" 

* **Respuesta / Propuesta de la IA:**
  * Reescritura del submódulo `menu_crud` en `main.py` adaptando la recolección de entradas del usuario y llamadas a `crud.py`.
  * Agregado del llamado a la nueva funcion buscar id por titulo.
  * Inserción de comentarios explicativos con la etiqueta `# MODIFICACION:` en cada punto modificado para facilitar la revisión del código por parte de los compañeros de equipo.

* **Decisión del usuario:** Aceptado.

* **Cómo se comprobó que funciona:** 
  * Se corrió la suite de pruebas `probar_crud.py` verificando la ejecución punta a punta de todos los casos de prueba sin fallas.

## 6. Se efectuaron pruebas en local, mediante la ejecución de main.py y el llamado a todas las funciones del crud para comprobar funcionalidad esperada. 