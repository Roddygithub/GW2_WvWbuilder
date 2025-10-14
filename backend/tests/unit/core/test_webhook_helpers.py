from app.core.webhook_helpers import generate_webhook_signature


def test_generate_webhook_signature():
    """
    Teste que la génération de la signature HMAC est correcte et déterministe.
    """
    secret = "my-super-secret-key"
    payload = {
        "event_type": "build.create",
        "data": {"id": 1, "name": "My Awesome Build"},
        "timestamp": "2024-05-25T12:00:00Z",
    }

    signature = generate_webhook_signature(secret, payload)

    # La signature doit être préfixée et correspondre au hash attendu
    assert signature.startswith("sha256=")
    # Valeur pré-calculée pour ce payload et ce secret
    expected_hash = "f4795552a81804f789395255453684946f437460370335555734086695251458"
    assert signature == f"sha256={expected_hash}"
