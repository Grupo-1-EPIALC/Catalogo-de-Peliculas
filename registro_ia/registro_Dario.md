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
  > Refactoriza la lógica de manejo de errores con uso defensivo de condicionales `if/else` por un manejo de errores basado en excepciones nativas (`try/except`).

* **Respuesta / Propuesta de la IA:**
  * Reestructuración de las funciones bajo el principio idiomático de Python (EAFP: *Easier to ask for forgiveness than permission*).
  * Sustitución de búsquedas manuales previas por la captura de excepciones explícitas como `ValueError` (para IDs inexistentes o repetidos), `OSError` (para fallas de escritura en disco) y `json.JSONDecodeError` (ante lecturas de archivos corruptos), garantizando que las excepciones lancen mensajes claros sin detener abruptamente el programa.

* **Decisión del usuario:** Aceptado.

* **Cómo se comprobó que funciona:** 
  * Se ejecutaron pruebas aislando entradas inválidas para validar la elevación de los mensajes de error configurados.

---

## 3. Autosuficiencia del Módulo y su Impacto en `main.py`

* **Prompt / Consulta del usuario:**
  > Rediseña el flujo de persistencia para que `crud.py` no dependa de recibir constantemente la variable `catalogo` en memoria como parámetro obligatorio. Básate en el principio de responsabilidades de POO, donde la persistencia es competencia de la entidad que modifica y `main` solo invoca funcionalidades sin la responsabilidad de persistir.

* **Respuesta / Propuesta de la IA:**
  * **Motivo:** Evitar la inconsistencia de datos entre la memoria RAM y el archivo físico. Al volver a las funciones autónomas, cada operación (alta, modificación o borrado) lee el estado actual del disco, aplica la operación y persiste inmediatamente los cambios de forma atómica.
  * **Efecto en `main.py`:** Se advierte que el contrato explícito en las normativas del proyecto especifica que `main` pasa el catálogo como argumento inicial en las funciones del CRUD y que el CRUD no persiste el archivo, por lo cual el cambio implica que se deberán alterar reglas de negocio.

* **Decisión del usuario:** Aceptado.

* **Cómo se comprobó que funciona:** 
  * Se constató que cada modificación realizada impactara de forma directa en el archivo JSON sin requerir pasos intermedios de guardado manual.

---

## 4. Agregado de la Función `obtener_id_por_titulo`

* **Prompt / Consulta del usuario:**
  > Incorpora una función utilitaria dentro del módulo CRUD para resolver la búsqueda de una película cuando el usuario no conoce su ID numérico. Recibirá `titulo` y retornará `id`.

* **Respuesta / Propuesta de la IA:**
  * Implementación de `obtener_id_por_titulo(titulo, ruta_json)` que realiza una comparación insensible a mayúsculas y minúsculas (*case-insensitive*) sobre el campo `title`, retornando el ID entero de la coincidencia o `None` si no existe.

* **Decisión del usuario:** Aceptado.

* **Cómo se comprobó que funciona:** 
  * Se probó enviando cadenas de texto en minúsculas y mayúsculas, confirmando el retorno correcto del entero ID asociado.

---

## 5. Refactorización e Integración Final en `main.py`

* **Prompt / Consulta del usuario:**
  > Actualiza el archivo `main.py` para sincronizar la interfaz de usuario con la nueva firma de las funciones de `crud.py`, documentando adecuadamente los cambios para el equipo y el responsable del módulo. Agrega como primera opción al menú CRUD de `main`, el llamado a la nueva función "buscar_id_por_titulo".

* **Respuesta / Propuesta de la IA:**
  * Reescritura del submódulo `menu_crud` en `main.py` adaptando la recolección de entradas del usuario y llamadas a `crud.py`.
  * Agregado del llamado a la nueva función buscar id por título.
  * Inserción de comentarios explicativos con la etiqueta `# MODIFICACION:` en cada punto modificado para facilitar la revisión del código por parte de los compañeros de equipo.

* **Decisión del usuario:** Aceptado.

* **Cómo se comprobó que funciona:** 
  * Se corrió la suite de pruebas `probar_crud.py` verificando la ejecución punta a punta de todos los casos de prueba sin fallas.

---

## 6. Se efectuaron pruebas manuales en local, mediante la ejecución de `main.py` y el llamado a todas las funciones del CRUD para comprobar la funcionalidad esperada. Se detectaron inconsistencias entre campos simples y listas.

* **Prompt / Consulta del usuario:**
  > Inspecciona la función [actualizar_pelicula], la misma sobrescribe cualquier campo; si el campo seleccionado contiene una lista, la función lo sobrescribe con un valor simple, rompiendo la lista. Esto NO debe suceder. Aplica blindaje para que, si detecta que el campo a modificar contiene una lista, no ejecute e informe al usuario que las listas se manipulan con las opciones 6 y 7.

