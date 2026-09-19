# Guía de Trabajo Práctico

> Completar el nombre de la materia, el tema elegido y los integrantes antes de empezar.

- **Materia:**
- **Tema del proyecto:**
- **Integrantes:**
  1.
  2.
  3.

---

## 1. Objetivo

Desarrollar una aplicación en Python que combine lógica de programación, manejo de datos con
pandas, persistencia en JSON/CSV o una API externa, y al menos una visualización con
Matplotlib, aplicando buenas prácticas de organización de código (módulos, funciones propias,
manejo de errores).

---

## 2. Requisitos funcionales (mínimos)

- [ ] **Carga de datos**: cargar, obtener o recuperar información (desde archivo, API o entrada
      del usuario).
- [ ] **Validación**: validar los datos ingresados/leídos y responder adecuadamente ante errores
      (mensajes claros, sin que el programa se caiga).
- [ ] **Operaciones sobre registros**: consultar, buscar, filtrar o modificar registros.
- [ ] **Indicadores**: calcular al menos **3 resultados o indicadores útiles** (promedios,
      totales, porcentajes, máximos/mínimos, tendencias, etc.).
- [ ] **Persistencia**: guardar y/o recuperar información mediante JSON, CSV o una API externa.
- [ ] **Visualización**: generar al menos **un gráfico claro** de los datos.

## 3. Requisitos técnicos (mínimos)

- [ ] Variables, tipos de datos, condicionales (`if/elif/else`) y estructuras repetitivas
      (`for`, `while`).
- [ ] Listas y diccionarios (uso real, no solo declarados).
- [ ] Al menos **4 funciones propias**, con nombres claros y **anotaciones de tipo**
      (ej. `def calcular_promedio(datos: list[float]) -> float:`).
- [ ] Manejo de errores con `try`/`except` (no genérico y vacío; capturar excepciones
      concretas y dar un mensaje útil).
- [ ] Código organizado en **al menos dos módulos `.py`** (separar `main.py` de la lógica).
- [ ] Persistencia o intercambio de datos con JSON o CSV.
- [ ] Uso de **pandas** para organizar, filtrar o analizar información.
- [ ] Al menos un gráfico con **Matplotlib**.
- [ ] Una fuente de datos externa (API o archivo) cuando sea pertinente al tema.

## 4. Estructura del proyecto

```
proyecto/
├── main.py              # Ejecución principal y flujo general
├── funciones.py         # Funciones propias y lógica reutilizable
├── analisis.ipynb        # Exploración con pandas, gráficos y conclusiones
├── datos.json / datos.csv  # Datos usados o producidos por la app
├── requirements.txt      # Bibliotecas externas necesarias
├── README.md             # Objetivo, instrucciones de ejecución, decisiones
└── registro_ia/
    ├── registro_[nombre_integrante_1].md
    ├── registro_[nombre_integrante_2].md
    └── registro_[nombre_integrante_3].md
```

La estructura puede adaptarse, pero siempre debe quedar separada la ejecución principal
(`main.py`) de las funciones reutilizables (`funciones.py` u otro módulo).

## 5. Uso de inteligencia artificial — qué hay que entregar

El uso de IA (Copilot, Claude, ChatGPT, etc.) está permitido como asistencia, pero:

- Cada integrante debe **poder explicar y modificar** cualquier código incorporado con IA.
- Hay que **registrar al menos 3 prompts relevantes** por integrante, con su respuesta.
- Por cada prompt hay que indicar si la propuesta fue **aceptada, modificada o rechazada**,
  y por qué.
- Hay que explicar **cómo se comprobó** que el código funcionaba (pruebas manuales, casos de
  prueba, datos de ejemplo, etc.).

Esto se documenta en la carpeta `registro_ia/`, un archivo por integrante (ver sección 6 y
plantilla al final).

## 6. Instrucciones para los agentes de IA (leer antes de programar)

Estas instrucciones son para el asistente de IA (Claude, Copilot u otro) que colabore en este
proyecto. Deben cumplirse durante **toda** la sesión de trabajo, no solo al final.

1. **Identificar al integrante activo.** Al empezar la sesión, si no está claro, preguntar
   quién es la persona que está trabajando (nombre del integrante), para registrar los prompts
   a su nombre. Si varias personas usan la misma sesión, confirmar el cambio de integrante
   cuando ocurra.

2. **Registrar cada intercambio relevante**, no solo los "3 mínimos" que pide la consigna.
   Es más fácil filtrar al final que reconstruir de memoria. Se considera relevante todo
   prompt que:
   - pida generar o modificar código,
   - pida explicar o corregir un error,
   - pida diseñar la estructura del proyecto o una función.
   No hace falta registrar preguntas triviales (ej. "¿qué hora es?").

3. **Archivo por integrante**: mantener/crear `registro_ia/registro_[nombre].md` y **agregar**
   una entrada nueva al final por cada intercambio relevante (no sobrescribir el archivo).

4. **Formato de cada entrada** (usar esta plantilla exacta):

   ```markdown
   ### Entrada N — [fecha y hora]

   **Prompt del usuario:**
   > (texto completo o resumen fiel del pedido)

   **Respuesta / propuesta de la IA:**
   (resumen de qué código o solución se propuso, sin pegar archivos enteros si son largos;
   alcanza con la idea clave y, si aplica, el fragmento relevante)

   **Decisión del usuario:** Aceptado / Modificado / Rechazado

   **Si fue modificado o rechazado:** explicar qué cambió el usuario y por qué (esto es una
   corrección del usuario y es tan importante como el prompt original).

   **Cómo se comprobó que funciona:** (ej. se ejecutó con datos de prueba X, se revisó
   manualmente la salida, se comparó contra un cálculo esperado, etc.)
   ```

5. **No inventar decisiones del usuario.** Si el agente no tiene claro si algo fue aceptado tal
   cual o modificado, debe preguntarlo antes de cerrar la entrada, en vez de asumir.

6. **Al final del proyecto**, generar un resumen breve en `registro_ia/RESUMEN.md` que liste,
   por integrante, cuántos prompts relevantes hubo y cuántos fueron aceptados/modificados/
   rechazados, para facilitar la sección correspondiente del `README.md`.

## 7. Checklist final antes de entregar

- [ ] Los 6 requisitos funcionales están implementados y se pueden mostrar funcionando.
- [ ] Los 9 requisitos técnicos están presentes en el código (no solo mencionados).
- [ ] Existen al menos 4 funciones propias con anotaciones de tipo.
- [ ] Hay manejo de errores real (`try/except`) en los puntos donde algo puede fallar
      (lectura de archivo, conversión de datos, llamada a API, etc.).
- [ ] El proyecto está separado en al menos 2 módulos `.py`.
- [ ] Existe `datos.json` o `datos.csv` con información real usada por la app.
- [ ] `analisis.ipynb` tiene exploración con pandas, al menos un gráfico y conclusiones escritas.
- [ ] `requirements.txt` lista las librerías externas usadas (pandas, matplotlib, requests, etc.).
- [ ] `README.md` explica objetivo, cómo ejecutar el proyecto y decisiones de diseño.
- [ ] Cada integrante tiene su `registro_ia/registro_[nombre].md` con al menos 3 prompts
      relevantes, la decisión tomada sobre cada uno y cómo se comprobó el funcionamiento.
- [ ] Cualquier integrante puede explicar y modificar cualquier parte del código, aunque
      haya sido generada con ayuda de IA.
