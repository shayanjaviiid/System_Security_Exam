"""
core.py
Project: Fake Data Prevention with Digital Signatures

This module holds the whole crypto pipeline as plain Python functions
that return structured data. The same functions are used by:

  * the four CLI scripts (setup_keys.py, sender.py, hacker.py, receiver.py)
  * the small Flask web demo (app.py)

The idea is intentionally SIMPLE so it is easy to explain in an exam:

  1. setup   -> create an RSA private + public key pair.
  2. sender  -> sign the data with the PRIVATE key. Send the data AND
                the signature (both in plain text).
  3. hacker  -> change the data. They do NOT have the private key, so
                they cannot produce a matching signature.
  4. receiver-> verify the signature with the PUBLIC key. If the data
                was changed, the signature no longer matches -> REJECTED.

Only ONE security tool is used: the RSA digital signature.
"""

import json
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.exceptions import InvalidSignature


PROJECT_DIR = Path(__file__).resolve().parent
PRIVATE_KEY_PATH = PROJECT_DIR / "private_key.pem"
PUBLIC_KEY_PATH = PROJECT_DIR / "public_key.pem"
DATA_PATH = PROJECT_DIR / "data.json"          # the message, in plain text
SIGNATURE_PATH = PROJECT_DIR / "signature.bin"  # the signature of that message


# ---------------------------------------------------------------------
# Step 1: generate the RSA key pair.
# ---------------------------------------------------------------------
def setup_keys():
    logs = []

    logs.append(("info", "Generating a fresh 2048-bit RSA private key."))
    logs.append(("note", "The private key is SECRET. It is used to SIGN data."))
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    logs.append(("ok", "Private key generated."))

    logs.append(("info", "Extracting the matching RSA public key."))
    logs.append(("note", "The public key is SHARED. It is used to VERIFY signatures."))
    public_key = private_key.public_key()
    logs.append(("ok", "Public key extracted."))

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    PRIVATE_KEY_PATH.write_bytes(private_pem)
    logs.append(("ok", f"Saved {PRIVATE_KEY_PATH.name} (keep secret)."))

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    PUBLIC_KEY_PATH.write_bytes(public_pem)
    logs.append(("ok", f"Saved {PUBLIC_KEY_PATH.name} (safe to share)."))

    return {
        "logs": logs,
        "private_pem_preview": _preview(private_pem.decode()),
        "public_pem": public_pem.decode(),
    }


# ---------------------------------------------------------------------
# Step 2: sender side — build data, sign it with the private key.
# ---------------------------------------------------------------------
def run_sender(data=None):
    logs = []
    if data is None:
        data = {
            "sensor": "temperature",
            "value": 25,
            "unit": "Celsius",
            "device_id": "iot-device-001",
        }

    logs.append(("info", "Building the original JSON message."))
    message = json.dumps(data, indent=2)
    logs.append(("data", message))

    logs.append(("info", "Loading our RSA private key from private_key.pem."))
    if not PRIVATE_KEY_PATH.exists():
        raise FileNotFoundError(
            "private_key.pem not found. Run Step 1 (setup_keys) first."
        )
    private_key = serialization.load_pem_private_key(
        PRIVATE_KEY_PATH.read_bytes(), password=None
    )
    logs.append(("ok", "Private key loaded."))

    logs.append(("info", "Signing the message with the private key (RSA + SHA-256)."))
    logs.append(("note",
                 "The signature is computed from the EXACT message bytes. "
                 "If anyone changes even one character of the data later, the "
                 "signature will no longer match -> tampering detected."))
    signature = private_key.sign(
        message.encode("utf-8"),
        padding.PKCS1v15(),
        hashes.SHA256(),
    )
    logs.append(("ok", "Signature created."))
    logs.append(("data", signature.hex()))

    # The message is sent in PLAIN TEXT. We are not hiding it (no encryption);
    # we only want to prove it is authentic and unmodified.
    DATA_PATH.write_text(message, encoding="utf-8")
    SIGNATURE_PATH.write_bytes(signature)
    logs.append(("ok", f"Wrote {DATA_PATH.name} and {SIGNATURE_PATH.name}."))

    return {
        "logs": logs,
        "payload": data,
        "message": message,
        "signature_hex": signature.hex(),
    }


