# -*- coding: utf-8 -*-
"""
Serveur API locale FastAPI pour SAFINUM Innovate Challenge 2026.
Conforme à docs/01_architecture.md et openapi.yaml.

Fonctionnalités :
- Chargement des catalogues CSV au démarrage (translations.csv, glossaire.csv)
- Chaîne de résolution stricte : Mémoire validée -> Glossaire -> Moteur automatique -> Repli source
- Intégrité financière absolue via protect.py (masquage/restauration/verify_integrity)
- CORS restreint et configurable via .env
- Limites strictes de taille (anti-DoS)
- AUCUNE JOURNALISATION DU TEXTE DES UTILISATEURS (confidentialité bancaire et RGPD)
"""

import os
import csv
import json
import time
import logging
import unicodedata
from typing import List, Optional, Dict
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.protect import (
    mask_sensitive_data,
    restore_sensitive_data,
    verify_integrity,
    annotate_glossary_in_masked_text,
    SECURITY_ALERT_KEYWORDS,
    is_security_alert_text
)
from backend.engine import TranslationEngine, AutomaticMockEngine, TranslationEngineError, TranslationEngineTimeoutError

load_dotenv()

# Réglage ANNOTATE_SECURITY_ALERTS (défaut : false)
ANNOTATE_SECURITY_ALERTS = os.getenv("ANNOTATE_SECURITY_ALERTS", "false").strip().lower() in ("true", "1", "yes")


# Configuration du logger : AUCUN TEXTE UTILISATEUR NE DOIT ÊTRE ENREGISTRÉ
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("safinum_api")

app = FastAPI(
    title="SAFINUM Local Translation & Accessibility API",
    version="1.0.0",
    description="API locale souveraine d'accessibilité linguistique pour services financiers camerounais."
)

# Configuration CORS restreinte
raw_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "https://safinum.cm,http://localhost:8000,http://127.0.0.1:8000,http://localhost:3000,http://localhost:5173"
)
allowed_origins = [o.strip() for o in raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Limites de sécurité
MAX_BATCH_SIZE = int(os.getenv("MAX_BATCH_SIZE", "100"))
MAX_TEXT_LENGTH = int(os.getenv("MAX_TEXT_LENGTH", "2000"))

# Limitation de débit (Rate Limiting anti-DoS en mémoire)
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "120"))
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").strip().lower() in ("true", "1", "yes")

_request_timestamps_by_ip: Dict[str, List[float]] = {}


def check_rate_limit(client_ip: str) -> bool:
    """Vérifie si une adresse IP a dépassé le quota de requêtes autorisées par minute."""
    if not RATE_LIMIT_ENABLED:
        return True
    now = time.time()
    window_start = now - 60.0
    timestamps = _request_timestamps_by_ip.setdefault(client_ip, [])
    # Élaguer les requêtes antérieures à la fenêtre glissante de 60s
    timestamps[:] = [t for t in timestamps if t > window_start]
    if len(timestamps) >= RATE_LIMIT_PER_MINUTE:
        return False
    timestamps.append(now)
    return True


def reset_rate_limit():
    """Réinitialise les compteurs de requêtes par IP (utilitaire de test)."""
    _request_timestamps_by_ip.clear()


@app.middleware("http")
async def rate_limiting_middleware(request: Request, call_next):
    # Les requêtes OPTIONS (CORS preflight) ne consomment pas de quota
    if request.method == "OPTIONS":
        return await call_next(request)

    client_ip = request.client.host if request.client else "127.0.0.1"
    if not check_rate_limit(client_ip):
        logger.warning("Rate limit exceeded for client IP: %s", client_ip)
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Limite de débit dépassée (trop de requêtes). Veuillez patienter."},
            headers={"Retry-After": "60"}
        )
    return await call_next(request)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Journalisation strictement anonyme de l'incident sans fuite de stack trace ou d'infos techniques
    logger.error("Unhandled internal exception: %s", type(exc).__name__)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Une erreur interne s'est produite. Aucun détail technique n'est divulgué."}
    )

