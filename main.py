from encryptor import encrypt_file, decrypt_file
from qr_encoder import encrypted_to_qr
from qr_scanner import scan_qr_chunks
import tkinter as tk
from tkinter import messagebox, filedialog
# main.py
import os
import sys

# Ensure the script runs from its own directory
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))


MAX_SIZE = 40 * 1024
app_state = {"file": None, "text": None}

# Resolve the safe base directory once so we can validate all file paths against it.
_BASE_DIR = os.path.realpath(os.getcwd())


def _safe_path(user_path: str) -> str:
    """Resolve *user_path* and raise ValueError if it escapes _BASE_DIR.

    This prevents path-traversal attacks where a crafted filename such as
    '../../etc/passwd' could reach files outside the working directory.
    """
    resolved = os.path.realpath(user_path)
    if not resolved.startswith(_BASE_DIR + os.sep) and resolved != _BASE_DIR:
        raise ValueError(f"Path '{user_path}' is outside the allowed directory.")
    return resolved


root = tk.Tk()
root.geometry("400x300")
root.title("QR Tool")


def show_encrypt_ui():
    clear_screen()
    tk.Button(root, text="Back", command=show_main_menu).place(x=10, rely=1.0, anchor="sw")
    tk.Label(root, text="\U0001f510 Encryption Mode").pack(pady=10)

    def choose_file():
        file_path = filedialog.askopenfilename()
        if file_path:
            # Validate the chosen path stays within the working directory.
            try:
                safe = _safe_path(file_path)
            except ValueError:
                messagebox.showerror("Error", "Selected file is outside the allowed directory.")
                return
            if os.path.getsize(safe) > MAX_SIZE:
                messagebox.showerror("Error", "File exceeds 40KB.")
            else:
                file_label.config(text=f"Selected: {os.path.basename(safe)}")
                app_state["file"] = safe
                app_state["text"] = None

    tk.Label(root, text="Choose a file (max 40KB) OR enter text:").pack()
    tk.Button(root, text="Upload File", command=choose_file).pack()

    file_label = tk.Label(root, text="No file selected.")
    file_label.pack()

    tk.Label(root, text="Or enter text:").pack()
    text_entry = tk.Text(root, height=5, width=40)
    text_entry.pack()

    tk.Label(root, text="Enter password:").pack()
    password_entry = tk.Entry(root, show="*")
    password_entry.pack()

    def start_encryption():
        text_data = text_entry.get("1.0", tk.END).strip()
        password = password_entry.get()
        file_path = app_state.get("file")

        # Check if password is missing
        if not password:
            messagebox.showerror("Error", "Please enter a password.")
            return

        # Check if both are filled OR both are empty
        if (file_path and text_data) or (not file_path and not text_data):
            messagebox.showerror("Error", "Please provide either a file OR text (not both).")
            return

        if file_path:
            try:
                # file_path was already validated in choose_file()
                encrypt_file(file_path, password)
                encrypted_to_qr("encrypted.bin")
                messagebox.showinfo("Success", "File encrypted and QR codes created.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to encrypt file: {e}")
        elif text_data:
            try:
                temp_path = _safe_path("temp_text.txt")
                # Save text to a temporary file
                with open(temp_path, "w") as temp_file:
                    temp_file.write(text_data)
                encrypt_file(temp_path, password)
                encrypted_to_qr("encrypted.bin")
                os.remove(temp_path)  # Clean up temporary file
                messagebox.showinfo("Success", "Text encrypted and QR codes created.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to encrypt text: {e}")

    tk.Button(root, text="Start Encryption", command=start_encryption).pack(pady=10)


def show_decrypt_ui():
    clear_screen()
    tk.Button(root, text="Back", command=show_main_menu).place(x=15, rely=0.9, anchor="sw")
    tk.Label(root, text="\U0001f513 Decrypt Mode").pack(pady=10)

    tk.Label(root, text="Enter password:").pack()
    decrypt_password_entry = tk.Entry(root, show="*")
    decrypt_password_entry.pack()

    def start_scanning():
        password = decrypt_password_entry.get()
        if not password:
            messagebox.showerror("Error", "Password is required.")
            return
        print("Ready to scan.")
        try:
            # scan_qr_chunks() validates every chunk before decoding;
            # decrypt_file() writes only to the fixed local path below.
            raw_bytes = scan_qr_chunks()
            output_path = _safe_path("decrypted.bin")
            decrypt_file(raw_bytes, password, output_path)
            messagebox.showinfo("Success", "QR code scanned and file decrypted.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to scan QR code: {e}")

    tk.Button(root, text="Start Scanning", command=start_scanning).pack(pady=10)


def clear_screen():
    for widget in root.winfo_children():
        widget.destroy()


def show_main_menu():
    clear_screen()
    tk.Label(root, text="What do you want to do?").pack(pady=10)
    tk.Button(root, text="Encrypt (create QR code)", command=show_encrypt_ui).pack(pady=5)
    tk.Button(root, text="Decrypt (scan QR code)", command=show_decrypt_ui).pack(pady=5)


show_main_menu()
root.mainloop()