* **Respuesta / Propuesta de la IA:**
  * Se implementó un blindaje de validación dentro de `actualizar_pelicula` que comprueba si el campo a modificar ya existe y es de tipo lista.
  * Se agregó un objeto global `_CAMPOS_LISTA_VALIDOS {}` que determina los campos que contienen listas y se consulta con `not in` antes de validar la nueva entrada.
  * Se refactorizaron las funciones que modifican campos (agregar y quitar valores en listas) con base en el nuevo objeto global. Agregar y quitar elementos de las listas actúan sobre el objeto, evaluando si son listas para agregar el nuevo dato o informar un error de tipo.

* **Decisión del usuario:** No Aceptado.
* **Argumento:** Un objeto rígido cargado en memoria RAM desde el código mismo del programa leerá siempre los mismos valores como listas. Si se agregan nuevos campos en el archivo `movies_unified.json`, estos no serán contemplados y siempre serán evaluados como campos nuevos.

* **Prompt / Consulta del usuario:**
  > Desestima tu propuesta: la detección de campos y del tipo de datos que contienen debe hacerse directa y dinámicamente desde el documento JSON, no desde un objeto estático en el CRUD, ya que este solo contendrá los valores iniciales fijos y no estará sujeto a cambios del JSON base. Ejemplo: si agrego un nuevo campo, `premios: ["oscar", "globo de oro"]`, este existirá en el JSON, pero la aplicación no puede reescribir `crud.py` para persistir el nuevo campo en el objeto `_CAMPOS_LISTA_VALIDOS {}`. Como resultado de tu estrategia, los nuevos campos que no existan en el objeto inicial nunca serán reconocidos.

* **Respuesta / Propuesta de la IA:**
  * Reemplazo de listas duras (`_CAMPOS_LISTA_VALIDOS`) por evaluación dinámica en tiempo de ejecución (`any(isinstance(p.get(clave), list) for p in catalogo)`). Esto garantiza persistencia entre reinicios del sistema sin impacto significativo en tiempo de ejecución ($\approx 0.05$ ms vs. $\sim 20$ ms de escritura en disco).
  * Se rediseñó `actualizar_pelicula` para que opere exclusivamente sobre la nueva implementación con base en las indicaciones del usuario.

* **Cómo se comprobó que funciona:** 
  * Se ejecutaron pruebas manuales intentando sobrescribir el campo genres (lista) a través de actualizar_pelicula, verificando que el sistema interrumpe la operación y muestra el mensaje de incompatibilidad de tipo de datos.

---
  
## 7. Ingreso de nuevos campos

* **Prompt / Consulta del usuario:**
  > Utiliza la misma herramienta de lectura dinámica del objeto para detectar si el valor ingresado como nombre de campo para la modificación no existe en la película seleccionada por ID. Aplica lo siguiente: si [dato ingresado] para modificar clave existe, actualiza valor; si [dato ingresado] no existe como clave, agrega nueva clave: valor a la película.

* **Respuesta / Propuesta de la IA:**
  * Se ajustó la lógica para que, si el nombre del campo ingresado no existe dentro de la película, se cree dinámicamente el nuevo par clave: valor (como campo simple).
  * En caso de que el campo ya exista, se valida que no sea una lista antes de actualizar su valor; de ser un campo simple existente, se sobrescribe con el nuevo dato ingresado.

* **Cómo se comprobó que funciona:** 
  * Se realizó la prueba asignando un campo inexistente (por ejemplo, "subtítulo") a una película mediante `actualizar_pelicula`, comprobando que la clave se crea e integra correctamente al diccionario y se persiste en el JSON sin afectar las demás propiedades.
  * Se realizó la prueba asignando un nuevo valor a "subtítulo" en la misma película mediante `actualizar_pelicula`, comprobando que el valor reemplaza el cargado previamente en la clave y se persiste en el JSON.

---
  
## 7. Implementación de nueva lógica en las funciones que manejan listas

* **Prompt / Consulta del usuario:**
  > Aplica a las funciones [agregar_valor_a_lista] y [quitar_valor_de_lista] la misma restricción utilizada en [actualizar_pelicula], pero en estas funciones se debe validar que las acciones se efectúen sobre campos de tipo lista en la película a modificar; en caso contrario (si el campo contiene un dato simple y plano), informa el error. Aplica también la creación (si no existe) de una nueva lista o la actualización de la misma si ya existía previamente.

