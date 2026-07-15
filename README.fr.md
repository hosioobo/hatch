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

## Structure du workspace

`$hatch init` crée ce conteneur local. Les trois répertoires frères sont des
dépôts Git indépendants.

```text
my-project/
├── hatch.toml                  # décrit les trois frontières
├── my-project-workbench/       # brouillons, essais et brief privés
├── my-project-product/         # source product sûre à rendre publique
└── my-project-evals/           # preuves privées, humaines ou automatiques
```

## Commandes

Hatch ne propose que deux commandes destinées à l'utilisateur. Les étapes qui
suivent font partie de `promote` ; ce ne sont pas des commandes à mémoriser.

### `init`

Utilisez `$hatch init` pour démarrer un projet.

1. Déterminez le répertoire parent, le nom du projet et l'identité Git publique.
2. Avec `--dry-run`, affichez uniquement les chemins du conteneur et des trois
   dépôts.
3. Sinon, créez le conteneur puis initialisez `workbench`, `product` et `evals`
   comme des dépôts Git indépendants sur `main`.
4. Écrivez `hatch.toml`, la politique d'audit privée du workbench, les
   instructions des dépôts, les fichiers d'ignorés, ainsi que le `VERSION`
   initial du product (`0.0.0`) et `CHANGELOG.md`.
5. Configurez l'identité Git publique du dépôt product.

Cette commande ne crée jamais de remote, commit, push, tag, release ou déploiement.

### `promote`

Utilisez `$hatch promote` lorsqu'un travail sélectionné est prêt à devenir un
instantané product.

1. Inspectez le candidat, l'état actuel du product et les evidence existantes,
   sans modifier le product.
2. Créez une Promotion Brief liée à sa source : intention, travail inclus et
   exclu, décisions de sécurité publique, critères d'acceptation, evidence et
   prochaine version stable.
3. Présentez le brief et obtenez confirmation avant toute modification du product.
4. Appliquez uniquement le périmètre confirmé au product ; ne synchronisez
   jamais automatiquement tout le workbench.
5. Écrivez `VERSION` et l'entrée `CHANGELOG.md` correspondante, lancez les
   vérifications product utiles et créez un commit product exact.
6. Auditez l'historique accessible de ce commit, les messages de commit, les
   identités Git, les chemins et le contenu des fichiers selon la politique privée.
7. Consignez une evidence humaine, automatique ou mixte pour ce même commit.
8. Exécutez le ready check. Il vérifie que le brief, le journal de version,
   l'audit et l'evidence désignent tous le même commit, puis affiche
   `READY TO PUSH`, `NOT READY` ou `NEEDS EVIDENCE`.

`promote` ne pousse pas, ne crée pas de tag ou de release et ne déploie jamais seul.

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
