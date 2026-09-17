#!/usr/bin/env python3
"""Generate the Ed25519 response-signing key for Machine Room (RFC 9421 / Web Bot Auth).

Writes worker/.signing.key (raw private key, base64url, gitignored) and prints the
public JWK to paste into the Worker source.
"""
import base64
import json
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

OUT = Path(__file__).resolve().parent.parent / "worker" / ".signing.key"


def b64u(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).decode().rstrip("=")


def main():
    if OUT.exists():
        raw = base64.urlsafe_b64decode(OUT.read_text().strip() + "==")
        priv = Ed25519PrivateKey.from_private_bytes(raw)
    else:
        priv = Ed25519PrivateKey.generate()
        raw = priv.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption(),
        )
        OUT.write_text(b64u(raw))
        print("wrote", OUT)
    pub = priv.public_key().public_bytes(
        encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw
    )
    print("PUBLIC_KEY_X=" + b64u(pub))
    print("KID=" + b64u(pub))


if __name__ == "__main__":
    main()
