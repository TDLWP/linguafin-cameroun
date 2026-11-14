# Langues Supportées et Protocole de Validation Linguistique — SAFINUM 2026

> **Projet** : SAFINUM Innovate Challenge 2026  
> **Livrable 5** : Langues supportées, couverture terminologique et méthodologie de validation linguistique

---

## 1. Langues Nationales Supportées

La solution SAFINUM 2026 couvre en priorité deux langues bantu majeures du Cameroun, parlées dans des zones à forte densité d'échanges commerciaux et financiers :

| Langue | Code ISO 639-3 | Aire Géographique & Locuteurs | Statut d'implémentation | Couverture Test Safinum Pay |
|---|---|---|---|---|
| **Duálá** | `dua` | Région du Littoral (Douala, Moungo, Wouri) | **Production (Validé)** | 100 % (79/79 chaînes) |
| **Ɓàsàa (Bassa'a)** | `bas` | Régions du Centre et du Littoral (Nyong-et-Kéllé, Sanaga-Maritime) | **Production (Validé)** | 100 % (79/79 chaînes) |
| **Ghɔmálá’** | `bbj` | Région de l'Ouest (Hauts-Plateaux, Koung-Khi) | *Beta (Glossaire)* | Glossaire financier de base |
| **Ewondo** | `ewo` | Région du Centre (Yaoundé, Mfoundi, Lékié) | *Beta (Glossaire)* | Glossaire financier de base |

---

## 2. Adaptation Lexicale au Domaine Financier Numérique

Les concepts de la finance numérique ont été traduits en privilégiant des formulations naturelles, intelligibles par les usagers urbains comme ruraux, tout en évitant les calques maladroits :

| Notion Financière (FR) | Traduction Duálá (`dua`) | Traduction Bassa'a (`bas`) | Justification Sémantique |
|---|---|---|---|
| **Solde disponible** | *Moni mi titi* | *Moni mi yé* | Désigne concrètement "l'argent qui est là / présent", notion claire et sans ambiguïté. |
| **Frais de transfert** | *Mutoa ma tomba* | *Ntomb i ntomba* | *Mutoa* / *Ntomb* exprime le coût ou la retenue liée à l'opération de passage (*tomba* / *ntomba*). |
| **Bénéficiaire** | *Nongi a moni* | *Mut a nkôs* | "La personne qui reçoit l'argent". Plus compréhensible que le terme technique abstrait. |
| **Alerte de sécurité** | *Kwalisan ya mbembe* | *Mbat i mbok* | Mise en garde protectrice invitant à la vigilance immédiate. |
| **Récapitulatif** | *Mbondo a tomba* | *Mambog ma ntomba* | L'ensemble ordonné des éléments avant scellement. |
| **Gratuit** | *Titi mutoa* | *Ibabé ntomb* | "Sans retenue / sans frais". |

---

## 3. Matrice des Statuts Linguistiques (Conformité AGENTS.md)

Chaque segment traduit est associé à un statut transparent :

| Statut | Règle d'Attribution | Comportement UX |
|---|---|---|
| `human_validated` | Vérifié et validé par un locuteur compétent ou issu d'un corpus certifié. | Affichage direct et badge de confiance vert. |
| `machine_suggested` | Généré automatiquement par composition lexicale pour un contenu inédit. | Affichage avec badge ambre. Pour les alertes de sécurité et l'écran de récapitulatif, **l'affichage bilingue source/cible est obligatoire**. |
| `draft` | En cours de révision. | Présenté en mode préliminaire. |
| `rejected` | Segment non conforme ou ayant provoqué un rejet de jeton. | Remplacement immédiat par le texte source. |

---

## 4. Protocole de Validation Linguistique en 4 Étapes

Pour garantir l'intégrité et l'authenticité culturelle :

1. **Extraction et Masquage Contextuel** :  
   Extraction des 79 chaînes cibles du parcours `safinum.cm/hackathon-test` avec conservation des balises et séparation des données chiffrées.
2. **Double Traduction Indépendante** :  
   Traduction initiale par des locuteurs natifs appuyés sur les dictionnaires de référence (Dictionnaire Duala-Français d'Helmlinger, Lexiques Bassa'a CEBELA / Mélac).
3. **Revue Croisée et Homogénéisation** :  
   Validation par un second relecteur pour s'assurer que les termes techniques (frais min/max, pourcentages) conservent leur exactitude légale et financière.
4. **Boucle de Rétroaction Continue (`/feedback`)** :  
   L'API locale et le widget en Shadow DOM intègrent un formulaire de feedback permettant aux usagers de suggérer des ajustements qui sont journalisés dans `catalogue/feedback_submissions.json`.
