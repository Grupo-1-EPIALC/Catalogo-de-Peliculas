# Instrucciones para agentes de IA en este repositorio

Estas reglas aplican a cualquier agente de IA (Claude Code u otro) que trabaje en este
proyecto, durante toda la sesion, no solo al hacer el commit final.

## Flujo de git obligatorio

- **Nunca commitear ni pushear directamente a `develop` ni a `main`.** Son ramas
  protegidas/compartidas por el equipo.
- Para cualquier cambio (por chico que sea: código, notebook, README, etc.), **crear una
  rama nueva** a partir de `develop` antes de tocar archivos:

  ```bash
  git checkout develop
  git pull
  git checkout -b <tipo>/<descripcion-corta>
  ```

  Nomenclatura sugerida (seguir el patron ya usado en el repo): `ticket-XXXXX` si hay un
  numero de ticket, o `feature/<descripcion-corta>` si no lo hay.

- Terminado el cambio, commitear en esa rama y pushearla con `-u origin <rama>`.
- **Abrir un Pull Request hacia `develop`** (no hacia `main`) en vez de mergear o pushear
  directo. Usar `gh pr create --base develop`.
- No hacer merge del propio PR salvo pedido explicito del usuario.
- Nunca usar `git push --force` sobre `develop` o `main`.

## Cuando pedir confirmacion

- Antes de crear una rama nueva o abrir un PR, esta bien proceder si el pedido del
  usuario ya lo implica (ej. "subi este cambio", "creame un PR con esto").
- Si el usuario pide explicitamente commitear directo a `develop` o `main` en una
  situacion puntual, se puede hacer, pero conviene confirmar que es intencional antes de
  saltarse la regla (no asumirlo por defecto).

## Por que

El equipo trabaja con Pull Requests para revisar cambios antes de que lleguen a
`develop`/`main` (ver historial de merges en este repo). Un agente commiteando directo
salta esa revision y puede romper el trabajo de otro integrante.
