# docs/guide_integration_tiers.md — Guide d'Intégration Tiers en Cinq Étapes (Zero Modification du Code Client)

> **Projet** : SAFINUM 2026 — Couche souveraine d'accessibilité linguistique pour services financiers camerounais  
> **Principe fondamental** : **Zéro modification du code de l'application bancaire ou financière hôte**. L'intégration s'effectue en surcouche étanche et non intrusive via une extension Manifest V3 et une API locale REST standardisée.

---

## 1. Vue d'Ensemble de l'Intégration

La couche SAFINUM s'interface avec n'importe quelle application financière web (portail bancaire, microfinance, portefeuille mobile, interface USSD webifiée) sans toucher à un seul fichier de son code source.

Deux modes d'intégration complémentaires sont disponibles :
1. **Mode Surcouche DOM Automatique (Extension Web)** : Aucune ligne de code à écrire dans l'application cible. L'extension observe les nœuds textuels du DOM, masque les montants/frais/bénéficiaires, les traduit et injecte un widget flottant en Shadow DOM étanche.
2. **Mode Appel API REST Découplé (curl / fetch)** : Pour les intégrateurs souhaitant consommer directement le moteur de traduction souverain et les garanties d'intégrité financière de SAFINUM dans leurs propres pipelines applicatifs.

---

## 2. Intégration en Cinq Étapes

### Étape 1 : Charger l'extension dans le navigateur (Edge / Chrome)
1. Ouvrez Microsoft Edge (ou Google Chrome) et rendez-vous sur la page des extensions :
   - Edge : `edge://extensions/`
   - Chrome : `chrome://extensions/`
2. Activez le **Mode développeur** (interrupteur en bas à gauche sur Edge ou en haut à droite sur Chrome).
3. Cliquez sur le bouton **Charger le dossier décompressé** (*Load unpacked*).
4. Sélectionnez le répertoire `extension/` du dépôt `linguafin-cameroun`.
5. L'extension « **SAFINUM - Couche d'Accessibilité Financière en Langues Camerounaises** » (v1.0.0) apparaît active dans la liste.

> **Garantie d'étanchéité** : Le widget et ses feuilles de style résident dans un Shadow DOM fermé (`mode: "closed"`). Aucun style CSS de l'extension ne déborde sur l'application hôte, et aucun style de l'hôte ne perturbe le widget.

---

### Étape 2 : Déclarer le domaine du service tiers dans les autorisations
Pour connecter la couche à un nouveau portail bancaire (ex: `https://banque-tiers.cm` ou `http://localhost:3000`), deux configurations déclaratives suffisent :

#### A. Côté Extension (`extension/manifest.json`)
Ajoutez l'URL de votre service dans le tableau `host_permissions` :
```json
{
  "manifest_version": 3,
  "name": "SAFINUM - Couche d'Accessibilité Financière en Langues Camerounaises",
  "permissions": [],
  "host_permissions": [
    "https://safinum.cm/hackathon-test*",
    "https://banque-tiers.cm/*",
    "http://127.0.0.1:8000/*"
  ]
}
```

#### B. Côté Backend (`.env`)
Déclarez le domaine tiers dans les origines CORS autorisées :
```env
ALLOWED_ORIGINS="https://safinum.cm,https://banque-tiers.cm,http://localhost:8000,http://127.0.0.1:8000"
```

---

### Étape 3 : Lancer l'API locale souveraine FastAPI
Assurez-vous que les dépendances sont installées (`pip install -r backend/requirements.txt`), puis démarrez le serveur uvicorn sur la boucle locale :

```powershell
python -m uvicorn backend.api:app --host 127.0.0.1 --port 8000
```

*Sortie console attendue au démarrage* :
```text
INFO:     Started server process [18420]
INFO:     Waiting for application startup.
2026-11-18 08:28:20,012 [INFO] Index EN→FR chargé : 79 entrées
2026-11-18 08:28:20,015 [INFO] Catalogues chargés : 168 traductions (dua: 84, bas: 84), 52 termes glossaire
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

Pour vérifier que le service est opérationnel :
```powershell
curl.exe -s http://127.0.0.1:8000/health
```
*Réponse réelle* :
```json
{
  "status": "ok",
  "version": "1.0.0",
  "offline_catalog_loaded": true,
  "active_languages_count": 2,
  "ml_model_available": true,
  "uptime_seconds": 1.45
}
```

---

### Étape 4 : Appel REST avec `curl` (Testé et Certifié)
Les intégrateurs backend ou scripts tiers peuvent soumettre directement des lots de segments textuels via l'endpoint `/translate/batch`.

#### Commande d'exécution réelle :
```bash
curl -X POST http://127.0.0.1:8000/translate/batch \
  -H "Content-Type: application/json" \
  -d '{
    "source_lang": "fr",
    "target_lang": "dua",
    "items": [
      {
        "id": "item_1",
        "text": "Solde disponible : 25 000 FCFA"
      },
      {
        "id": "item_2",
        "text": "Frais de transfert : 1 500 FCFA"
      }
    ]
  }'
