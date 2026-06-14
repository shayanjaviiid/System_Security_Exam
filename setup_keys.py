"""
Step 1: Key Setup
Project: Fake Data Prevention with Digital Signatures

This script generates the RSA key pair used to sign and verify data.
  - private_key.pem : SECRET, used to SIGN data.
  - public_key.pem  : SHARED, used to VERIFY signatures.
"""

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


def main():
    print("=" * 60)
    print(" STEP 1: GENERATING THE RSA KEY PAIR ")
    print("=" * 60)

    # ---------------------------------------------------------------
    # 1. Generate the RSA private key
    # ---------------------------------------------------------------
    print("\n[1/3] Generating a 2048-bit RSA PRIVATE KEY...")
    print("      The private key is SECRET. It is used to SIGN data.")
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    print("      Private key generated successfully.")

    # ---------------------------------------------------------------
    # 2. Derive the public key
    # ---------------------------------------------------------------
    print("\n[2/3] Extracting the matching RSA PUBLIC KEY...")
    print("      The public key is SHARED. It is used to VERIFY signatures.")
    public_key = private_key.public_key()
    print("      Public key extracted successfully.")

    # ---------------------------------------------------------------
    # 3. Save both keys to PEM files
    # ---------------------------------------------------------------
    print("\n[3/3] Saving keys to PEM files...")

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    with open("private_key.pem", "wb") as f:
        f.write(private_pem)
    print("      -> private_key.pem  (KEEP THIS SECRET)")

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    with open("public_key.pem", "wb") as f:
        f.write(public_pem)
    print("      -> public_key.pem   (safe to share)")

    # ---------------------------------------------------------------
    # Done
    # ---------------------------------------------------------------
    print("\n" + "=" * 60)
    print(" SETUP COMPLETE ")
    print("=" * 60)
    print(" Files created in the current folder:")
    print("   - private_key.pem   (used to SIGN data)")
    print("   - public_key.pem    (used to VERIFY signatures)")
    print("\n Next step: run sender.py to sign some data.")


if __name__ == "__main__":
    main()
