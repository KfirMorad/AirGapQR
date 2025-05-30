# AirGapQR — Secure Offline File Transfer via QR

**AirGapQR** is a file transfer system designed for high-security environments. It encrypts and slices any file into QR codes, allowing secure transmission between air-gapped systems — no network, no USB, no risk.

---

## Features

1. AES-256 Encryption using the Fernet standard  
2. File compression and chunking  
3. QR code generation for each chunk  
4. Camera-based scanning and file reconstruction  
5. SHA-256 integrity verification  
6. Supports both GUI (optional) and CLI mode  

---

## How It Works

### Sender Workflow:

1. Select a file to send  
2. Encrypt the file using a password (AES-256)  
3. Compress and split the file into base64-encoded chunks  
4. Generate a QR code for each chunk  
5. Display the QR codes one by one or export as a slideshow  

### Receiver Workflow:

1. Scan QR codes using a webcam  
2. Reconstruct and decrypt the data  
3. Verify the SHA-256 hash to ensure integrity  
4. Save the original file to disk  

---

## Use Case

1. Air-gapped intelligence systems  
2. Secure environments without trusted I/O hardware  
3. Covert or emergency data transfer scenarios  
4. Demonstrations or educational tools for physical-layer secure communication  
