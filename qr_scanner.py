import cv2
from pyzbar.pyzbar import decode
import base64
import re

# Maximum number of chunks to accept to prevent unbounded accumulation
MAX_CHUNKS = 1000
# Maximum length of a single base64-encoded chunk (e.g. 10 MB decoded ~ 13.4 MB base64)
MAX_CHUNK_LENGTH = 13_981_016
# Regex that matches valid base64 strings (standard and URL-safe alphabets, with optional padding)
BASE64_RE = re.compile(r'^[A-Za-z0-9+/\-_]+=*$')


def is_valid_base64_chunk(chunk: str) -> bool:
    """Return True only if *chunk* is a non-empty, well-formed base64 string."""
    if not chunk or not isinstance(chunk, str):
        return False
    if len(chunk) > MAX_CHUNK_LENGTH:
        return False
    # Length must be a multiple of 4 after stripping padding, or pyzbar data
    # may include padding already – let base64.b64decode validate length;
    # here we just check the character set.
    if not BASE64_RE.match(chunk):
        return False
    return True


def scan_qr_chunks():
    cap = cv2.VideoCapture(0)
    seen = set()
    chunks = []

    print("📷 Scanning... Press Q to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        decoded_objects = decode(frame)

        for obj in decoded_objects:
            data = obj.data.decode()
            if data not in seen:
                if not is_valid_base64_chunk(data):
                    print("⚠️  Skipping invalid/unexpected chunk – not valid base64.")
                    continue
                if len(chunks) >= MAX_CHUNKS:
                    print("⚠️  Maximum chunk limit reached; ignoring further chunks.")
                    continue
                print(f"🧩 New chunk captured ({len(chunks)})")
                seen.add(data)
                chunks.append(data)

        cv2.imshow("QR Scanner - Press Q to Stop", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    return chunks_to_bytes(chunks)


def chunks_to_bytes(chunks: list) -> bytes:
    binary_data = b""
    for chunk in chunks:
        # Validate again at decode time; ignore any chunk that slipped through
        if not is_valid_base64_chunk(chunk):
            print("⚠️  Skipping chunk with invalid base64 content during assembly.")
            continue
        try:
            # validate=True raises binascii.Error on non-base64 characters
            binary_data += base64.b64decode(chunk, validate=True)
        except Exception as exc:
            print(f"⚠️  Failed to decode chunk, skipping: {exc}")
    return binary_data
