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
_MIN_PASSWORD_LENGTH = 8
_MAX_PASSWORD_LENGTH = 1024
app_state = {"file": None, "text": None}


root = tk.Tk()
root.geometry("400x300")
root.title("QR Tool")


def _validate_password(password: str) -> str:
    """Return an error message string if the password is invalid, else empty string."""
    if not password:
        return "Please enter a password."
    if len(password) < _MIN_PASSWORD_LENGTH:
        return f"Password must be at least {_MIN_PASSWORD_LENGTH} characters."
    if len(password) > _MAX_PASSWORD_LENGTH:
        return "Password is too long."
    return ""


def show_encrypt_ui():
    clear_screen()
    tk.Button(root, text="Back", command=show_main_menu).place(x=10, rely=1.0, anchor="sw")
    tk.Label(root, text="🔐 Encryption Mode").pack(pady=10)

    def choose_file():
        file_path = filedialog.askopenfilename()
        if file_path:
            # Resolve the real path to prevent path-traversal tricks
            real_path = os.path.realpath(file_path)
            try:
                size = os.path.getsize(real_path)
            except OSError as e:
                messagebox.showerror("Error", f"Cannot read file: {e}")
                return
            if size > MAX_SIZE:
                messagebox.showerror("Error", "File exceeds 40KB.")
            elif size == 0:
                messagebox.showerror("Error", "File is empty.")
            else:
                file_label.config(text=f"Selected: {os.path.basename(real_path)}")
                app_state["file"] = real_path
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

        # Validate password
        pw_error = _validate_password(password)
        if pw_error:
            messagebox.showerror("Error", pw_error)
            return

        # Check if both are filled OR both are empty
        if (file_path and text_data) or (not file_path and not text_data):
            messagebox.showerror("Error", "Please provide either a file OR text (not both).")
            return

        # Validate text size if text path is chosen
        if text_data and len(text_data.encode("utf-8")) > MAX_SIZE:
            messagebox.showerror("Error", "Text exceeds 40KB.")
            return

        if file_path:
            try:
                encrypt_file(file_path, password)
                encrypted_to_qr("encrypted.bin")
                messagebox.showinfo("Success", "File encrypted and QR codes created.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to encrypt file: {e}")
        elif text_data:
            try:
                # Save text to a temporary file
                with open("temp_text.txt", "w", encoding="utf-8") as temp_file:
                    temp_file.write(text_data)
                encrypt_file("temp_text.txt", password)
                encrypted_to_qr("encrypted.bin")
                os.remove("temp_text.txt")  # Clean up temporary file
                messagebox.showinfo("Success", "Text encrypted and QR codes created.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to encrypt text: {e}")
    tk.Button(root, text="Start Encryption", command=start_encryption).pack(pady=10)


def show_decrypt_ui():
    clear_screen()
    tk.Button(root, text="Back", command=show_main_menu).place(x=15, rely=0.9, anchor="sw")
    tk.Label(root, text="🔓 Decrypt Mode").pack(pady=10)

    tk.Label(root, text="Enter password:").pack()
    decrypt_password_entry = tk.Entry(root, show="*")
    decrypt_password_entry.pack()

    def start_scanning():
        password = decrypt_password_entry.get()
        pw_error = _validate_password(password)
        if pw_error:
            messagebox.showerror("Error", pw_error)
            return
        try:
            decrypt_file(scan_qr_chunks(), password)
            messagebox.showinfo("Success", "QR code scanned")
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
