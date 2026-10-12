# Attendance Tracking System

A modular Python desktop application for student attendance using a webcam, QR codes, Tkinter, OpenCV, and SQLite.

## Features

- Desktop GUI built with Tkinter
- Live webcam preview
- QR code detection with OpenCV
- Automatic camera startup and face presence detection during QR attendance scans
- On-screen attendance confirmation and success sound
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

The attendance camera starts automatically. Show the student's face and generated QR code together in the camera view. A successful scan outlines the detected face and QR code in green, captures a photo, records attendance, and displays a confirmation with a sound. QR images are saved under `qrcodes/`, captured images under `captures/`, and the database under `data/`.

## Important security note

The attendance scanner checks that a face is visible while a student's QR code is scanned, but it does **not** match that face to the registered student. A photo is evidence of a scan, not proof of identity. If face verification is required, add a face-matching component, consent and retention controls, and anti-spoofing protections before using it in a real school.