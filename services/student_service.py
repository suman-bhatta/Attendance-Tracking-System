import re
from pathlib import Path

import qrcode
from PIL import Image, ImageDraw, ImageFont

from database import get_connection

ROOT_DIR = Path(__file__).resolve().parents[1]
QR_DIR = ROOT_DIR / "qrcodes"


def _make_labeled_qr(payload: str, name: str) -> Image.Image:
    qr_image = qrcode.make(payload).convert("RGB")
    font_size = 20
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except OSError:
        font = ImageFont.load_default()

    draw = ImageDraw.Draw(qr_image)
    max_width = qr_image.width - 24
    words = name.split()
    lines = []
    line = ""

    for word in words:
        candidate = f"{line} {word}".strip()
        if line and draw.textbbox((0, 0), candidate, font=font)[2] > max_width:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)

    line_height = draw.textbbox((0, 0), "Ag", font=font)[3] + 4
    padding = 12
    labeled_image = Image.new(
        "RGB",
        (qr_image.width, qr_image.height + padding * 2 + line_height * len(lines)),
        "white",
    )
    labeled_image.paste(qr_image, (0, 0))
    draw = ImageDraw.Draw(labeled_image)
    y = qr_image.height + padding
    for line in lines:
        bounds = draw.textbbox((0, 0), line, font=font)
        x = (qr_image.width - (bounds[2] - bounds[0])) // 2
        draw.text((x, y), line, fill="black", font=font)
        y += line_height

    return labeled_image


def register_student(full_name: str, student_number: str, class_name: str):
    full_name = full_name.strip()
    student_number = student_number.strip()
    class_name = class_name.strip()

    if not full_name or not student_number or not class_name:
        raise ValueError("Full name, student number, and class are required.")

    first_name = full_name.split(maxsplit=1)[0].lower()
    filename_parts = [
        re.sub(r'[<>:"/\\|?*\s]+', "_", value).strip("._")
        for value in (first_name, student_number)
    ]
    if not all(filename_parts):
        raise ValueError("The student's name and number must contain filename-safe characters.")

    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO students (full_name, student_number, class_name) VALUES (?, ?, ?)",
            (full_name, student_number, class_name),
        )
        student_id = cursor.lastrowid

    QR_DIR.mkdir(parents=True, exist_ok=True)
    qr_path = QR_DIR / f"{filename_parts[0]}_{filename_parts[1]}.png"
    _make_labeled_qr(f"STUDENT:{student_id}", full_name).save(qr_path)
    return student_id, qr_path
