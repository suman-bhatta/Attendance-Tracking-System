import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import cv2

from database import initialize_database
from services.attendance_service import mark_attendance


class AttendanceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        initialize_database()

        self.title("Student Attendance Tracking System")
        self.geometry("1050x700")
        self.minsize(850, 600)
        self.configure(bg="#f3f5f9")

        self.camera = None
        self.camera_running = False
        self.qr_detector = cv2.QRCodeDetector()
        self.last_processed_payload = None
        self.video_image = None

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        header = tk.Frame(self, bg="#172554", padx=24, pady=18)
        header.pack(fill="x")
        tk.Label(
            header, text="Attendance Tracking System",
            bg="#172554", fg="white", font=("Segoe UI", 22, "bold")
        ).pack(anchor="w")
        tk.Label(
            header, text="Scan a registered student's QR code to record attendance",
            bg="#172554", fg="#dbeafe", font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(4, 0))

        body = tk.Frame(self, bg="#f3f5f9", padx=20, pady=20)
        body.pack(fill="both", expand=True)

        left = tk.Frame(body, bg="white", padx=14, pady=14)
        left.pack(side="left", fill="both", expand=True)

        self.video_label = tk.Label(
            left, text="Camera is stopped", bg="#111827", fg="white",
            font=("Segoe UI", 14), width=70, height=25
        )
        self.video_label.pack(fill="both", expand=True)

        controls = tk.Frame(left, bg="white")
        controls.pack(fill="x", pady=(12, 0))
        self.start_button = ttk.Button(controls, text="Start Camera", command=self.start_camera)
        self.start_button.pack(side="left")
        self.stop_button = ttk.Button(controls, text="Stop Camera", command=self.stop_camera, state="disabled")
        self.stop_button.pack(side="left", padx=(8, 0))

        right = tk.Frame(body, bg="white", padx=18, pady=18, width=270)
        right.pack(side="right", fill="y", padx=(16, 0))
        right.pack_propagate(False)

        tk.Label(right, text="Attendance Status", bg="white", fg="#172554",
                 font=("Segoe UI", 15, "bold")).pack(anchor="w")
        self.status_label = tk.Label(
            right, text="Ready to scan", bg="#eff6ff", fg="#1d4ed8",
            font=("Segoe UI", 11), justify="left", anchor="nw",
            padx=12, pady=12, wraplength=220
        )
        self.status_label.pack(fill="x", pady=(12, 16))

        tk.Label(
            right,
            text="How to use\n\n1. Register a student with register_student.py\n2. Open that student's QR code\n3. Start the camera\n4. Hold the QR code in view\n5. The system captures an image and records attendance",
            bg="white", fg="#374151", font=("Segoe UI", 10),
            justify="left", wraplength=225
        ).pack(anchor="w")

        footer = tk.Label(
            self, text="Attendance records are stored locally in data/attendance.db",
            bg="#f3f5f9", fg="#6b7280", font=("Segoe UI", 9)
        )
        footer.pack(pady=(0, 12))

    def start_camera(self):
        if self.camera_running:
            return
        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():
            self.camera.release()
            self.camera = None
            messagebox.showerror("Camera Error", "Unable to open the webcam. Check camera permissions.")
            return

        self.camera_running = True
        self.last_processed_payload = None
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.status_label.configure(text="Camera started. Show a student QR code.", bg="#eff6ff", fg="#1d4ed8")
        self._update_frame()

    def _update_frame(self):
        if not self.camera_running or self.camera is None:
            return

        ok, frame = self.camera.read()
        if not ok:
            self.status_label.configure(text="Could not read from camera.", bg="#fef2f2", fg="#b91c1c")
            self.after(100, self._update_frame)
            return

        frame = cv2.flip(frame, 1)
        payload, points, _ = self.qr_detector.detectAndDecode(frame)

        if points is not None:
            points = points.astype(int).reshape(-1, 2)
            for index in range(len(points)):
                cv2.line(frame, tuple(points[index]), tuple(points[(index + 1) % len(points)]), (0, 220, 80), 3)

        if payload and payload != self.last_processed_payload:
            self.last_processed_payload = payload
            result = mark_attendance(payload, frame.copy())
            if result["ok"]:
                self.status_label.configure(text=result["message"], bg="#dcfce7", fg="#166534")
                messagebox.showinfo("Attendance Successful", result["message"])
                # Require the QR code to leave and be presented again before processing it again.
            else:
                self.status_label.configure(text=result["message"], bg="#fef2f2", fg="#b91c1c")
                messagebox.showwarning("Attendance Not Marked", result["message"])

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame = cv2.resize(rgb_frame, (700, 480))
        image = Image.fromarray(rgb_frame)
        self.video_image = ImageTk.PhotoImage(image=image)
        self.video_label.configure(image=self.video_image, text="")
        self.after(15, self._update_frame)

    def stop_camera(self):
        self.camera_running = False
        if self.camera is not None:
            self.camera.release()
            self.camera = None
        self.video_label.configure(image="", text="Camera is stopped")
        self.video_image = None
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.status_label.configure(text="Camera stopped. Ready to scan.", bg="#eff6ff", fg="#1d4ed8")

    def _on_close(self):
        self.stop_camera()
        self.destroy()
