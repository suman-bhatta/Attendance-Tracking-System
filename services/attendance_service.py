from datetime import datetime
from pathlib import Path
from database import get_connection

ROOT_DIR = Path(__file__).resolve().parents[1]
CAPTURE_DIR = ROOT_DIR / "captures"


def mark_attendance(qr_payload: str, frame):
    """Validate a student QR payload and save today's attendance photo."""
    if not qr_payload.startswith("STUDENT:"):
        return {"ok": False, "message": "This QR code is not a student attendance code."}

    try:
        student_id = int(qr_payload.split(":", 1)[1])
    except (TypeError, ValueError):
        return {"ok": False, "message": "Invalid student QR code."}

    now = datetime.now()
    with get_connection() as connection:
        student = connection.execute(
            "SELECT id, full_name, student_number, class_name FROM students WHERE id = ?",
            (student_id,),
        ).fetchone()

        if student is None:
            return {"ok": False, "message": "Student not found. Please register the student first."}

        existing = connection.execute(
            "SELECT id FROM attendance WHERE student_id = ? AND attendance_date = ?",
            (student_id, now.date().isoformat()),
        ).fetchone()

        if existing:
            return {
                "ok": False,
                "message": f"Attendance already marked today for {student['full_name']}.",
            }

        CAPTURE_DIR.mkdir(parents=True, exist_ok=True)
        image_path = CAPTURE_DIR / f"student_{student_id}_{now:%Y%m%d_%H%M%S}.jpg"
        if frame is None:
            return {"ok": False, "message": "Could not capture the student's image."}

        import cv2
        if not cv2.imwrite(str(image_path), frame):
            return {"ok": False, "message": "Could not save the captured image."}

        connection.execute(
            """INSERT INTO attendance
               (student_id, attendance_date, attendance_time, image_path)
               VALUES (?, ?, ?, ?)""",
            (student_id, now.date().isoformat(), now.strftime("%H:%M:%S"), str(image_path)),
        )

    return {
        "ok": True,
        "message": f"Attendance marked successfully!\n\n"
                   f"Student: {student['full_name']}\n"
                   f"Student ID: {student['student_number']}\n"
                   f"Class: {student['class_name']}\n"
                   f"Time: {now:%H:%M:%S}",
        "student": dict(student),
        "image_path": str(image_path),
    }