* **Respuesta / Propuesta de la IA:**
  * Se actualizaron las funciones `agregar_valor_a_lista` y `quitar_valor_de_lista` para validar que las operaciones se ejecuten exclusivamente sobre campos de tipo lista (`isinstance(..., list)`).
  * Se incorporó el control de error para interrumpir la ejecución mediante una excepción `ValueError` si el usuario intenta operar sobre un campo simple existente, notificando que dichos campos deben gestionarse desde la opción 4 (`actualizar_pelicula`).
  * En `agregar_valor_a_lista`, se implementó la creación automática del nuevo campo, inicializándolo como lista (`[valor]`) en caso de que la clave no existiera previamente en la película, o anexando el elemento (`append`) si la lista ya estaba presente.

**Decisión del usuario:** Aceptado

**Cómo se comprobó que funciona:**
  * Se verificó agregando un elemento a un campo de lista nuevo y a uno existente, confirmando la creación/actualización limpia. Asimismo, se probó la adición sobre un campo simple (como title), comprobando que la función bloquea la acción y lanza el ValueError correspondiente.
  * Se verificó intentando eliminación de un elemento sobre un campo que no contenía una lista, el sistema informa correctamente el error.
  * Se verificó la eliminación de un elemento inexistente en una lista; el sistema informa correctamente que no se eliminó porque no existía ese valor en la lista.

---
  
## 7. Implementación de nueva lógica en las funciones que manejan listas

* **Prompt / Consulta del usuario:**
  > Comprueba la integridad y el funcionamiento de todo el archivo `crud.py`; verifica que las funciones estén correctas en relación con lo que establecimos y los cambios indicados, cumpliendo con el contrato de la consigna para este módulo.

* **Respuesta / Propuesta de la IA:**
El archivo `crud.py` se encuentra en un estado impecable, consistente y 100 % alineado con todas las decisiones de arquitectura que definieron.
A continuación, la comprobación paso a paso de la integridad y el funcionamiento según las reglas establecidas:

# Reporte de Auditoría e Integridad de Código: `crud.py`

**Módulo:** `crud.py`
**Estado:** Finalizado / Aprobado
**Compatibilidad:** Python 3.10+
**Persistencia:** JSON (`utf-8`)

---

## 1. Análisis Técnico por Función

### Módulo de Carga y Persistencia

#### `cargar_catalogo(ruta_json)`
* **Objetivo:** Leer y deserializar el archivo JSON del catálogo.
* **Manejo de excepciones:** Captura `FileNotFoundError` y `json.JSONDecodeError`, devolviendo una lista vacía `[]` con un registro explícito en consola sin interrumpir la aplicación.

#### `guardar_catalogo(catalogo, ruta_json)`
* **Objetivo:** Persistir los datos en disco.
* **Manejo de excepciones:** Captura `OSError` ante problemas de permisos o espacio en disco.

---

### Módulo de Lectura y Búsqueda

#### `obtener_pelicula_por_id(id_pelicula, ruta_json)`
* Búsqueda eficiente mediante generadores (`next()`). Devuelve el `dict` de la película o `None` si no existe.

#### `obtener_id_por_titulo(titulo, ruta_json)`
* Normalización con `.strip().lower()` para coincidencias exactas e insensibles a mayúsculas/minúsculas.

---

### Módulo de Modificación y Escritura (CRUD)

#### `crear_pelicula(nueva_pelicula, ruta_json)`
* Validaciones estrictas: requiere que el parámetro sea `dict` y contenga de forma obligatoria las claves `"id"` y `"title"`.
* Verificación previa de ID duplicado vía `any()`. Arroja `ValueError` si el ID ya existe.

#### `actualizar_pelicula(id_pelicula, campo_o_dict, nuevo_valor, ruta_json)`
* Desempaquetado flexible para recibir un diccionario o pares `clave`/`valor`.
* **Blindaje:** Inspecciona si la propiedad evaluada es de tipo lista en la película o en el catálogo global. Si lo es, cancela la operación e indica usar las opciones de lista.

#### `eliminar_pelicula(id_pelicula, ruta_json)`
* Remueve el objeto del catálogo y persiste los cambios. Arroja `ValueError` si el ID no es encontrado.

#### `agregar_valor_a_lista(...)` / `quitar_valor_de_lista(...)`
* **Soporte Polimórfico:** Maneja llamadas desde `main.py` pasando el catálogo explícito o utilizando la carga por defecto por ID.
* **Lógica de Lista:**
  * Si la clave no existe al agregar, inicializa el campo como una nueva lista (`[valor]`).
  * Si el campo existe pero es escalar (tipo simple), frena la ejecución mediante `ValueError`.
  * Si al quitar el elemento no existe dentro de la lista, lanza `ValueError` con mensaje informativo.

---

## 2. Conclusión
El archivo `crud.py` cumple con todas las especificaciones solicitadas, garantizando un código desacoplado, mantenible y listo para su integración con `main.py`.