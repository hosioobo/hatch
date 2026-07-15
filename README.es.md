# Hatch

[English](README.md) | [한국어](README.ko.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [Français](README.fr.md) | [Español](README.es.md)

## Construye con libertad. Publica con limpieza.

Hatch ofrece a quienes crean en solitario un workbench privado para explorar y
un espacio product limpio para compartir. Hace explícita la frontera entre
ambos, para que cada publicación no requiera reconstruir los mismos requisitos.

## Inicio rápido

Después de instalar Hatch, inicia un proyecto con `$hatch`. Crea repositorios
Git locales e independientes para el workbench, el product y la evidencia de
evaluación.

Cuando una versión del product esté lista, vuelve a usar `$hatch` para
promoverla. Hatch confirma el alcance, registra la versión y el changelog,
audita el commit exacto y decide si está listo para hacer push.

## Estructura del workspace

`$hatch init` crea este contenedor local. Los tres directorios hermanos son
repositorios Git independientes.

```text
my-project/
├── hatch.toml                  # describe los tres límites
├── my-project-workbench/       # borradores, experimentos y brief privados
├── my-project-product/         # código product seguro para hacerlo público
└── my-project-evals/           # evidencia privada humana o automatizada
```

## Comandos

Hatch solo tiene dos comandos para quien lo usa. Los pasos posteriores forman
parte de `promote`; no son comandos adicionales que haya que recordar.

### `init`

Usa `$hatch init` al iniciar un proyecto.

1. Define el directorio padre, el nombre del proyecto y la identidad Git pública.
2. Con `--dry-run`, muestra solo las rutas del contenedor y de los tres repositorios.
3. De lo contrario, crea el contenedor e inicializa `workbench`, `product` y
   `evals` como repositorios Git independientes en `main`.
4. Escribe `hatch.toml`, la política de auditoría privada del workbench, las
   instrucciones de los repositorios, los archivos de ignore, y el `VERSION`
   inicial (`0.0.0`) y `CHANGELOG.md` del product.
5. Configura la identidad Git pública del repositorio product.

Nunca crea un remoto, commit, push, tag, release ni despliegue por sí mismo.

### `promote`

Usa `$hatch promote` cuando el trabajo seleccionado esté listo para convertirse
en un snapshot del product.

1. Inspecciona el candidato, el estado actual del product y la evidence
   existente sin modificar el product.
2. Crea una Promotion Brief fijada a su source: intención, trabajo incluido y
   excluido, decisiones de seguridad pública, criterios de aceptación, evidence
   y la siguiente versión estable.
3. Muestra el brief y obtén confirmación antes de cambiar el product.
4. Aplica al product solo el alcance confirmado; nunca sincronices todo el
   workbench automáticamente.
5. Escribe `VERSION` y la entrada correspondiente de `CHANGELOG.md`, ejecuta
   las comprobaciones product relevantes y crea un commit product exacto.
6. Audita el historial alcanzable de ese commit, mensajes de commit, identidades
   Git, rutas y contenido de archivos conforme a la política privada.
7. Registra evidence humana, automatizada o mixta para ese mismo commit.
8. Ejecuta el ready check. Verifica que el brief, el registro de versión, la
   auditoría y la evidence señalen el mismo commit, y luego informa
   `READY TO PUSH`, `NOT READY` o `NEEDS EVIDENCE`.

`promote` no hace push, no crea tags ni releases y no despliega por sí mismo.

## Por qué existe Hatch

### El workbench no es el product

**El problema.** Un proyecto necesita un lugar para borradores, experimentos,
notas y trabajo sin terminar. Un repositorio público necesita una instantánea
segura y enfocada. Mezclarlos convierte cada publicación en una limpieza.

**La solución.** Mantenlos en repositorios Git independientes. Desarrolla con
libertad en el workbench y promueve al product solo el trabajo que debe ser
público.

### La promoción debe ser repetible

**El problema.** Cada promoción plantea las mismas preguntas: ¿qué se incluye?
¿es seguro publicarlo? ¿qué versión es? ¿se probó de verdad?

**La solución.** Hatch reúne esas preguntas en un único flujo: brief, versión,
auditoría, evidencia de evaluación y decisión de preparación, todo vinculado a
un commit product exacto.

### Resumen

Hatch separa la exploración privada del trabajo product público y hace que el
paso entre ambos sea pequeño, deliberado y verificable.