# ---------------------------------------------------------------------
# Step 3: hacker side — the only possible attack: change the data.
# ---------------------------------------------------------------------
def run_hacker():
    logs = []
    logs.append(("warn", "ATTACK: the attacker intercepts the message and changes the value to 999."))
    logs.append(("note",
                 "The data travels in plain text, so the attacker CAN read and "
                 "edit it. But the signature was made with the sender's PRIVATE "
                 "key, which the attacker does NOT have."))

    if not DATA_PATH.exists():
        raise FileNotFoundError("data.json not found. Run Step 2 (sender) first.")

    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    logs.append(("info", f"Original data: {json.dumps(data)}"))
    data["value"] = 999
    logs.append(("warn", f"Forged data : {json.dumps(data)}"))

    # The attacker writes the changed message back. They CANNOT update the
    # signature to match, because signing needs the private key. They leave
    # the old signature in place and hope the receiver does not notice.
    DATA_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    logs.append(("warn", "Tampered data.json written back. The signature was NOT updated (the attacker can't)."))
    logs.append(("note",
                 "Expected at receiver: the signature no longer matches the "
                 "changed data -> InvalidSignature -> message REJECTED."))

    return {"logs": logs}


# ---------------------------------------------------------------------
# Step 4: receiver side — verify the signature, accept or reject.
# ---------------------------------------------------------------------
def run_receiver():
    logs = []
    logs.append(("info", "Loading the incoming message and its signature."))
    if not DATA_PATH.exists() or not SIGNATURE_PATH.exists():
        raise FileNotFoundError("data.json / signature.bin not found. Run the sender first.")

    message = DATA_PATH.read_text(encoding="utf-8")
    signature = SIGNATURE_PATH.read_bytes()
    logs.append(("ok", "Loaded data.json and signature.bin."))
    logs.append(("data", message))

    logs.append(("info", "Loading the sender's public key from public_key.pem."))
    public_key = serialization.load_pem_public_key(PUBLIC_KEY_PATH.read_bytes())
    logs.append(("ok", "Public key loaded."))

    logs.append(("info", "Verifying the signature against the message (RSA + SHA-256)."))
    try:
        public_key.verify(
            signature,
            message.encode("utf-8"),
            padding.PKCS1v15(),
            hashes.SHA256(),
        )
    except InvalidSignature:
        logs.append(("fail", "INVALID SIGNATURE — the message does not match its signature."))
        logs.append(("fail", "The data is FAKE or has been TAMPERED with."))
        logs.append(("fail", "Message REJECTED."))
        return {"logs": logs, "status": "rejected", "reason": "bad_signature"}

    original_data = json.loads(message)
    logs.append(("ok", "Signature is VALID."))
    logs.append(("ok", "Message ACCEPTED."))
    logs.append(("data", json.dumps(original_data, indent=2)))
    return {"logs": logs, "status": "accepted", "data": original_data}


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def _preview(text, head=2, tail=1):
    """Return the first few lines + a hint, so we don't leak a full private key."""
    lines = text.strip().splitlines()
    if len(lines) <= head + tail + 1:
        return text
    return "\n".join(lines[:head] + ["    ... (private body hidden) ..."] + lines[-tail:])


def project_state():
    """Tell the UI which files currently exist on disk."""
    return {
        "private_key": PRIVATE_KEY_PATH.exists(),
        "public_key": PUBLIC_KEY_PATH.exists(),
        "data": DATA_PATH.exists(),
        "signature": SIGNATURE_PATH.exists(),
    }


def reset():
    """Delete all generated artifacts so the demo can be re-run from scratch."""
    removed = []
    for p in [DATA_PATH, SIGNATURE_PATH, PRIVATE_KEY_PATH, PUBLIC_KEY_PATH]:
        if p.exists():
            p.unlink()
            removed.append(p.name)
    return {"removed": removed}
