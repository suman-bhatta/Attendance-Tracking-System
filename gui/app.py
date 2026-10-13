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
        self.video_label.configure(text="Starting camera...")
        self.start_button.configure(state="disabled")
        self.status_label.configure(text="Starting camera...")
        self.scan_details_label.configure(text="Opening the webcam automatically...")
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.after(100, self.start_camera)

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

        right = tk.Frame(body, bg="white", padx=18, pady=18, width=290)
        right.pack(side="right", fill="y", padx=(16, 0))
        right.pack_propagate(False)

        tk.Label(
            right,
            text="Attendance",
            bg="white",
            fg="#172554",
            font=("Segoe UI", 16, "bold")
        ).pack(anchor="w")

        self.status_label = tk.Label(
            right,
            text="Camera stopped",
            bg="#eff6ff",
            fg="#1d4ed8",
            font=("Segoe UI", 12, "bold"),
            justify="left",
            anchor="w",
            padx=12,
            pady=12,
            wraplength=240
        )
        self.status_label.pack(fill="x", pady=(12, 18))

        tk.Label(
            right,
            text="LATEST SCAN",
            bg="white",
            fg="#64748b",
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w")
        self.scan_details_label = tk.Label(
            right,
            text="Start the camera, then hold a registered student's QR code in view.",
            bg="#f8fafc",
            fg="#334155",
            font=("Segoe UI", 10),
            justify="left",
            anchor="nw",
            padx=12,
            pady=12,
            wraplength=240
        )
        self.scan_details_label.pack(fill="x", pady=(6, 18))

        tk.Label(
            right,
            text="TO RECORD ATTENDANCE\n\n1. Register the student and open their QR image.\n\n2. Start the camera.\n\n3. Hold the QR code steady in front of the camera.\n\n4. Wait for the result to appear above.",
            bg="white",
            fg="#374151",
            font=("Segoe UI", 10),
            justify="left",
            wraplength=245
        ).pack(anchor="w")

        footer = tk.Label(
            self, text="Attendance records are stored locally in data/attendance.db",
            bg="#f3f5f9", fg="#6b7280", font=("Segoe UI", 9)
        )
        footer.pack(pady=(0, 12))

    def start_camera(self):
        if self.camera_running:
            return

        camera_backends = (cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY)
        for camera_index in range(3):
            for backend in camera_backends:
                camera = cv2.VideoCapture(camera_index, backend)
                if camera.isOpened():
                    self.camera = camera
                    break
                camera.release()
            if self.camera is not None:
                break

        if self.camera is None:
            self.video_label.configure(text="Camera is stopped")
            self.start_button.configure(state="normal")
            self.status_label.configure(
                text="Camera stopped",
                bg="#eff6ff",
                fg="#1d4ed8"
            )
            self.scan_details_label.configure(
                text="Camera could not be opened. Check the connection and permissions, then try again."
            )
            messagebox.showerror(
                "Camera Error",
                "Unable to open a webcam. Check Windows camera permissions, "
                "close other apps using the camera, and make sure it is connected.",
            )
            return

        self.camera_running = True
        self.last_processed_payload = None
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.status_label.configure(
            text="Camera active - Ready to scan",
            bg="#eff6ff",
            fg="#1d4ed8"
        )
        self.scan_details_label.configure(
            text="Hold a registered student's QR code in view. The latest result will appear here."
        )
        self._update_frame()

    def _update_frame(self):
        if not self.camera_running or self.camera is None:
            return

        ok, frame = self.camera.read()
        if not ok:
            self.status_label.configure(
                text="Camera active - No video",
                bg="#fef2f2",
                fg="#b91c1c"
            )
            self.scan_details_label.configure(
                text="Could not read from the camera. Check that it is connected and not in use by another app."
            )
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
                student = result["student"]
                self.status_label.configure(
                    text="Attendance recorded",
                    bg="#dcfce7",
                    fg="#166534"
                )
                self.scan_details_label.configure(
                    text=(
                        f"Student: {student['full_name']}\n"
                        f"Student No: {student['student_number']}\n"
                        f"Class: {student['class_name']}\n\n"
                        "Attendance photo saved."
                    )
                )
            else:
                self.status_label.configure(
                    text="Attendance not recorded",
                    bg="#fef2f2",
                    fg="#b91c1c"
                )
                self.scan_details_label.configure(text=result["message"])

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
        self.status_label.configure(
            text="Camera stopped",
            bg="#eff6ff",
            fg="#1d4ed8"
        )
        self.scan_details_label.configure(
            text="Start the camera, then hold a registered student's QR code in view."
        )

    def _on_close(self):
        self.stop_camera()
        self.destroy()
