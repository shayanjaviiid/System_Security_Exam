"""
Step 3: Hacker (Man-in-the-Middle Attack Simulation)
Project: Fake Data Prevention with Digital Signatures

This script plays the role of an attacker who has intercepted the
message on the network. The data travels in PLAIN TEXT, so the attacker
CAN read and edit it. Their GOAL is to change the temperature reading to
a fake value (999) and have the receiver accept it as genuine.

There is only ONE thing the attacker can try: change the data.
They do NOT have the sender's private key, so they cannot produce a
matching signature for the changed data. When the receiver verifies the
signature, the attack is caught and the message is REJECTED.
"""

import json


def main():
    print("=" * 60)
    print(" STEP 3: HACKER - MAN-IN-THE-MIDDLE ATTACK ")
    print("=" * 60)
    print(" The attacker wants to change the temperature reading to 999.")
    print(" To succeed, they would need the SENDER'S PRIVATE KEY to make a")
    print(" new matching signature. They do NOT have it, so the attack fails.")

    print("\n>>> ATTACK: change the data, leave the old signature in place")
    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"    Original data: {data}")

    data["value"] = 999
    print(f"    Forged data  : {data}")

    # The attacker writes the changed message back. They CANNOT update
    # signature.bin to match, because signing needs the private key.
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("    Tampered data.json written back.")
    print("    The signature (signature.bin) was NOT updated (the attacker can't).")
    print("    EXPECTED RESULT in receiver: invalid signature -> REJECTED.")

    print("\n" + "=" * 60)
    print(" HACKER FINISHED - data.json has been tampered with ")
    print("=" * 60)
    print(" Now run:  python receiver.py")
    print(" The receiver should DETECT the tampering and REJECT the data.")


if __name__ == "__main__":
    main()
