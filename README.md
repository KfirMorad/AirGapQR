AirGapQR is a file transfer system designed for high-security environments. It encrypts and slices any file into QR codes, allowing secure transmission between air-gapped systems — no network, no USB, no risk.

Features

AES-256 Encryption (Fernet standard)
File compression and chunking
QR code generation for each chunk
Camera-based scanning and reconstruction
SHA-256 integrity check
Full GUI (optional) or CLI mode
How It Works

Sender Workflow:

Select a file to send.
Encrypt with a password (AES-256).
Compress and split into base64 chunks.
Generate QR codes from chunks.
Display one-by-one or export as slideshow.
Receiver Workflow:

Scan QR codes with webcam.
Reconstruct and decrypt data.
Verify SHA-256 hash.
Save the original file.
Use Case

Air-gapped intelligence systems
Secure zones with no trusted I/O hardware
Covert or emergency data transmission
Demonstrations of secure physical-layer transfer
