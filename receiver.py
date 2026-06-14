"""
Step 4: Receiver
Project: Fake Data Prevention with Digital Signatures

This script simulates the server that receives the message. It must
check that the data is genuine before trusting it.

  Sender did:    sign the data with the PRIVATE key.
  Receiver does: verify the signature with the PUBLIC key.

If the signature check passes, the data is authentic and untampered.
If it fails, the data is FAKE or TAMPERED and we must reject it.
"""

import json
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature


def main():
    print("=" * 60)
    print(" STEP 4: RECEIVER - VERIFYING THE DATA ")
    print("=" * 60)

    # ---------------------------------------------------------------
    # 1. Load the incoming message and its signature
    # ---------------------------------------------------------------
    print("\n[1/3] Loading the incoming files...")
    with open("data.json", "r", encoding="utf-8") as f:
        message = f.read()
    print("      -> data.json loaded (the message, in plain text)")

    with open("signature.bin", "rb") as f:
        signature = f.read()
    print("      -> signature.bin loaded (the digital signature)")

    # ---------------------------------------------------------------
    # 2. Load the sender's public key
    # ---------------------------------------------------------------
    print("\n[2/3] Loading the sender's PUBLIC KEY from public_key.pem...")
    print("      The public key can ONLY verify signatures; it cannot create")
    print("      them. So if verification passes, we know the holder of the")
    print("      matching PRIVATE key signed this exact message.")
    with open("public_key.pem", "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())
    print("      Public key loaded successfully.")

    # ---------------------------------------------------------------
    # 3. Verify the signature against the message
    # ---------------------------------------------------------------
    print("\n[3/3] Verifying the signature (RSA + SHA-256)...")
    try:
        public_key.verify(
            signature,
            message.encode("utf-8"),
            padding.PKCS1v15(),
            hashes.SHA256(),
        )
    except InvalidSignature:
        print("\n" + "!" * 60)
        print(" SECURITY WARNING: INVALID SIGNATURE ")
        print(" The message does NOT match its signature.")
        print(" This means the data is FAKE or has been TAMPERED with.")
        print(" The message will be REJECTED.")
        print("!" * 60)
        return

    # ---------------------------------------------------------------
    # Success
    # ---------------------------------------------------------------
    print("      Signature is VALID.")
    print("\n" + "=" * 60)
    print(" MESSAGE ACCEPTED ")
    print("=" * 60)
    print(" The data is authentic and untampered.")
    print(" Original data received:")
    original_data = json.loads(message)
    for key, value in original_data.items():
        print(f"   {key}: {value}")


if __name__ == "__main__":
    main()
