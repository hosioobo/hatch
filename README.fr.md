# Hatch

[English](README.md) | [한국어](README.ko.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [Français](README.fr.md) | [Español](README.es.md)

## Construisez librement. Publiez proprement.

Hatch offre aux créateurs indépendants un workbench privé pour explorer et un
espace product propre pour partager. La frontière entre les deux est explicite :
inutile de reconstruire les mêmes exigences à chaque publication.

## Démarrage rapide

Après avoir installé Hatch, démarrez un projet avec `$hatch`. Il crée des dépôts
Git locaux distincts pour le workbench, le product et les preuves d'évaluation.

Lorsqu'une version du product est prête, utilisez à nouveau `$hatch` pour la
promouvoir. Hatch confirme le périmètre, consigne la version et le changelog,
audite le commit exact et décide s'il est prêt à être poussé.

## Pourquoi Hatch existe

### Le workbench n'est pas le product

**Le problème.** Un projet a besoin d'un endroit pour les brouillons, les
expériences, les notes et le travail inachevé. Un dépôt public a besoin d'un
instantané sûr et ciblé. Les mélanger transforme chaque publication en ménage.

**La solution.** Gardez-les dans des dépôts Git indépendants. Développez
librement dans le workbench et ne promouvez dans le product que le travail qui
doit être public.

### La promotion doit être reproductible

**Le problème.** Chaque promotion soulève les mêmes questions : qu'est-ce qui
est inclus ? Peut-on le publier sans risque ? Quelle est cette version ? A-t-il
vraiment été testé ?

**La solution.** Hatch transforme ces questions en un seul flux : brief,
version, audit, preuves d'évaluation et décision de préparation, tous liés à
un commit product précis.

### En résumé

Hatch sépare l'exploration privée du travail product public, puis rend le
passage entre les deux petit, délibéré et vérifiable.
