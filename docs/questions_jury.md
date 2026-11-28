# Questions Probables du Jury & Réponses d'Ingénierie — SAFINUM 2026

> **Projet** : SAFINUM Innovate Challenge 2026  
> **Cadre** : Préparation à la soutenance devant le jury technique et d'évaluation.  
> **Principe de véracité absolue** : Toutes les réponses ci-dessous sont exclusivement étayées par le code source, les catalogues réels et les mesures empiriques consignées dans le dépôt. Tout élément non testé sur notre banc d'essai est explicitement qualifié de **« non mesuré »**.

---

## Sommaire
- [I. Intégrité Financière & Préservation des Données (Q1 à Q4)](#i-intégrité-financière--préservation-des-données)
- [II. Indépendance & Non-Intrusion sur le Site Cible (Q5 à Q7)](#ii-indépendance--non-intrusion-sur-le-site-cible)
- [III. Choix des Langues & Validation Linguistique (Q8 à Q12)](#iii-choix-des-langues--validation-linguistique)
- [IV. Sécurité, Confidentialité & Secrets (Q13 à Q15)](#iv-sécurité-confidentialité--secrets)
- [V. Mode Hors-Ligne & Résilience Réseau (Q16 à Q18)](#v-mode-hors-ligne--résilience-réseau)
- [VI. Licences, Dépendances & Propriété Intellectuelle (Q19 à Q21)](#vi-licences-dépendances--propriété-intellectuelle)
- [VII. Contenu Inédit, Limites & Durabilité (Q22 à Q25)](#vii-contenu-inédit-limites--durabilité)
- [VIII. Plan de Secours de Démonstration (Scénarios de Crise)](#viii-plan-de-secours-de-démonstration-scénarios-de-crise)

---

## I. Intégrité Financière & Préservation des Données

### Q1. Comment garantissez-vous qu'aucun montant, frais ou numéro de compte n'est altéré lors de la traduction ?
**Réponse** :  
Par un masquage déterministe par jetons inviolables avant toute opération linguistique, implémenté dans [`backend/protect.py`](../backend/protect.py) et [`extension/content.js`](../extension/content.js) :
1. Les entités critiques (montants, devises, frais, dates, téléphones, IBAN CM21, numéros de compte, références transactionnelles) sont extraites par des expressions régulières strictes et remplacées par des jetons synthétiques uniques (`__NUM_0__`, `__CURR_0__`, etc.).
2. Le moteur linguistique ne manipule que ces jetons opaques sans jamais modifier les chiffres ou devises.
3. Après traduction, la fonction `restore_tokens()` réinsère rigoureusement chaque valeur d'origine à son emplacement exact.
- **Résultat vérifié** : 0 altération constatée sur les 91 cas d'épreuve de [`tests_integrite/cases.json`](../tests_integrite/cases.json) et sur les 60 injections de la répétition finale sur le panneau jury ([`docs/repetition_finale.md`](repetition_finale.md)).

### Q2. Que se passe-t-il si un algorithme ou un modèle de traduction modifie ou supprime un montant financier ?
**Réponse** :  
Le système déclenche un **repli de sécurité immédiat vers le texte source original** sans erreur silencieuse :
- La fonction `verify_integrity()` vérifie qu'exactement 100 % des jetons masqués sont présents dans la chaîne restituée.
- Si un seul jeton manque, a été altéré ou dupliqué (comme observé lors de tests du modèle neuronal Fulfulde sur 6 libellés sensibles), la proposition est rejetée et le texte source en français ou anglais est réaffiché intégralement ([`backend/protect.py:L140-L165`](../backend/protect.py)).

### Q3. Comment sont gérés les montants écrits en toutes lettres ou les formats atypiques (espaces insécables, devises préfixées) ?
**Réponse** :  
Le parseur d'intégrité normalise les espaces insécables standards (`\u00A0`) et fines (`\u202F`), et intègre des motifs regex spécifiques pour les montants en toutes lettres (*« vingt-cinq mille »*, *« cent mille francs CFA »*) ainsi que les devises préfixées ou suffixées (*« FCFA 25 000 »*, *« 25.000 XAF »*) :
- Ces variantes sont couvertes dans `OFFLINE_SENSITIVE_PATTERNS` de [`extension/content.js`](../extension/content.js) et testées avec succès sur les cas `T034` à `T043` de [`tests_integrite/cases.json`](../tests_integrite/cases.json).

### Q4. Votre système a-t-il déjà été confronté à des cas d'attaque ou d'injection hostile sur des données financières ?
**Réponse** :  
Oui. Le banc d'épreuve [`tests_integrite/cases.json`](../tests_integrite/cases.json) contient **61 cas hostiles** spécialement conçus pour piéger les systèmes de traduction :
- Tentatives d'altération de décimales (`T044`), montants négatifs (`T045`), montants collés aux mots (`T046`), pourcentages de frais (`T048`), devises étrangères imbriquées (`T049`), doublons de montants dans une même phrase (`T073`), et URLs piégées contenant des paramètres sensibles (`T065`).
- **Résultat mesuré** : 100 % de succès (91/91 cas validés dans [`tests/test_integrite_figee.py`](../tests/test_integrite_figee.py) sur le pipeline algorithmique et l'API).

---

## II. Indépendance & Non-Intrusion sur le Site Cible

### Q5. Avez-vous modifié le code source du site cible https://safinum.cm/hackathon-test ?
**Réponse** :  
**Non, absolument aucune modification.**  
Conformément à la règle 1 d'[`AGENTS.md`](../AGENTS.md), le site cible est traité comme une boîte noire immuable :
- L'accessibilité est fournie entièrement de l'extérieur par une extension de navigateur Manifest V3 via un `content_script` isolé.
- Aucune balise, aucun script et aucune feuille de style n'ont été injectés ou modifiés sur le serveur distant `safinum.cm`.

### Q6. Comment l'extension s'intègre-t-elle dans une page web sans casser les scripts et styles du site hôte ?
**Réponse** :  
Grâce à un cloisonnement strict par **Shadow DOM ouvert** ([`extension/content.js:L180-L240`](../extension/content.js)) :
- Le widget d'accessibilité SAFINUM est encapsulé dans son propre arbre `#safinum-accessibility-host`.
- Tous ses styles CSS sont strictement confinés au Shadow DOM, évitant toute fuite ou conflit avec les règles CSS de l'application bancaire hôte.
- Les traductions in-situ utilisent un parcours direct des nœuds textuels (`TreeWalker` textuel) sans détruire les nœuds du DOM ni casser les gestionnaires d'événements JavaScript attachés aux boutons et formulaires.

### Q7. Si le site cible met à jour son interface ou modifie son DOM dynamiquement, l'extension fonctionne-t-elle toujours ?
**Réponse** :  
Oui, grâce à un `MutationObserver` instrumenté et stabilisé :
- L'extension observe les ajouts de nœuds et les changements textuels au sein de `#app` avec un debounce de 160 ms.
- Elle applique un verrou d'observation (`state.isMutating = true`) et marque les éléments traités par `data-safinum-translated="true"` pour prévenir formellement toute boucle infinie de ré-observation.
- **Preuve mesurée** : Sur un parcours dynamique de 5 étapes bancaires (Solde, Frais, Bénéficiaire, Récapitulatif, Reçu), le système traite exactement **41 mutations en 5 lots** et converge vers **0 mutation résiduelle** après stabilisation ([`docs/mesures_performance.md:L99-L132`](mesures_performance.md)).

---

## III. Choix des Langues & Validation Linguistique

### Q8. Pourquoi avoir choisi le Duálá et le Ɓàsàa plutôt que d'autres langues nationales camerounaises ?
**Réponse** :  
Pour trois raisons documentées dans [`docs/langue_et_validation.md`](langue_et_validation.md) et [`docs/etat_des_donnees.md`](etat_des_donnees.md) :
1. **Poids démographique et économique** : Ce sont deux langues majeures parlées dans les principaux bassins d'activité commerciale et de transactions financières du pays (Littoral, Wouri, Moungo, Sanaga-Maritime, Nyong-et-Kéllé).
2. **Disponibilité des ressources d'amorçage** : Ce sont les deux seules langues camerounaises disposant d'un jeu vérifié de chaînes d'interface logicielle libres téléchargées (Common Voice DS-06 : 283 chaînes pour le Duálá et 516 pour le Ɓàsàa ; MediaWiki DS-30 : 565 messages pour le Duálá).
3. **Faisabilité de la validation locale** : Disponibilité de réseaux associatifs et linguistiques identifiables à Douala et Yaoundé pour la campagne de relecture humaine.

### Q9. Pourquoi le Fulfulde est-il écarté ?
**Réponse** :  
Le Fulfulde a été intégré et évalué sur un banc d'essai réel ([`catalogue/evaluation_fulfulde_20.csv`](../catalogue/evaluation_fulfulde_20.csv)), puis **formellement écarté du parcours nominal** pour des motifs techniques et de sécurité :
1. **Hallucinations sévères observées** : Répétitions en boucle (*« Ɓe njaɓi ɓe, ɓe njaɓi ɓe... »* pour *« Frais »*), anglicismes bruts non traduits (*« Balance »*, *« Transaction reference »*) et dérives religieuses hors contexte (*« To gooŋgaay ɗowtanaago Allah... »* pour *« Confirmer le transfert »*).
2. **Défaillance de préservation financière** : Le modèle omet les jetons de protection masqués sur 6 phrases sensibles, obligeant notre garde-fou à basculer en repli source français.
3. **Variété non vérifiée et absence de relecture native** : Qualité intrinsèque non mesurée, et risque de confusion entre le Fulfulde Adamawa du Cameroun (`fub`) et les variétés nigérianes (`fuv`).
- Le moteur reste accessible uniquement via un commutateur expérimental explicite dans le widget avec bandeau d'alerte ([`docs/langue_et_validation.md:L83-L107`](langue_et_validation.md)).

### Q10. Pourquoi 0 chaîne validée par un locuteur natif à ce jour ?
**Réponse** :  
Par **transparence et rigueur éthique absolue** :
- Conformément à la règle 4 d'[`AGENTS.md`](../AGENTS.md), il est formellement interdit de présenter une traduction automatique ou rédigée par IA comme une traduction authentique.
- À date de soumission du prototype technique (novembre 2026), aucun locuteur natif qualifié n'a encore formellement signé les fiches d'évaluation.
- Le catalogue compte **84 chaînes par langue**, toutes honnêtement déclarées au statut `machine_suggested` dans [`catalogue/translations.csv`](../catalogue/translations.csv).
- L'interface affiche en permanence un bandeau d'avertissement visible : *« ⚠️ Traductions générées par IA, non validées par un locuteur natif »*.

### Q11. Comment distinguez-vous une traduction automatique d'une traduction certifiée par un locuteur ?
**Réponse** :  
Par un cycle de vie d'états immuable à 4 niveaux défini dans [`AGENTS.md`](../AGENTS.md) :
- `draft` : Proposition rédigée ou modifiée.
- `machine_suggested` : Sortie brute d'un modèle d'IA (statut actuel des 84 chaînes).
- `human_validated` : Traduction confirmée, signée et horodatée par un locuteur natif identifié via [`scripts/importer_validation.py`](../scripts/importer_validation.py).
- `rejected` : Traduction rejetée en cas d'erreur ou d'ambiguïté.
- Le script d'ingestion refuse catégoriquement de promouvoir une ligne en `human_validated` si le code validateur ou la date fait défaut ([`backend/tests/test_validation_import.py`](../backend/tests/test_validation_import.py)).

### Q12. Comment ont été créées les traductions actuelles du catalogue si aucun locuteur natif ne les a encore validées ?
**Réponse** :  
Par une méthodologie en trois piliers supervisés :
1. **Brouillon IA avec périphrases obligatoires** : Recours à des formulations périphrastiques pour les concepts bancaires modernes sans équivalent littéral (*Nongi a moni* / *Mut a nkôs* pour « bénéficiaire » ; *Kwele ebolo* / *Tiba nsal* pour « annuler » ; *Su la moni ma lomabe* pour « plafond »).
2. **Recoupement lexical réel** : Confrontation avec les lexiques du projet Mélac (`lexique_bassa.json`, 994 entrées, montrant 4 termes 100 % attestés et 58 termes partiellement attestés ; Duálá à 0 % car le lexique Mélac ne contient que 7 termes anatomiques, documenté dans [`catalogue/crosscheck_rapport.csv`](../catalogue/crosscheck_rapport.csv)).
3. **Recoupement d'interface logicielle** : Confrontation avec les messages réels de Common Voice (MPL-2.0) et MediaWiki (GPL-2.0+), répertoriée dans [`catalogue/recoupement_ui_resultats.csv`](../catalogue/recoupement_ui_resultats.csv).

---

## IV. Sécurité, Confidentialité & Secrets

### Q13. Comment traitez-vous les données sensibles comme les codes OTP ou les codes PIN bancaires ?
**Réponse** :  
Par une **sanctuarisation absolue** à la fois côté extension et côté backend :
- La fonction `isSecretText()` dans [`extension/content.js`](../extension/content.js) et `has_confidential_secret()` dans [`backend/protect.py`](../backend/protect.py) détectent les formats sensibles (mots de passe, codes OTP à 4, 6 ou 8 chiffres, codes de validation).
- Tout libellé contenant un code secret est **restitué strictement à l'identique**, n'est **jamais traduit** et n'est **jamais transmis sur le réseau** à l'API.
- **Résultat vérifié** : Testé sur les cas `T088`, `T089`, `T090` de [`tests_integrite/cases.json`](../tests_integrite/cases.json) dans [`tests/test_integrite_figee.py`](../tests/test_integrite_figee.py).

### Q14. Collectez-vous des données personnelles, bancaires ou analytiques des utilisateurs ?
**Réponse** :  
**Non, strictement aucune donnée.**  
Conformément à la règle 3 d'[`AGENTS.md`](../AGENTS.md) :
- Aucune télémétrie, aucun tracker, aucun cookie et aucun stockage persistant de données personnelles.
- Les requêtes au backend local ne contiennent que les fragments textuels anonymisés de l'interface ; aucune coordonnée bancaire ni solde réel n'est journalisé.

### Q15. Y a-t-il des clés d'API secrètes ou des identifiants sensibles embarqués dans l'extension ?
**Réponse** :  
**Aucune clé secrète.**  
- L'extension fonctionne soit de manière autonome avec son catalogue local embarqué, soit en s'adressant au backend local (`127.0.0.1:8000`).
- Aucun service tiers payant nécessitant un secret client n'est utilisé. Le fichier `.env.example` est exempt de tout secret.

---

## V. Mode Hors-Ligne & Résilience Réseau

### Q16. Que se passe-t-il si le backend est coupé ?
**Réponse** :  
L'extension **bascule instantanément et de manière transparente sur son mode hors-ligne nominal** :
1. Elle dispose d'un catalogue embarqué complet de 84 chaînes ([`extension/offline_catalog.json`](../extension/offline_catalog.json)).
2. L'échec du backend est mémorisé pour la session, évitant de pénaliser les chargements ultérieurs avec des timeouts réseau.
3. Le délai de repli a été optimisé à 400 ms maximum par tentative avec un seul hôte testé.
- **Performance mesurée sur banc d'essai** : Lorsque le backend est totalement arrêté, le premier rendu traduit apparaît en **79,22 ms en médiane** et **99,28 ms au $P_{95}$** ([`docs/mesures_performance.md:L34-L63`](mesures_performance.md)), respectant largement le seuil d'exigence (< 1 000 ms).

### Q17. Pourquoi faire passer les appels réseau par un Service Worker dans le Manifest V3 ?
**Réponse** :  
Pour respecter l'architecture sécurisée Manifest V3 et contourner les blocages stricts des navigateurs modernes :
- Les appels HTTP directs depuis un `content_script` sur une page HTTPS (`safinum.cm`) vers une API locale HTTP (`http://127.0.0.1:8000`) sont systématiquement bloqués par la politique de sécurité des navigateurs (Contenu Mixte, Private Network Access PNA).
- Le Service Worker d'arrière-plan ([`extension/background.js`](../extension/background.js)) gère ces requêtes avec des permissions strictement restreintes (`host_permissions: ["http://127.0.0.1:8000/*", "http://localhost:8000/*"]`) et communique avec le `content_script` par messages runtime.

### Q18. Quel est le volume exact de stockage nécessaire sur le terminal client pour faire fonctionner l'extension ?
**Réponse** :  
L'empreinte totale réelle sur disque du dossier client [`extension/`](../extension/) est de **125 034 octets (soit 122,10 Ko)**, répartie sur 7 fichiers légers :
- `content.js` : 40,6 Ko
- `offline_catalog.json` : 32,6 Ko
- `background.js` : 1,5 Ko
- `manifest.json` : 1,4 Ko
- Dossier `icons/` (3 PNG) : 48,9 Ko
- Aucun runtime Node.js, aucun modèle de plusieurs gigaoctets et aucun framework lourd n'est requis côté client ([`THIRD_PARTY.md`](../THIRD_PARTY.md)).

---

## VI. Licences, Dépendances & Propriété Intellectuelle

### Q19. Pourquoi ne pas avoir utilisé le modèle de traduction multilingue NLLB-200 de Meta ?
**Réponse** :  
Pour deux raisons rédhibitoires documentées dans [`docs/etat_des_donnees.md`](etat_des_donnees.md) :
1. **Absence totale des langues cibles** : Les codes ISO `dua` (Duálá) et `bas` (Ɓàsàa) sont **absents de NLLB-200 et du benchmark FLORES-200**. Parmi les langues liées au Cameroun, Meta ne couvre que le fulfulde nigérian (`fuv`), le haoussa et le kanouri.
2. **Restriction légale et non-certification** : NLLB est distribué sous licence de recherche **CC BY-NC 4.0** et sa carte modèle indique expressément qu'il n'est pas conçu pour la production ni pour les textes de domaines spécialisés (juridique, financier).

### Q20. Quelles sont les licences des bibliothèques tierces intégrées et respectent-elles le cadre commercial/hackathon ?
**Réponse** :  
Toutes les dépendances intégrées sont consignées dans [`THIRD_PARTY.md`](../THIRD_PARTY.md) :
- Côté extension : **0 dépendance externe**, JavaScript natif pur en conformité Web Standards.
- Côté backend : FastAPI (MIT), Uvicorn (BSD-3-Clause), Pydantic (MIT), Playwright (Apache-2.0, pour banc d'essai uniquement).
- Seul le module optionnel expérimental CTranslate2 / SentencePiece utilise le bundle Flagship sous licence CC BY-NC 4.0, isolé et désactivé par défaut.

### Q21. Pourquoi les jeux de données de recherche externes (Common Voice, MediaWiki, OPUS) ne sont-ils pas inclus dans le dépôt Git ?
**Réponse** :  
Par respect de la propreté du dépôt et des licences sous-jacentes :
- Ces jeux externes (situés hors dépôt dans `DOSSIER_RECHERCHE_DONNEES_SAFINUM`) relèvent de licences diverses (MPL-2.0, GPL-2.0+, CC0).
- Leurs chemins sont explicitement exclus dans [`.gitignore`](../.gitignore).
- Seules les extractions de recoupement dérivées nécessaires au fonctionnement figurent dans [`catalogue/recoupement_ui_resultats.csv`](../catalogue/recoupement_ui_resultats.csv).

---

## VII. Contenu Inédit, Limites & Durabilité

### Q22. Comment le système gère-t-il un libellé ou un message inédit qui n'existe pas dans le catalogue ?
**Réponse** :  
Par un traitement hybride prudent qui ne trompe jamais l'utilisateur ([`extension/content.js:L310-L380`](../extension/content.js)) :
1. **Préservation du texte source** : Le texte français original est conservé intact.
2. **Recherche de sous-termes financiers** : Si des termes du glossaire sont identifiés, leurs équivalents locaux sont proposés **entre crochets** immédiatement après le terme (ex: *« Solde [Moni mi yé] insuffisant »*).
3. **Balisage explicite** : Un badge visuel contrasté `[Contenu inédit]` est accolé au message pour avertir l'utilisateur que la formulation n'est pas issue du catalogue validé.
4. **Alertes de sécurité sanctuarisées** : Les avertissements de sécurité inédits (*« Ne partagez jamais votre code »*) sont maintenus en français sans altération par précaution.

### Q23. Quelles sont les principales limites actuelles du prototype ?
**Réponse** :  
Trois limites réelles documentées avec franchise :
1. **Catalogue à taille finie** : 84 chaînes par langue. Si une page bancaire utilise des formulations littéraires complexes très éloignées des libellés standards, l'extension affiche le texte source enrichi de gloses entre crochets.
2. **Sortie vocale non intégrée** : Le prototype actuel est une couche d'accessibilité visuelle/textuelle ; la synthèse vocale locale en langues camerounaises (TTS) n'est pas encore implémentée.
3. **Absence de certification native terrain** : Les 84 propositions actuelles sont au statut `machine_suggested` en attente de la signature des validateurs.

### Q24. Quelles sont les métriques réelles non mesurées que vous refusez d'inventer ?
**Réponse** :  
Conformément à la règle 10.4 d'[`AGENTS.md`](../AGENTS.md) et à [`docs/mesures_performance.md:L156-L167`](mesures_performance.md), les grandeurs suivantes sont formellement déclarées **« non mesuré »** :
- Consommation de batterie sur session mobile prolongée : **non mesuré**.
- Temps d'exécution sur smartphone ARM d'entrée de gamme (1 Go RAM) : **non mesuré** (tests exécutés sur PC de développement Windows 11 / Intel Core i7 / 32 Go RAM).
- Débit et latence sur réseau cellulaire réel 2G/EDGE en milieu rural : **non mesuré**.
- Taux d'intelligibilité auprès de populations analphabètes non scolarisées : **non mesuré**.
- Durée moyenne de remplissage de la fiche de validation par un locuteur : **non mesurée**.

### Q25. Comment le projet peut-il évoluer durablement vers 10 ou 20 langues nationales camerounaises ?
**Réponse** :  
Grâce à un modèle d'industrialisation modulaire et souverain :
1. **Architecture déclarative par fichiers CSV** : Ajouter une langue ne demande aucune refonte logicielle, simplement une colonne dans [`catalogue/translations.csv`](../catalogue/translations.csv) et un export JSON.
2. **Kit de validation reproductible** : Fiches de validation prêtes à l'emploi avec priorités de relecture (haute / normale) et livrets PDF 9 pt générés automatiquement ([`catalogue/kit_validation/`](../catalogue/kit_validation/)).
3. **Importateur certifié** : [`scripts/importer_validation.py`](../scripts/importer_validation.py) valide et ingère les retours humains avec traçabilité complète.

---

## VIII. Plan de Secours de Démonstration (Scénarios de Crise)

En situation de soutenance en direct devant le jury, tout incident technique imprévu doit être immédiatement contourné grâce aux protocoles de secours prévus ci-après :

```
┌────────────────────────────────────────────────────────────────────────────┐
│                    INCIDENT TECHNIQUE EN SOUTENANCE ?                      │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      │
         ┌────────────────────────────┼────────────────────────────┐
         ▼                            ▼                            ▼
┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│  RÉSEAU COUPÉ    │         │  SITE CIBLE HS   │         │ WIDGET INVISIBLE │
│ (Perte Internet) │         │ (safinum.cm lent)│         │(Bloqueur/Shadow) │
└────────┬─────────┘         └────────┬─────────┘         └────────┬─────────┘
         ▼                            ▼                            ▼
┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│  BASCULE OFFLINE │         │   MOCK LOCAL     │         │ INSPECTION & CLI │
│ Catalogue 122 Ko │         │  mock_bank.html  │         │  Scripts Python  │
│  Actif à 100 %   │         │  127.0.0.1:8000  │         │  Suites tests    │
└──────────────────┘         └──────────────────┘         └──────────────────┘
```

### Scénario 1 : Coupure totale de la connexion Internet en direct
- **Symptôme** : Perte de la connexion Wi-Fi / 4G de la salle de jury.
- **Action immédiate** :
  1. Continuer la démonstration sans interruption.
  2. Démontrer au jury la force architecturale de SAFINUM : l'extension fonctionne **100 % hors-ligne** grâce à son catalogue embarqué de 122 Ko ([`extension/offline_catalog.json`](../extension/offline_catalog.json)).
  3. Ouvrir le sélecteur de langue du widget : basculer entre Duálá et Ɓàsàa. Les 84 libellés sont traduits localement en **moins de 80 ms**.
  4. Couper volontairement le backend local devant le jury pour prouver le repli hors-ligne automatique sans dégradation.

### Scénario 2 : Le site cible https://safinum.cm/hackathon-test est lent, indisponible ou renvoie une erreur serveur
- **Symptôme** : Le serveur distant du hackathon subit un ralentissement (> 10 s), un crash HTTP 500 ou une coupure DNS.
- **Action immédiate** :
  1. Basculer sur la maquette locale conforme intégrée au dépôt : [`tests/mock_bank.html`](../tests/mock_bank.html).
  2. Ouvrir la maquette dans le navigateur Edge réel :
     `file:///C:/Users/FLEX%20ZONE/Desktop/linguafin-cameroun/tests/mock_bank.html`
  3. Cette maquette reproduit rigoureusement l'ensemble des conteneurs, formulaires, montants, frais et alertes bancaires du site cible.
  4. Montrer que l'extension s'y greffe avec une fidélité identique (traduction dynamique, surbrillance des montants, badge bilingue).

### Scénario 3 : Le widget Shadow DOM ne s'affiche pas ou est bloqué
- **Symptôme** : Un paramètre de sécurité du navigateur ou un bloqueur d'éléments empêche l'apparition du bouton flottant d'accessibilité.
- **Action immédiate** :
  1. Vérifier dans la console Edge (F12) que l'extension est bien chargée.
  2. Si l'icône de l'extension est visible dans la barre d'outils Edge, inspecter l'élément racine `#safinum-accessibility-host` dans les éléments du DOM.
  3. Déclencher la bascule de langue directement via la console développeur :
     ```javascript
     window.__safinum_test_set_lang && window.__safinum_test_set_lang('dua');
     ```
  4. Si le navigateur hôte est totalement verrouillé, basculer sur la démonstration automatisée Playwright en direct avec la commande :
     ```powershell
     python scripts/repetition_finale.py
     ```
     qui lance une instance Microsoft Edge vierge, injecte les cas du jury, traduit la page et affiche les relevés d'intégrité en direct.
