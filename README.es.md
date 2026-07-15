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
