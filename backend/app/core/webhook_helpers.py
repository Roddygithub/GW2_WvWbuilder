import hmac
import hashlib
import json
from typing import Dict, Any


def generate_webhook_signature(secret: str, payload: Dict[str, Any]) -> str:
    """
    Génère une signature HMAC-SHA256 pour un payload de webhook.

    Args:
        secret: Le secret partagé pour signer le payload.
        payload: Le dictionnaire du payload à signer.

    Returns:
        La signature hexadécimale.
    """
    payload_bytes = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    signature = hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()
    return f"sha256={signature}"
