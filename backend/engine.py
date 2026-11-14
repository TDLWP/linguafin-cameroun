# -*- coding: utf-8 -*-
"""
Module engine.py — Adaptateur de moteur de traduction automatique avec interface abstraite.
SAFINUM Innovate Challenge 2026.

RÈGLES :
- Interface abstraite TranslationEngine
- Clé d'API et configuration lues côté serveur dans l'environnement (.env)
- Gestion stricte du timeout (défaut : 2.0s)
- En cas d'erreur ou de timeout : levée d'exception gérée -> repli source garanti.
"""

import os
import time
from abc import ABC, abstractmethod
from typing import Optional
from dotenv import load_dotenv

# Chargement de la configuration serveur depuis .env
load_dotenv()


class TranslationEngineError(Exception):
    """Exception levée en cas d'échec du moteur de traduction automatique."""
    pass


class TranslationEngineTimeoutError(TranslationEngineError):
    """Exception levée en cas de dépassement de délai d'attente du moteur."""
    pass


class TranslationEngine(ABC):
    """Interface abstraite pour tout moteur de traduction automatique (NMT / LLM)."""

    def __init__(self, api_key: Optional[str] = None, timeout_seconds: float = 2.0):
        self.api_key = api_key or os.getenv("TRANSLATION_API_KEY", "")
        self.timeout_seconds = float(os.getenv("TRANSLATION_TIMEOUT_SECONDS", str(timeout_seconds)))

    @abstractmethod
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Traduit le texte source vers la langue cible.
        Doit respecter le délai imparti (self.timeout_seconds).
        Lève TranslationEngineTimeoutError si le délai expire.
        Lève TranslationEngineError en cas d'erreur d'API.
        """
        pass


class AutomaticMockEngine(TranslationEngine):
    """
    Adaptateur de moteur automatique local / heuristique pour l'évaluation et les tests.
    Gère la simulation d'appels API, les timeouts configurables et les erreurs.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout_seconds: float = 2.0,
        simulated_delay: float = 0.0,
        simulate_error: bool = False
    ):
        super().__init__(api_key=api_key, timeout_seconds=timeout_seconds)
        self.simulated_delay = simulated_delay
        self.simulate_error = simulate_error

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        # Vérification d'erreur simulée ou réelle
        if self.simulate_error:
            raise TranslationEngineError("Erreur interne du moteur de traduction automatique simulé.")

        # Vérification du timeout
        if self.simulated_delay > 0:
            if self.simulated_delay > self.timeout_seconds:
                # Simuler le temps partiel avant timeout
                time.sleep(min(self.timeout_seconds, 0.1))
                raise TranslationEngineTimeoutError(
                    f"Dépassement du délai d'attente ({self.simulated_delay}s > {self.timeout_seconds}s)."
                )
            time.sleep(self.simulated_delay)

        # Traduction heuristique de base (préservation stricte de tout jeton __SAFE_*__)
        return text


class CTranslate2FulfuldeEngine(TranslationEngine):
    """
    Adaptateur de moteur de traduction local pour Français -> Fulfulde.
    Utilise le modèle INT8 'flagship-ai/cameroon-int8' (dossier 'francais-fufulde').
    Licence : CC BY-NC 4.0.
    
    Règles strictes :
    - Le moteur reste optionnel : si les dépendances ou le modèle sont absents ou en erreur,
      repli source garanti sans planter.
    - Le masquage/restauration des valeurs financières est géré en amont/aval par protect.py.
    - Statut systématique : 'machine_suggested'.
    """

    def __init__(
        self,
        model_dir: Optional[str] = None,
        timeout_seconds: float = 5.0,
        device: str = "cpu",
        enabled: bool = False
    ):
        super().__init__(timeout_seconds=timeout_seconds)
        if model_dir is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.model_dir = os.path.join(base_dir, "models", "francais-fufulde")
        else:
            self.model_dir = model_dir
            
        self.device = device
        self.enabled = enabled  # Désactivé par défaut (évalué mais écarté pour incohérences observées)
        self._translator = None
        self._sp_source = None
        self._sp_target = None
        self._is_available = False
        self._load_error = None
        self._init_engine()

    def _init_engine(self):
        """Initialise le traducteur CTranslate2 et les tokeniseurs SentencePiece si disponibles."""
        try:
            import ctranslate2
            import sentencepiece as spm

            source_spm = os.path.join(self.model_dir, "source.spm")
            target_spm = os.path.join(self.model_dir, "target.spm")
            model_bin = os.path.join(self.model_dir, "model.bin")

            if not (os.path.exists(source_spm) and os.path.exists(target_spm) and os.path.exists(model_bin)):
                self._load_error = f"Fichiers du modèle introuvables dans {self.model_dir}"
                self._is_available = False
                return

            self._sp_source = spm.SentencePieceProcessor(model_file=source_spm)
            self._sp_target = spm.SentencePieceProcessor(model_file=target_spm)
            self._translator = ctranslate2.Translator(
                self.model_dir,
                device=self.device,
                intra_threads=2,
                inter_threads=1
            )
            self._is_available = True
            self._load_error = None
        except Exception as e:
            self._is_available = False
            self._load_error = str(e)

    def is_available(self) -> bool:
        """Indique si le modèle local Fulfulde est chargé, prêt et explicitement activé."""
        return self._is_available and self.enabled

    def translate(self, text: str, source_lang: str, target_lang: str, allow_experimental: bool = False) -> str:
        """
        Traduit le texte source vers le Fulfulde (ful/ff).
        En cas de moteur désactivé, d'indisponibilité ou d'erreur, renvoie le texte source sans planter.
        """
        # Le moteur est désactivé par défaut : ne répond que si le mode expérimental est explicitement autorisé
        if not (self.enabled or allow_experimental) or not self._is_available:
            return text

        # Vérification des langues compatibles
        if target_lang.lower() not in ("ful", "ff", "fufulde"):
            return text

        cleaned = text.strip()
        if not cleaned:
            return text

        try:
            start_t = time.time()
            # Tokenisation avec SentencePiece
            tokens = self._sp_source.encode(cleaned, out_type=str)
            # Ajout du token EOS requis par l'architecture Marian NMT
            if not tokens or tokens[-1] != "</s>":
                tokens.append("</s>")
            
            # Inférence CTranslate2
            results = self._translator.translate_batch(
                [tokens],
                max_batch_size=1,
                beam_size=2
            )
            
            if time.time() - start_t > self.timeout_seconds:
                # Timeout atteint -> repli source
                return text

            output_tokens = results[0].hypotheses[0]
            clean_out_tokens = [t for t in output_tokens if t not in ("</s>", "<pad>", "<unk>")]
            # Détokenisation SentencePiece cible
            translated_text = self._sp_target.decode(clean_out_tokens)
            return translated_text.strip() if translated_text.strip() else text
        except Exception:
            # Repli source en cas d'erreur interne sans planter
            return text