START_TIME = time.time()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_TRANSLATIONS_PATH = os.path.join(BASE_DIR, "catalogue", "translations.csv")
CSV_GLOSSAIRE_PATH    = os.path.join(BASE_DIR, "catalogue", "glossaire.csv")
FEEDBACK_FILE         = os.path.join(BASE_DIR, "catalogue", "feedback_submissions.json")
EN_TO_FR_INDEX_PATH   = os.path.join(BASE_DIR, "data", "en_to_fr_index.json")


def normalize_en_key(s: str) -> str:
    """Normalise une chaîne EN pour la comparaison d'index (NFKC, lower, espaces insécables -> espace)."""
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("\u00A0", " ").replace("\u202F", " ").replace("\u2007", " ")
    return s.lower().strip()


def load_en_to_fr_index() -> Dict[str, str]:
    """Charge l'index EN→FR depuis data/en_to_fr_index.json.
    Retourne {en_normalized: fr_source}. Ne lève jamais d'exception."""
    if not os.path.exists(EN_TO_FR_INDEX_PATH):
        logger.warning("Index EN→FR introuvable : %s", EN_TO_FR_INDEX_PATH)
        return {}
    try:
        with open(EN_TO_FR_INDEX_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        idx = data.get("en_to_fr", {})
        logger.info("Index EN→FR chargé : %d entrées", len(idx))
        return idx
    except Exception as exc:
        logger.error("Erreur chargement index EN→FR : %s", exc)
        return {}

# Index global EN→FR chargé au démarrage
EN_INDEX: Dict[str, str] = load_en_to_fr_index()




# Structures en mémoire
class TranslationMemory:
    def __init__(self):
        # Format : { "dua": { "source_fr": ("cible", "statut", "cle") }, "bas": { ... } }
        self.translations: Dict[str, Dict[str, Dict[str, str]]] = {}
        # Format : { "source_fr": { "dua": "cible", "bas": "cible" } }
        self.glossary: Dict[str, Dict[str, str]] = {}
        self.load_catalogs()

    def load_catalogs(self):
        # 1. Chargement de translations.csv
        if os.path.exists(CSV_TRANSLATIONS_PATH):
            with open(CSV_TRANSLATIONS_PATH, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    lang = row["langue"].strip().lower()
                    src = row["source"].strip()
                    tgt = row["cible"].strip()
                    stat = row.get("statut", "machine_suggested").strip()
                    key = row.get("cle", "").strip()

                    if lang not in self.translations:
                        self.translations[lang] = {}
                    self.translations[lang][src] = {
                        "target": tgt,
                        "status": stat,
                        "key": key
                    }

        # 2. Chargement de glossaire.csv
        if os.path.exists(CSV_GLOSSAIRE_PATH):
            with open(CSV_GLOSSAIRE_PATH, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    src = row["terme_source"].strip()
                    lang = row["langue"].strip().lower()
                    tgt = row["terme_cible"].strip()

                    if src not in self.glossary:
                        self.glossary[src] = {}
                    self.glossary[src][lang] = tgt


from backend.engine import (
    TranslationEngine,
    TranslationEngineError,
    TranslationEngineTimeoutError,
    AutomaticMockEngine,
    CTranslate2FulfuldeEngine
)

MEMOIRE = TranslationMemory()
# Moteur automatique par défaut
AUTO_ENGINE: TranslationEngine = AutomaticMockEngine()
# Moteur CTranslate2 local dédié au Fulfulde
FULFULDE_ENGINE: TranslationEngine = CTranslate2FulfuldeEngine()



# --- Modèles Pydantic ---

class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"
    offline_catalog_loaded: bool
    active_languages_count: int
    ml_model_available: bool = True
    uptime_seconds: float


class LanguageInfo(BaseModel):
    code: str
    name: str
    autonym: str
    status: str
    human_validated_entries: int
    glossary_entries: int


class TranslationItemRequest(BaseModel):
    id: str = Field(..., max_length=100)
    text: str
    screen_context: Optional[str] = Field("global", max_length=100)
    is_critical_security: Optional[bool] = False


class BatchTranslationRequest(BaseModel):
    source_lang: str = Field("fr", max_length=10)
    target_lang: str = Field("dua", max_length=10)
    allow_machine_translation: bool = True
    allow_experimental: bool = False
    annotate_security_alerts: Optional[bool] = None
    items: List[TranslationItemRequest]



class TranslationItemResponse(BaseModel):
    id: str
    source_text: str
    target_text: str
    status: str
    integrity_verified: bool
    masked_tokens_count: int
    bilingual_required: bool
    novel_annotated: Optional[bool] = False
    badge: Optional[str] = None


class BatchTranslationResponse(BaseModel):
    target_lang: str
    total_items: int
    verified_integrity_rate: float
    items: List[TranslationItemResponse]


class FeedbackRequest(BaseModel):
    source_text: str = Field(..., min_length=1, max_length=2000, description="Texte source")
    target_lang: str = Field(..., min_length=2, max_length=10, description="Code langue cible")
    suggested_translation: str = Field(..., min_length=1, max_length=2000, description="Traduction suggérée")
    screen_context: Optional[str] = Field("dashboard", max_length=100, description="Contexte de l'écran")
    validator_code: Optional[str] = Field(None, max_length=100, description="Code du validateur")
    comment: Optional[str] = Field(None, max_length=2000, description="Commentaire optionnel")


class FeedbackResponse(BaseModel):
    feedback_id: str
    status: str
    message: str


# --- Endpoints ---

@app.get("/health", response_model=HealthResponse)
def get_health():
    # Journalisation de monitoring anonyme
    logger.info("Health check requested")
    return HealthResponse(
        status="ok",
        version="1.0.0",
        offline_catalog_loaded=bool(MEMOIRE.translations),
        active_languages_count=len(MEMOIRE.translations),
        ml_model_available=True,
        uptime_seconds=round(time.time() - START_TIME, 2)
    )


@app.get("/languages", response_model=List[LanguageInfo])
def get_languages(include_experimental: bool = False):
    logger.info("Languages metadata requested (include_experimental=%s)", include_experimental)
    dua_trans = MEMOIRE.translations.get("dua", {})
    dua_human = sum(1 for v in dua_trans.values() if v.get("status") == "human_validated")
    bas_trans = MEMOIRE.translations.get("bas", {})
    bas_human = sum(1 for v in bas_trans.values() if v.get("status") == "human_validated")

    langs = [
        LanguageInfo(
            code="dua",
            name="Duala",
            autonym="Duálá",
            status="machine_suggested",
            human_validated_entries=dua_human,
            glossary_entries=len(MEMOIRE.glossary)
        ),
        LanguageInfo(
            code="bas",
            name="Bassa'a",
            autonym="Ɓàsàa",
            status="machine_suggested",
            human_validated_entries=bas_human,
            glossary_entries=len(MEMOIRE.glossary)
        ),
        LanguageInfo(
            code="bbj",
            name="Ghomala'",
            autonym="Ghɔmálá’",
            status="beta",
            human_validated_entries=0,
            glossary_entries=len(MEMOIRE.glossary)
        ),
        LanguageInfo(
            code="ewo",
            name="Ewondo",
            autonym="Ewondo",
            status="beta",
            human_validated_entries=0,
            glossary_entries=len(MEMOIRE.glossary)
        )
    ]

    if include_experimental:
        langs.append(
            LanguageInfo(
                code="ful",
                name="Fulfulde (Expérimental)",
                autonym="Fulfulde",
                status="experimental",
                human_validated_entries=0,
                glossary_entries=len(MEMOIRE.glossary)
            )
        )

    return langs


@app.post("/translate/batch", response_model=BatchTranslationResponse)
def translate_batch(req: BatchTranslationRequest):
    # 1. Validation des limites de taille (sécurité anti-DoS)
    if len(req.items) > MAX_BATCH_SIZE:
        logger.warning("Batch size limit exceeded: %d > %d", len(req.items), MAX_BATCH_SIZE)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Le lot dépasse la limite autorisée de {MAX_BATCH_SIZE} éléments."
        )

    for item in req.items:
        if len(item.text) > MAX_TEXT_LENGTH:
            logger.warning("Item text length limit exceeded: %d > %d", len(item.text), MAX_TEXT_LENGTH)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Un élément dépasse la longueur maximale de {MAX_TEXT_LENGTH} caractères."
            )

    target_lang = req.target_lang.lower().strip()
    lang_translations = MEMOIRE.translations.get(target_lang, {})
    glossary = MEMOIRE.glossary

    # Journalisation de monitoring STRICTEMENT ANONYME (aucun contenu textuel)
    logger.info("Processing translation batch: %d items, target_lang=%s", len(req.items), target_lang)

    output_items = []
    verified_count = 0

    source_lang = req.source_lang.lower().strip()
    annotate_sec_setting = (
        req.annotate_security_alerts
        if req.annotate_security_alerts is not None
        else ANNOTATE_SECURITY_ALERTS
    )

    for item in req.items:
        src_raw = item.text.strip()

        # Résolution EN→FR : si source_lang == "en", tenter de résoudre via l'index.
        # Le texte résolu (FR) est utilisé pour la recherche en mémoire et le masquage.
        # Règle : correspondance exacte normalisée uniquement, jamais inventée.
        # Si non résolu : traitement standard (badge "contenu inédit" si absent de la mémoire).
        if source_lang == "en":
            en_norm = normalize_en_key(src_raw)
            fr_equiv = EN_INDEX.get(en_norm)
            if fr_equiv:
                src_raw = fr_equiv   # on travaille avec la source FR

        # ÉTAPE 1 : Masquage des entités sensibles par jetons inviolables
        masked_src, token_map, token_order = mask_sensitive_data(src_raw)

        # Détection des alertes et avertissements de sécurité (factorisée)
        is_sec_alert = is_security_alert_text(src_raw) or bool(item.is_critical_security)

        # Détection étendue des contenus à sensibilité critique (montants, frais, avertissements, erreurs, récapitulatifs)
        critical_markers = {
            *SECURITY_ALERT_KEYWORDS,
            # Frais et tarifs
            "frais", "commission", "%", "pourcent", "tarif",
            # Erreurs et échecs
            "erreur", "échec", "echec", "insuffisant", "invalide", "rejeté", "rejete",
            "impossible", "error", "fail", "failed",
            # Récapitulatifs et confirmations
            "récapitulatif", "recapitulatif", "confirmation", "total à débiter", "total a debiter",
            # Devises et montants
            "fcfa", "xaf", "cfa", "eur", "usd", "frs", "solde", "montant"
        }
        src_lower = src_raw.lower()
        has_masked_sensitive = bool(token_map)
        is_critical = (
            is_sec_alert or
            has_masked_sensitive or
            any(marker in src_lower for marker in critical_markers)
        )

        # ÉTAPE 2 : Chaîne de résolution (Mémoire -> Glossaire -> Annotation inédite -> Repli)
        candidate_text: Optional[str] = None
        item_status = "fallback_source"
        novel_annotated = False
        novel_badge: Optional[str] = None

        # 2.1 Mémoire de traduction validée (recherche directe ou masquée)
        if src_raw in lang_translations:
            # Texte brut connu dans le catalogue
            candidate_text = lang_translations[src_raw]["target"]
            item_status = lang_translations[src_raw]["status"]
            # Si le texte validé est un template, on ré-applique le masquage pour restauration
            candidate_text, _ = mask_sensitive_data(candidate_text)[:2]
        elif masked_src in lang_translations:
            candidate_text = lang_translations[masked_src]["target"]
            item_status = lang_translations[masked_src]["status"]

        # 2.2 Terme exact du glossaire terminologique
        elif src_raw in glossary and target_lang in glossary[src_raw]:
            candidate_text = glossary[src_raw][target_lang]
            item_status = "machine_suggested"

        # 2.3 Texte absent de la mémoire : conservation du texte source + annotation des termes financiers du glossaire
        else:
            if is_sec_alert and not annotate_sec_setting:
                # Réglage ANNOTATE_SECURITY_ALERTS = false :
                # Les avertissements de sécurité et alertes restent en français sans annotation,
                # avec le badge « avertissement affiché en français : traduction non validée ».
                candidate_text = masked_src
                item_status = "fallback_source"
                novel_annotated = False
                novel_badge = "avertissement affiché en français : traduction non validée"
            else:
                annotated_masked, has_anno, _ = annotate_glossary_in_masked_text(masked_src, glossary, target_lang)
                if has_anno:
                    candidate_text = annotated_masked
                    item_status = "machine_suggested"
                    novel_annotated = True
                    novel_badge = "contenu inédit : termes annotés, phrase non traduite"
                else:
                    candidate_text = masked_src
                    item_status = "fallback_source"
                    novel_annotated = False
                    novel_badge = None


        # ÉTAPE 3 : Restauration et contrôle d'intégrité strict
        restored_text, is_valid = restore_sensitive_data(candidate_text, token_map, src_raw)

        # ÉTAPE 4 : Contrôle supplémentaire via verify_integrity
        if is_valid:
            if not verify_integrity(src_raw, restored_text, token_map):
                is_valid = False
                restored_text = src_raw
                item_status = "fallback_source"
                novel_annotated = False
                novel_badge = None

        if is_valid:
            verified_count += 1
        else:
            restored_text = src_raw
            item_status = "fallback_source"
            novel_annotated = False
            novel_badge = None

        # Règle spéciale bilinguisme pour contenus sensibles non attestés
        bilingual_req = is_critical and (item_status != "human_validated")

        # Règle critique : pour toute chaîne dont sensibilité est critique
        # (montants, frais, avertissements, erreurs) ET non attestée,
        # affiche le texte français d'origine suivi de la proposition entre crochets, sans le remplacer.
        # Exception : si la chaîne est un repli source ou identique après normalisation NFKC,
        # ou s'il s'agit d'un contenu inédit annoté terme par terme,
        # ne jamais insérer de crochets bilingues sur des montants ou nombres purs.
        is_same_text = (
            item_status == "fallback_source" or
            src_raw == restored_text or
            unicodedata.normalize("NFKC", src_raw).strip() == unicodedata.normalize("NFKC", restored_text).strip()
        )
        if novel_annotated:
            # Termes financiers déjà annotés individuellement entre crochets dans la phrase source
            final_target = restored_text
        elif is_same_text:
            final_target = src_raw
        elif bilingual_req and not restored_text.startswith(src_raw + " ["):
            final_target = f"{src_raw} [{restored_text}]"
        else:
            final_target = restored_text

        output_items.append(TranslationItemResponse(
            id=item.id,
            source_text=item.text,
            target_text=final_target,
            status=item_status,
            integrity_verified=is_valid,
            masked_tokens_count=len(token_map),
            bilingual_required=bilingual_req,
            novel_annotated=novel_annotated,
            badge=novel_badge
        ))

    rate = (verified_count / len(output_items)) if output_items else 1.0

    return BatchTranslationResponse(
        target_lang=target_lang,
        total_items=len(output_items),
        verified_integrity_rate=round(rate, 3),
        items=output_items
    )


@app.post("/feedback", response_model=FeedbackResponse, status_code=201)
def submit_feedback(req: FeedbackRequest):
    # Journalisation strictement anonyme (aucun texte utilisateur n'est loggué)
    logger.info("Feedback received for target_lang=%s, context=%s", req.target_lang, req.screen_context)

    submission = {
        "id": f"fbk_{int(time.time()*1000)}",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source_text": req.source_text,
        "target_lang": req.target_lang,
        "suggested_translation": req.suggested_translation,
        "screen_context": req.screen_context,
        "validator_code": req.validator_code or "COMMUNITY_USER",
        "comment": req.comment or ""
    }

    submissions = []
    if os.path.exists(FEEDBACK_FILE):
        try:
            with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
                submissions = json.load(f)
        except Exception:
            submissions = []

    submissions.append(submission)

    with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(submissions, f, ensure_ascii=False, indent=2)

    return FeedbackResponse(
        feedback_id=submission["id"],
        status="recorded",
        message="Proposition enregistrée avec succès pour examen linguistique."
    )
