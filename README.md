# Attendance Tracking System

A modular Python desktop application for student attendance using a webcam, QR codes, Tkinter, OpenCV, and SQLite.

## Features

- Desktop GUI built with Tkinter
- Live webcam preview
- QR code detection with OpenCV
- Student registration and QR code generation
- Capture and save an attendance image
- SQLite attendance records with date/time
- Prevents a student from being marked present more than once per day

## Requirements

- Python 3.10 or newer
- A working webcam
- Tkinter (included with most standard Windows Python installations)

## Setup on Windows

```powershell
py -m venv .venv
.venv\\Scripts\\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run the app

First register students and generate their QR codes:

```powershell
python register_student.py
```

Then launch the attendance scanner:

```powershell
python main.py
```

The attendance scanner opens the webcam automatically when it starts. Show the generated QR code to the webcam; use **Stop Camera** if you need to pause it. A successful scan captures a photo and records attendance. QR images are saved under `qrcodes/`, captured images under `captures/`, and the database under `data/`.

## Important security note

This starter validates the QR code against the local student database and captures a photo, but it does **not** perform facial identity matching. A photo is evidence of a scan, not proof that the person in front of the camera is the registered student. If face verification is required, add a face-matching component, consent and retention controls, and anti-spoofing protections before using it in a real school.