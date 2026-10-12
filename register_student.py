import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

from database import initialize_database
from services.student_service import register_student


def main():
    initialize_database()

    root = tk.Tk()
    root.title("Register Student")
    root.geometry("460x390")
    root.resizable(False, False)
    root.configure(bg="white")

    tk.Label(
        root,
        text="Register Student",
        font=("Segoe UI", 20, "bold"),
        bg="white",
        fg="#172554"
    ).pack(pady=(20, 14))

    form = tk.Frame(root, bg="white", padx=28)
    form.pack(fill="x")

    entries = {}

    for label_text, key in [
        ("Full name", "full_name"),
        ("Student number", "student_number"),
        ("Class / Course", "class_name"),
    ]:
        tk.Label(
            form,
            text=label_text,
            bg="white",
            anchor="w"
        ).pack(fill="x", pady=(5, 2))

        entry = ttk.Entry(form)
        entry.pack(fill="x", ipady=5)
        entries[key] = entry

    def submit():
        try:
            full_name = entries["full_name"].get()
            student_id, qr_path = register_student(
                full_name,
                entries["student_number"].get(),
                entries["class_name"].get(),
            )

            qr_image = Image.open(qr_path)
            qr_image.thumbnail((220, 280))

            popup = tk.Toplevel(root)
            popup.title("Student QR Code")
            popup.configure(bg="white")

            tk.Label(
                popup,
                text=f"{full_name} (internal ID: {student_id})",
                bg="white",
                font=("Segoe UI", 11, "bold")
            ).pack(pady=10)

            photo = ImageTk.PhotoImage(qr_image)

            image_label = tk.Label(popup, image=photo, bg="white")
            image_label.image = photo
            image_label.pack(padx=20, pady=8)

            tk.Label(
                popup,
                text=f"Saved to: {qr_path}",
                bg="white",
                wraplength=350
            ).pack(padx=12, pady=(0, 12))

            messagebox.showinfo(
                "Success",
                "Student registered and QR code generated."
            )

            for entry in entries.values():
                entry.delete(0, tk.END)

        except Exception as exc:
            messagebox.showerror("Registration Error", str(exc))

    ttk.Button(
        root,
        text="Register Student & Generate QR",
        command=submit
    ).pack(pady=20)

    root.mainloop()


if __name__ == "__main__":
    main()