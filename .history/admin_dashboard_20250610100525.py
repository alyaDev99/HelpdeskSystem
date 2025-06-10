import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
from mysql.connector import Error
from datetime import datetime
from hashlib import sha256

class AdminDashboard:
    def __init__(self, user_id=None):
        self.user_id = user_id  # store for future use
        # MySQL connection settings
        self.db_config = {
            'host': 'localhost',
            'user': 'root',
                 font=("Segoe UI", 14, "bold")).pack(pady=20)
        ttk.Button(sidebar, text="👥 View Users", width=20, command=self.view_users).pack(pady=10)
        ttk.Button(sidebar, text="➕ Add User", width=20, command=self.add_user).pack(pady=10)
        ttk.Button(sidebar, text="🗑 Delete User", width=20, command=self.delete_user).pack(pady=10)
        ttk.Button(sidebar, text="📊 View Tickets", width=20, command=self.view_tickets).pack(pady=10)
        ttk.Button(sidebar, text="🚪 Logout", width=20, command=self.dashboard.destroy).pack(pady=20)

        # Main content area
        self.content_frame = tk.Frame(self.dashboard, bg="#f7f9fa")
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.show_welcome()
        self.dashboard.mainloop()

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_welcome(self):
        self.clear_content()
        tk.Label(self.content_frame, text="Welcome to the Admin Dashboard",
                 font=("Segoe UI", 18, "bold"), bg="#f7f9fa").pack(pady=50)

    def view_users(self):
        self.clear_content()
        tk.Label(self.content_frame, text="User List", font=("Segoe UI", 16, "bold"),
                 bg="#f7f9fa").pack(pady=20)

        columns = ("ID", "Username", "Role", "Department")
        tree = ttk.Treeview(self.content_frame, columns=columns, show="headings", height=15)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor="center")
        tree.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, role, department FROM users")
            for row in cursor.fetchall():
                tree.insert("", tk.END, values=row)
        except Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            conn.close()

    def add_user(self):
        self.clear_content()
        frame = tk.Frame(self.content_frame, bg="#f7f9fa")
        frame.pack(pady=20)

        tk.Label(frame, text="Username:", bg="#f7f9fa").pack(pady=5)
        username_entry = tk.Entry(frame, width=40)
        username_entry.pack(pady=5)

        tk.Label(frame, text="Password:", bg="#f7f9fa").pack(pady=5)
        password_entry = tk.Entry(frame, width=40, show="*")
        password_entry.pack(pady=5)

        tk.Label(frame, text="Department:", bg="#f7f9fa").pack(pady=5)
        department_entry = tk.Entry(frame, width=40)
        department_entry.pack(pady=5)

        tk.Label(frame, text="Role:", bg="#f7f9fa").pack(pady=5)
        role_var = tk.StringVar(value="Staff")
        ttk.OptionMenu(frame, role_var, "Staff", "Technician", "Admin").pack(pady=5)

        def submit_user():
            u = username_entry.get().strip()
            p = password_entry.get()
            d = department_entry.get().strip()
            r = role_var.get()
            if not u or not p or not d:
                return messagebox.showerror("Error", "All fields are required.")

            hashed = sha256(p.encode()).hexdigest()
            try:
                conn = self.connect_db()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, password, role, department) VALUES (%s,%s,%s,%s)",
                    (u, hashed, r, d)
                )
                conn.commit()
                messagebox.showinfo("Success", f"User '{u}' added.")
                self.view_users()
            except Error as e:
                messagebox.showerror("Database Error", str(e))
            finally:
                conn.close()

        ttk.Button(self.content_frame, text="Add User", command=submit_user).pack(pady=10)

    def delete_user(self):
        self.clear_content()
        tk.Label(self.content_frame, text="Delete User", font=("Segoe UI", 16, "bold"),
                 bg="#f7f9fa").pack(pady=20)

        columns = ("ID", "Username", "Role", "Department")
        tree = ttk.Treeview(self.content_frame, columns=columns, show="headings", height=15)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor="center")
        tree.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, role, department FROM users")
            for row in cursor.fetchall():
                tree.insert("", tk.END, values=row)
        except Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            conn.close()

        def submit_delete():
            try:
                sel = tree.selection()[0]
                user_id = tree.item(sel)["values"][0]
                conn = self.connect_db()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
                conn.commit()
                messagebox.showinfo("Deleted", f"User ID {user_id} removed.")
                self.view_users()
            except IndexError:
                messagebox.showerror("No Selection", "Please select a user first.")
            except Error as e:
                messagebox.showerror("Database Error", str(e))
            finally:
                conn.close()

        ttk.Button(self.content_frame, text="Delete Selected User", command=submit_delete).pack(pady=10)

    def view_tickets(self):
        self.clear_content()
        tk.Label(self.content_frame, text="All Tickets", font=("Segoe UI", 16, "bold"),
                 bg="#f7f9fa").pack(pady=20)

        tree_frame = tk.Frame(self.content_frame)
        tree_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        x_scroll = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        y_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        columns = ("ID", "Staff", "Department", "Issue", "Description", "Priority",
                   "Technician", "Status", "Resolution", "Created At", "Resolved At")

        tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                            xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set, height=15)
        x_scroll.config(command=tree.xview)
        y_scroll.config(command=tree.yview)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        for col in columns:
            width = 250 if col in ("Description", "Resolution") else 120
            tree.heading(col, text=col)
            tree.column(col, width=width, anchor="center")

        try:
            conn = self.connect_db()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT
                  t.id,
                  su.username AS staff_name,
                  su.department AS staff_department,
                  t.title,
                  t.description,
                  t.priority,
                  tu.username AS technician_name,
                  t.status,
                  t.resolution_notes,
                  t.created_at,
                  t.resolved_at
                FROM tickets t
                LEFT JOIN users su ON t.staff_id = su.id
                LEFT JOIN users tu ON t.technician_id = tu.id
                ORDER BY t.id
            ''')
            for row in cursor.fetchall():
                clean = tuple("" if v is None else v for v in row)
                tree.insert("", tk.END, values=clean)
        except Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            conn.close()

        def show_details(event):
            selected_item = tree.selection()
            if selected_item:
                values = tree.item(selected_item)["values"]
                detail_window = tk.Toplevel(self.dashboard)
                detail_window.title(f"Ticket Details — ID {values[0]}")
                detail_window.geometry("700x600")
                detail_window.configure(bg="#f7f9fa")

                fields = columns
                for i, value in enumerate(values):
                    label = tk.Label(detail_window, text=f"{fields[i]}:", font=("Segoe UI", 10, "bold"),
                                     bg="#f7f9fa")
                    label.pack(anchor="w", padx=10, pady=(8, 2))
                    text = tk.Text(detail_window, wrap=tk.WORD, height=2 if len(str(value)) < 60 else 4)
                    text.insert(tk.END, str(value))
                    text.config(state=tk.DISABLED, bg="#ffffff", relief=tk.FLAT)
                    text.pack(fill=tk.X, padx=10, pady=2)

        tree.bind("<Double-1>", show_details)


# Run the Admin Dashboard
if __name__ == "__main__":
    AdminDashboard()
