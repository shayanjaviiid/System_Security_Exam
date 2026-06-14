"""
Step 2: Sender
Project: Fake Data Prevention with Digital Signatures

This script simulates a device that needs to send some data so the
receiver can be SURE it is genuine and was not modified.

We use ONE security tool: a DIGITAL SIGNATURE.
  - We sign the data with our RSA PRIVATE KEY.
  - Only we have the private key, so only we can produce a valid signature.

The message is sent in PLAIN TEXT together with its signature. We are
not hiding the data (no encryption); we only want to prove it is
authentic and untampered.
"""

import json
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding


def main():
    print("=" * 60)
    print(" STEP 2: SENDER - SIGNING THE DATA ")
    print("=" * 60)

    # ---------------------------------------------------------------
    # 1. Build the data we want to send
    # ---------------------------------------------------------------
    print("\n[1/4] Creating the original data (a simple JSON message)...")
    data = {
        "sensor": "temperature",
        "value": 25,
        "unit": "Celsius",
        "device_id": "iot-device-001",
    }
    message = json.dumps(data, indent=2)
    print("      Data to send:")
    print(f"      {data}")

    # ---------------------------------------------------------------
    # 2. Load the RSA private key from Step 1
    # ---------------------------------------------------------------
    print("\n[2/4] Loading our RSA PRIVATE KEY from private_key.pem...")
    print("      Only WE have this key, so only WE can produce a valid signature.")
    with open("private_key.pem", "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)
    print("      Private key loaded successfully.")

    # ---------------------------------------------------------------
    # 3. Sign the data
    # ---------------------------------------------------------------
    print("\n[3/4] Signing the message (RSA + SHA-256)...")
    print("      The signature is computed from the EXACT message bytes.")
    print("      If anyone changes even one character of the data, the")
    print("      signature will no longer match -> tampering detected.")
    signature = private_key.sign(
        message.encode("utf-8"),
        padding.PKCS1v15(),
        hashes.SHA256(),
    )
    print("      Signature created.")
    print(f"      Signature (hex, first 60 chars): {signature.hex()[:60]}...")

    # ---------------------------------------------------------------
    # 4. Save the message and the signature
    # ---------------------------------------------------------------
    print("\n[4/4] Saving files for the receiver...")
    with open("data.json", "w", encoding="utf-8") as f:
        f.write(message)
    print("      -> data.json       (the message, in plain text)")

    with open("signature.bin", "wb") as f:
        f.write(signature)
    print("      -> signature.bin   (the digital signature of the message)")

    # ---------------------------------------------------------------
    # Done
    # ---------------------------------------------------------------
    print("\n" + "=" * 60)
    print(" SENDER FINISHED ")
    print("=" * 60)
    print(" The message has been SIGNED -> proves authenticity (no fake data).")
    print(" Ready to be transmitted to the receiver.")


if __name__ == "__main__":
    main()
