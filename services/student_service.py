import qrcode
from pathlib import Path
from database import get_connection

ROOT_DIR = Path(__file__).resolve().parents[1]
QR_DIR = ROOT_DIR / "qrcodes"


def register_student(full_name: str, student_number: str, class_name: str):
    full_name = full_name.strip()
    student_number = student_number.strip()
    class_name = class_name.strip()

    if not full_name or not student_number or not class_name:
        raise ValueError("Full name, student number, and class are required.")

    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO students (full_name, student_number, class_name) VALUES (?, ?, ?)",
            (full_name, student_number, class_name),
        )
        student_id = cursor.lastrowid

    QR_DIR.mkdir(parents=True, exist_ok=True)
    qr_path = QR_DIR / f"student_{student_id}.png"
    qrcode.make(f"STUDENT:{student_id}").save(qr_path)
    return student_id, qr_path
