from hashlib import sha256
from binascii import unhexlify, hexlify
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

from pisa.logger import Logger

logger = Logger("Cryptographer")


# FIXME: Cryptographer is assuming AES-128-GCM and SHA256 since they are the only pair accepted by the encrypted blob
#   and the only pair programmed so far.
class Cryptographer:
    @staticmethod
    # ToDo: #20-test-tx-decrypting-edge-cases
    def decrypt(encrypted_blob, key, rtype="hex"):
        if rtype not in ["hex", "bytes"]:
            raise ValueError("Wrong return type. Return type must be 'hex' or 'bytes'")

        if len(encrypted_blob.data) % 2:
            logger.info(
                "Incorrect (Odd-length) value to be decrypted.", encrypted_blob=encrypted_blob.data, dispute_txid=key
            )
            return None

        # sk is the H(txid) (32-byte) and nonce is set to 0 (12-byte)
        sk = sha256(unhexlify(key)).digest()
        nonce = bytearray(12)

        logger.info(
            "Creating new blob.",
            sk=hexlify(sk).decode(),
            nonce=hexlify(nonce).decode(),
            encrypted_blob=encrypted_blob.data,
        )

        # Decrypt
        cipher = ChaCha20Poly1305(sk)
        data = unhexlify(encrypted_blob.data.encode())

        try:
            blob = cipher.decrypt(nonce=nonce, data=data, associated_data=None)

            # Change the blob encoding to hex depending on the rtype (default)
            if rtype == "hex":
                blob = hexlify(blob).decode("utf8")

        except InvalidTag:
            blob = None

        return blob
