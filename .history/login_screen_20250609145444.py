import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
import mysql.connector
from mysql.connector import Error
from hashlib import sha256
import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller bundle """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def login():
    username = username_entry.get().strip()
    password = password_entry.get()

    if not username or not password:
        return messagebox.showwarning("Input Error", "Please enter both username and password.")

    password_hash = sha256(password.encode()).hexdigest()

    try:
        # Connect to MySQL database
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="kinnporsche",
            database="helpdesk_db"
        )

        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, role FROM users WHERE username=%s AND password=%s",
            (username, password_hash)
        )
        user = cursor.fetchone()
        conn.close()

        if not user:
            return messagebox.showerror("Login Failed", "Invalid credentials.")

        user_id, role = user
        dashboard.destroy()

        # Load appropriate dashboard
        if role.lower() == "staff":
            import staff_dashboard
            staff_dashboard.StaffDashboard(user_id)
        elif role.lower() == "technician":
            import technician_dashboard
            technician_dashboard.TechnicianDashboard(user_id)
        elif role.lower() == "admin":
            import admin_dashboard
            admin_dashboard.AdminDashboard(user_id)
        else:
            messagebox.showerror("Login Failed", "Unknown user role.")

    except Error as e:
        messagebox.showerror("Database Error", f"Error connecting to MySQL:\n{e}")

# ---------- GUI Setup ----------
dashboard = tk.Tk()
dashboard.title("Helpdesk System Login")
dashboard.state('zoomed')  # Fullscreen

# Load and resize background image
bg_image_path = resource_path("assets/helpdesk_1.png")
bg_image = Image.open(bg_image_path)
screen_width = dashboard.winfo_screenwidth()
screen_height = dashboard.winfo_screenheight()
bg_image = bg_image.resize((screen_width, screen_height))
bg_photo = ImageTk.PhotoImage(bg_image)

# Create canvas and place background
canvas = tk.Canvas(dashboard, width=screen_width, height=screen_height)
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, image=bg_photo, anchor="nw")

# Overlay
canvas.create_rectangle(0, 0, screen_width, screen_height, fill="black", outline="", stipple="gray50")

# Login box
overlay_width = 600
overlay_height = 350
overlay_img = Image.new("RGBA", (overlay_width, overlay_height), (0, 0, 0, 200))
overlay_photo = ImageTk.PhotoImage(overlay_img)
canvas.create_image(screen_width // 2, screen_height // 2, image=overlay_photo, anchor="center")

# Logo
logo_image_path = resource_path("assets/1.png")
logo_image = Image.open(logo_image_path)
logo_image = logo_image.resize((100, 100))
logo_photo = ImageTk.PhotoImage(logo_image)
canvas.create_image(screen_width // 2 - 230, screen_height // 2 - 10, image=logo_photo, anchor="center")

# Title
canvas.create_text(screen_width // 2, screen_height // 2 - 300,
                   text="KENYA NATIONAL BUREAU OF STATISTICS HELPDESK",
                   font=("Sorts Mill Goudy", 26, "bold"), fill="white")

# Login Heading
canvas.create_text(screen_width // 2 + 20, screen_height // 2 - 130,
                   text="Login", font=("Sorts Mill Goudy", 24, "bold"), fill="white")

# Username Label & Entry
canvas.create_text(screen_width // 2 - 140, screen_height // 2 - 30,
                   text="Username : ", font=("Sorts Mill Goudy", 10, "bold"), fill="white")
username_entry = tk.Entry(dashboard, font=("Arial", 14))
canvas.create_window(screen_width // 2 + 30, screen_height // 2 - 30, window=username_entry, width=200)

# Password Label & Entry
canvas.create_text(screen_width // 2 - 140, screen_height // 2 + 20,
                   text="Password : ", font=("Sorts Mill Goudy", 10, "bold"), fill="white")
password_entry = tk.Entry(dashboard, show="*", font=("Arial", 15))
canvas.create_window(screen_width // 2 + 30, screen_height // 2 + 20, window=password_entry, width=200)

# Login Button
login_button = tk.Button(dashboard, text="Login", command=login, font=("Arial", 10))
canvas.create_window(screen_width // 2 + 30, screen_height // 2 + 90, window=login_button, width=120)

# Footer
canvas.create_text(screen_width // 2 + 600, screen_height // 2 + 350,
                   text="designed by dkn", font=("Sorts Mill Goudy", 10, "bold"), fill="white")

# Start the application
dashboard.mainloop()
