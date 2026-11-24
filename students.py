
import re
import customtkinter as ctk

from tkinter import ttk, messagebox
from database import connect_db


from ui_theme import apply_treeview_theme
# Ye function dashboard ke andar Students page open karega
def open_students_window(parent):

    # Parent frame ke andar students ka page bana rahe hain
    page = ctk.CTkFrame(
        parent,
        fg_color="#080F1E"
    )

    page.pack(fill="both", expand=True)

    # ================= PAGE HEADING =================

    ctk.CTkLabel(
        page,
        text="Student Management",
        font=("Arial", 28, "bold"),
        text_color="white"
    ).pack(pady=20)

    # ================= PHONE VALIDATION =================

    # Phone mein sirf 10 digits tak allow kar rahe hain
    def validate_phone_input(value):
        return value.isdigit() and len(value) <= 10 or value == ""

    phone_validator = page.register(validate_phone_input)

    # ================= INPUT FORM =================

    form = ctk.CTkFrame(
        page,
        fg_color="#17243A"
    )

    form.pack(fill="x", padx=25, pady=10)

    name_entry = ctk.CTkEntry(
        form,
        placeholder_text="Student Name",
        width=220
    )
    name_entry.grid(row=0, column=0, padx=10, pady=20)

    email_entry = ctk.CTkEntry(
        form,
        placeholder_text="Email",
        width=220
    )
    email_entry.grid(row=0, column=1, padx=10)

    phone_entry = ctk.CTkEntry(
        form,
        placeholder_text="Phone (10 digits)",
        width=180,
        validate="key",
        validatecommand=(phone_validator, "%P")
    )
    phone_entry.grid(row=0, column=2, padx=10)

    # ================= STUDENT TABLE =================

    table_frame = ctk.CTkFrame(
        page,
        fg_color="#131F35"
    )

    table_frame.pack(
        fill="both",
        expand=True,
        padx=25,
        pady=15
    )

    columns = ("ID", "Name", "Email", "Phone")

    apply_treeview_theme(page)
    tree = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        selectmode="browse"
    )

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=180)

    tree.pack(fill="both", expand=True)

    # ================= CLEAR FIELDS =================

    # Form ke saare input boxes clear karta hai
    def clear_fields():

        name_entry.delete(0, "end")
        email_entry.delete(0, "end")
        phone_entry.delete(0, "end")

        tree.selection_remove(tree.selection())

    # Sirf input boxes clear karta hai
    def clear_entries_only():

        name_entry.delete(0, "end")
        email_entry.delete(0, "end")
        phone_entry.delete(0, "end")

    # ================= LOAD STUDENTS =================

    # Database se students ke records table mein load karta hai
    def load_students():

        # Table ke purane records clear kar rahe hain
        for item in tree.get_children():
            tree.delete(item)

        db = connect_db()

        if db is None:
            messagebox.showerror(
                "Database Error",
                "Unable to connect to database!"
            )
            return

        cursor = None

        try:

            cursor = db.cursor()

            cursor.execute(
                "SELECT * FROM students ORDER BY student_id DESC"
            )

            records = cursor.fetchall()

            # Database ke records table mein show kar rahe hain
            for row in records:
                tree.insert(
                    "",
                    "end",
                    values=row
                )

        except Exception as e:

            messagebox.showerror(
                "Load Error",
                str(e)
            )

        finally:

            if cursor:
                cursor.close()

            db.close()

    # ================= SELECT STUDENT =================

    # Student select karne par uski details form mein aayengi
    def select_student(event):

        selected = tree.selection()

        if not selected:
            return

        values = tree.item(selected[0])["values"]

        clear_entries_only()

        name_entry.insert(0, values[1])
        email_entry.insert(0, values[2])
        phone_entry.insert(0, values[3])

    tree.bind(
        "<<TreeviewSelect>>",
        select_student
    )

    # ================= VALIDATE STUDENT DETAILS =================

    # Add aur Update ke liye details validate karta hai
    def get_student_details():

        student_name = name_entry.get().strip()
        student_email = email_entry.get().strip().lower()
        phone = phone_entry.get().strip()

        if not student_name:

            messagebox.showwarning(
                "Warning",
                "Student name is required!"
            )
            return None

        email_pattern = (
            r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        )

        if not re.fullmatch(email_pattern, student_email):

            messagebox.showwarning(
                "Invalid Email",
                "Please enter a valid email address!"
            )
            return None

        if not phone.isdigit() or len(phone) != 10:

            messagebox.showwarning(
                "Invalid Phone",
                "Phone number must contain exactly 10 digits!"
            )
            return None

        return student_name, student_email, phone

    # ================= ADD STUDENT =================

    # New student ka record database mein insert karta hai
    def add_student():

        details = get_student_details()

        if details is None:
            return

        db = connect_db()

        if db is None:
            messagebox.showerror(
                "Database Error",
                "Unable to connect to database!"
            )
            return

        cursor = None

        try:

            cursor = db.cursor()

            # Same email pehle se registered hai ya nahi check kar rahe hain
            cursor.execute(
                "SELECT student_id FROM students WHERE LOWER(email) = %s",
                (details[1],)
            )

            if cursor.fetchone():

                messagebox.showwarning(
                    "Duplicate Email",
                    "This email is already registered!"
                )
                return

            cursor.execute(
                """
                INSERT INTO students (name, email, phone)
                VALUES (%s, %s, %s)
                """,
                details
            )

            db.commit()

            messagebox.showinfo(
                "Success",
                "Student Added Successfully!"
            )

            clear_fields()
            load_students()

        except Exception as e:

            db.rollback()

            messagebox.showerror(
                "Database Error",
                str(e)
            )

        finally:

            if cursor:
                cursor.close()

            db.close()

    # ================= UPDATE STUDENT =================

    # Selected student ki details update karta hai
    def update_student():

        selected = tree.selection()

        if not selected:

            messagebox.showwarning(
                "Warning",
                "Please select a student first!"
            )
            return

        student_id = tree.item(selected[0])["values"][0]

        details = get_student_details()

        if details is None:
            return

        db = connect_db()

        if db is None:

            messagebox.showerror(
                "Database Error",
                "Unable to connect to database!"
            )
            return

        cursor = None

        try:

            cursor = db.cursor()

            # Dusre student ke same email ka check kar rahe hain
            cursor.execute(
                """
                SELECT student_id FROM students
                WHERE LOWER(email) = %s AND student_id != %s
                """,
                (details[1], student_id)
            )

            if cursor.fetchone():

                messagebox.showwarning(
                    "Duplicate Email",
                    "This email belongs to another student!"
                )
                return

            cursor.execute(
                """
                UPDATE students
                SET name = %s, email = %s, phone = %s
                WHERE student_id = %s
                """,
                (*details, student_id)
            )

            db.commit()

            messagebox.showinfo(
                "Success",
                "Student Updated Successfully!"
            )

            clear_fields()
            load_students()

        except Exception as e:

            db.rollback()

            messagebox.showerror(
                "Update Error",
                str(e)
            )

        finally:

            if cursor:
                cursor.close()

            db.close()

    # ================= SEARCH STUDENT =================

    # Name, email ya phone se student search karta hai
    def search_student():

        keyword = name_entry.get().strip()

        db = connect_db()

        if db is None:

            messagebox.showerror(
                "Database Error",
                "Unable to connect to database!"
            )
            return

        cursor = None

        try:

            cursor = db.cursor()

            cursor.execute(
                """
                SELECT * FROM students
                WHERE name LIKE %s OR email LIKE %s OR phone LIKE %s
                ORDER BY student_id DESC
                """,
                (
                    "%" + keyword + "%",
                    "%" + keyword + "%",
                    "%" + keyword + "%"
                )
            )

            # Table ke purane search results clear kar rahe hain
            for item in tree.get_children():
                tree.delete(item)

            # Search ke naye results show kar rahe hain
            for row in cursor.fetchall():

                tree.insert(
                    "",
                    "end",
                    values=row
                )

        except Exception as e:

            messagebox.showerror(
                "Search Error",
                str(e)
            )

        finally:

            if cursor:
                cursor.close()

            db.close()

    # ================= DELETE STUDENT =================

    # Student ko tabhi delete karenge jab uski issue history na ho
    def delete_student():

        selected = tree.selection()

        if not selected:

            messagebox.showwarning(
                "Warning",
                "Please select a student first!"
            )
            return

        student_id = tree.item(selected[0])["values"][0]

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this student?"
        )

        if not confirm:
            return

        db = connect_db()

        if db is None:

            messagebox.showerror(
                "Database Error",
                "Unable to connect to database!"
            )
            return

        cursor = None

        try:

            cursor = db.cursor()

            # Student ki puri issue history check kar rahe hain
            cursor.execute(
                """
                SELECT COUNT(*) FROM issued_books
                WHERE student_id = %s
                """,
                (student_id,)
            )

            history_count = cursor.fetchone()[0]

            if history_count > 0:

                messagebox.showwarning(
                    "Cannot Delete",
                    "This student has issue history. Record cannot be deleted!"
                )
                return

            cursor.execute(
                "DELETE FROM students WHERE student_id = %s",
                (student_id,)
            )

            db.commit()

            messagebox.showinfo(
                "Success",
                "Student Deleted Successfully!"
            )

            clear_fields()
            load_students()

        except Exception as e:

            db.rollback()

            messagebox.showerror(
                "Delete Error",
                str(e)
            )

        finally:

            if cursor:
                cursor.close()

            db.close()

    # ================= BUTTONS =================

    buttons = ctk.CTkFrame(
        page,
        fg_color="transparent"
    )

    buttons.pack(pady=12)

    ctk.CTkButton(
        buttons,
        text="Add Student",
        command=add_student,
        width=130
    ).pack(side="left", padx=5)

    ctk.CTkButton(
        buttons,
        text="Update Student",
        command=update_student,
        fg_color="#D97706",
        hover_color="#B45309",
        width=130
    ).pack(side="left", padx=5)

    ctk.CTkButton(
        buttons,
        text="View All",
        command=load_students,
        width=110
    ).pack(side="left", padx=5)

    ctk.CTkButton(
        buttons,
        text="Search",
        command=search_student,
        width=110
    ).pack(side="left", padx=5)

    ctk.CTkButton(
        buttons,
        text="Clear Fields",
        command=clear_fields,
        fg_color="#475569",
        hover_color="#334155",
        width=120
    ).pack(side="left", padx=5)

    ctk.CTkButton(
        buttons,
        text="Delete",
        command=delete_student,
        fg_color="#DC2626",
        hover_color="#991B1B",
        width=110
    ).pack(side="left", padx=5)

    # Page open hote hi students ke records load honge
    load_students()