```

#### Sortie brute réelle constatée lors du test :
```json
{
  "target_lang": "dua",
  "total_items": 2,
  "verified_integrity_rate": 1.0,
  "items": [
    {
      "id": "item_1",
      "source_text": "Solde disponible : 25 000 FCFA",
      "target_text": "Solde disponible [Moni mi titi o bolane] : 25 000 FCFA",
      "status": "machine_suggested",
      "integrity_verified": true,
      "masked_tokens_count": 1,
      "bilingual_required": true,
      "novel_annotated": true,
      "badge": "contenu inédit : termes annotés, phrase non traduite"
    },
    {
      "id": "item_2",
      "source_text": "Frais de transfert : 1 500 FCFA",
      "target_text": "Frais de transfert [Mutoa ma tomba] : 1 500 FCFA",
      "status": "machine_suggested",
      "integrity_verified": true,
      "masked_tokens_count": 1,
      "bilingual_required": true,
      "novel_annotated": true,
      "badge": "contenu inédit : termes annotés, phrase non traduite"
    }
  ]
}
```

> **Observation critique** : Les montants financiers `25 000 FCFA` et `1 500 FCFA` sont restés **100% intacts** (`masked_tokens_count: 1`, `integrity_verified: true`). Les termes inconnus ont été annotés entre crochets bilingues sans altérer la phrase source.

---

### Étape 5 : Appel avec `fetch` JavaScript (Testé et Certifié)
Pour les applications monopages (Vue, React, Angular) ou les services Node.js souhaitant consommer directement l'API en tâche de fond.

#### Snippet JavaScript exécutable :
```javascript
const payload = {
  source_lang: "fr",
  target_lang: "bas", // Bassa'a
  items: [
    {
      id: "item_1",
      text: "Solde disponible : 50 000 FCFA"
    },
    {
      id: "item_2",
      text: "Ce bénéficiaire n'a jamais été utilisé sur ce compte. Vérifiez le numéro avant de continuer."
    }
  ]
};

async function traduireInterface() {
  try {
    const response = await fetch("http://127.0.0.1:8000/translate/batch", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      throw new Error(`Erreur HTTP: ${response.status}`);
    }

    const data = await response.json();
    console.log("Résultat reçu du backend :", data);
    return data;
  } catch (error) {
    console.warn("API locale indisponible, repli sur le catalogue embarqué", error);
  }
}

traduireInterface();
```

#### Sortie console réelle constatée lors de l'exécution Node.js :
```json
{
  "target_lang": "bas",
  "total_items": 2,
  "verified_integrity_rate": 1.0,
  "items": [
    {
      "id": "item_1",
      "source_text": "Solde disponible : 50 000 FCFA",
      "target_text": "Solde disponible [Moni mi yé inyu salo] : 50 000 FCFA",
      "status": "machine_suggested",
      "integrity_verified": true,
      "masked_tokens_count": 1,
      "bilingual_required": true,
      "novel_annotated": true,
      "badge": "contenu inédit : termes annotés, phrase non traduite"
    },
    {
      "id": "item_2",
      "source_text": "Ce bénéficiaire n'a jamais été utilisé sur ce compte. Vérifiez le numéro avant de continuer.",
      "target_text": "Nu a nkôs a nsal bé kii hane o kompiti yini. Béñgê namba ilole u nkenel bisu.",
      "status": "machine_suggested",
      "integrity_verified": true,
      "masked_tokens_count": 0,
      "bilingual_required": false,
      "novel_annotated": false,
      "badge": null
    }
  ]
}
```

---

## 3. Matrice Récapitulative des Statuts de Réponse

| Statut (`status`) | Signification opérationnelle | Action de l'application hôte |
|---|---|---|
| `human_validated` | Traduction certifiée par un locuteur natif | Affichage direct substitutif dans la langue locale |
| `machine_suggested` | Traduction générée par modèle ou glossaire non validée | Affichage bilingue obligatoire sur éléments financiers |
| `fallback_source` | Repli de sécurité (chaîne inconnue ou intégrité non prouvée) | Conservation intégrale du texte source d'origine |
| `rejected` | Terme formellement révoqué par le comité de relecture | Conservation stricte du texte source |

---

## 4. Dépannage et Bonnes Pratiques

1. **Erreur CORS en navigateur (`No 'Access-Control-Allow-Origin' header`)** :  
   Vérifiez que le domaine de votre application figure bien dans `ALLOWED_ORIGINS` dans le fichier `.env` du backend.
2. **Erreur 429 Too Many Requests** :  
   Le serveur intègre une protection anti-DoS limitant le débit à 120 requêtes/minute par adresse IP. Utilisez des requêtes par lot (`items`) au lieu de requêtes unitaires.
3. **Disponibilité hors-ligne** :  
   Si l'API FastAPI est éteinte, l'extension bascule instantanément et automatiquement sur le catalogue hors-ligne embarqué (`offline_catalog.json`) sans générer d'erreur visible pour l'utilisateur.
