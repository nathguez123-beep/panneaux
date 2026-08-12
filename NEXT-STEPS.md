# État du site et suite — 12 août 2026

Contenu réécrit avec les chiffres vérifiés post-réforme du 5 juin 2026.
Build validé sur Astro 7 : 6 pages générées, aucune erreur.

## Ce qui est fait

- **6 pages réécrites** avec chiffres datés et sourcés, plus une nouvelle page
  `reforme-photovoltaique-juin-2026` (la réforme S21 : prime supprimée, rachat à
  1,1 c€/kWh, vente totale interdite ≤ 9 kWc)
- **JSON-LD ajouté** dans `Base.astro` : schéma `WebPage` sur chaque page, plus
  `FAQPage` quand la page passe une prop `faq` — c'est ce que les moteurs de réponse
  extraient en priorité
- **`public/llms.txt`** créé : fiche de faits complète, prix, rentabilité, FAQ
- Nav mise à jour, pages légales séparées en pied de page

## Bloquant : le domaine

`astro.config.mjs` contient encore `site: 'https://example.fr'`. Tant que ce n'est pas
changé, les URLs canoniques, le sitemap et le `robots.txt` pointent tous vers un domaine
qui n'existe pas.

À faire dès que le domaine est choisi :

1. `astro.config.mjs` → `site: 'https://LE-VRAI-DOMAINE.fr'`
2. `public/robots.txt` → corriger la ligne `Sitemap:`
3. Regénérer les mirrors et le sitemap (voir ci-dessous)

## Les 3 fichiers — reste à faire

Le skill `ai-visibility-pack` est installé. Dans Claude Code, dire simplement
« lance ai-visibility-pack sur ce site » une fois le domaine défini. Ou à la main :

```bash
pip install beautifulsoup4 markdownify
npm run build
python3 scripts/make_mirrors.py dist --base-url https://LE-DOMAINE.fr --update-llms public/llms.txt
python3 scripts/make_sitemap.py dist --base-url https://LE-DOMAINE.fr --dry-run
```

Remarque sur le sitemap : les règles de priorité du script sont écrites pour des URLs
anglaises, donc `aides-...`, `rentabilite-...` et `reforme-...` retombent à 0.6 au lieu
de 0.9. Le `--dry-run` est là pour ça — ajuster avant d'écrire, ou ajouter les termes
français (`aide`, `prime`, `rentabilite`, `reforme`, `tarif`) aux règles du script.

Retirer aussi `@astrojs/sitemap` de `astro.config.mjs` : il génère un sitemap plat sans
pondération, ce qui est précisément ce qu'on veut corriger.

Servir les `.md` en `Content-Type: text/plain` selon l'hébergeur — sinon le navigateur
les télécharge au lieu de les afficher. Détails dans `references/hosting.md` du skill.

## Ce qui manque encore, et qui ne peut venir que de toi

- **Le domaine.**
- **Le chemin de conversion.** Le site n'a aucun CTA ni lien de prise de rendez-vous.
  En l'état c'est un site d'information pur — excellent pour être cité, inutile pour
  générer des leads. Il faut décider où et comment le visiteur devient un contact.
- **Les villes ciblées.** Les requêtes à plus forte intention sont du type
  « panneaux solaires à [ville] ». Aucune page locale n'existe pour l'instant.
- **Mentions légales.** Elles contiennent probablement encore des champs à remplir —
  obligatoire en France, et c'est un signal de confiance pour les moteurs.

## Chiffres à revérifier avant toute publication supplémentaire

Sources contradictoires ou non confirmées, volontairement écartées du contenu actuel :

- Le taux de TVA à 10 % pour une installation de 12 kWc — une source l'affirme, la
  majorité indique 20 % au-delà de 9 kWc. Non publié.
- La tarification 12 kWc (18 000–26 000 €) repose sur une source unique.
- Le détail « déclaration préalable » n'a pas pu être confirmé sur service-public.fr
  (fiche F1996 en 404 au moment de la rédaction).

Le dossier complet des données et sources est dans le projet Claude,
`claude/fr-solar-market-data-aug-2026.md`.
