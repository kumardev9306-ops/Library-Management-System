
import customtkinter as ctk
from tkinter import ttk, messagebox
from database import connect_db


from ui_theme import apply_treeview_theme
# Parent frame dashboard se milega
# mode se decide hoga issue page dikhana hai ya return page
def open_issue_return_window(parent, mode="all"):

    page = ctk.CTkFrame(parent, fg_color="#080F1E")
    page.pack(fill="both", expand=True)

    # Main heading
    heading_text = "Issue Books" if mode == "issue" else "Return Books"

    ctk.CTkLabel(
        page,
        text=heading_text,
        font=("Arial", 26, "bold"),
        text_color="white"
    ).pack(anchor="w", padx=20, pady=(15, 10))

    book_map = {}
    student_map = {}

    # Issue mode me book aur student select karne ka form dikhega
    if mode in ("issue", "all"):

        form = ctk.CTkFrame(page, fg_color="#17243A")
        form.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            form,
            text="Select Book",
            font=("Arial", 13, "bold")
        ).grid(row=0, column=0, padx=15, pady=(12, 5))

        book_box = ctk.CTkComboBox(
            form,
            values=["No books available"],
            width=300,
            state="readonly"
        )
        book_box.grid(row=1, column=0, padx=15, pady=(0, 12))

        ctk.CTkLabel(
            form,
            text="Select Student",
            font=("Arial", 13, "bold")
        ).grid(row=0, column=1, padx=15, pady=(12, 5))

        student_box = ctk.CTkComboBox(
            form,
            values=["No students"],
            width=300,
            state="readonly"
        )
        student_box.grid(row=1, column=1, padx=15, pady=(0, 12))

    # History heading
    ctk.CTkLabel(
        page,
        text="Book Issue History",
        font=("Arial", 20, "bold"),
        text_color="white"
    ).pack(anchor="w", padx=20, pady=(15, 5))

    # Search bar
    search_frame = ctk.CTkFrame(
        page,
        fg_color="transparent"
    )
    search_frame.pack(fill="x", padx=20, pady=5)

    search_entry = ctk.CTkEntry(
        search_frame,
        placeholder_text="Search by book or student name...",
        width=300,
        height=38
    )
    search_entry.pack(side="left", padx=5)

    # History table
    table_frame = ctk.CTkFrame(page)
    table_frame.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=10
    )

    columns = (
        "Issue ID",
        "Book",
        "Student",
        "Issue Date",
        "Return Date",
        "Status"
    )

    apply_treeview_theme(page)
    tree = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        selectmode="browse"
    )

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=130, anchor="center")

    tree.pack(fill="both", expand=True)

    # Dropdown me books aur students load karna
    def load_options():

        if mode not in ("issue", "all"):
            return

        db = connect_db()

        if db is None:
            messagebox.showerror(
                "Database Error",
                "Unable to connect to database!"
            )
            return

        cursor = db.cursor()

        try:
            cursor.execute(
                """
                SELECT book_id, title, available
                FROM books
                ORDER BY title
                """
            )

            book_map.clear()
            book_values = []

            for book_id, title, available in cursor.fetchall():

                if available > 0:
                    label = f"{book_id} - {title} ({available} available)"
                    book_values.append(label)
                    book_map[label] = book_id

            book_box.configure(
                values=book_values if book_values else ["No books available"]
            )

            book_box.set(
                book_values[0] if book_values else "No books available"
            )

            cursor.execute(
                "SELECT student_id, name FROM students ORDER BY name"
            )

            student_map.clear()
            student_values = []

            for student_id, name in cursor.fetchall():

                label = f"{student_id} - {name}"
                student_values.append(label)
                student_map[label] = student_id

            student_box.configure(
                values=student_values if student_values else ["No students"]
            )

            student_box.set(
                student_values[0] if student_values else "No students"
            )

        except Exception as e:
            messagebox.showerror("Error", str(e))

        finally:
            cursor.close()
            db.close()

    # Selected book ko student ko issue karna
    def issue_book():

        selected_book = book_box.get()
        selected_student = student_box.get()

        if selected_book not in book_map:
            messagebox.showwarning(
                "Warning",
                "Please select an available book!"
            )
            return

        if selected_student not in student_map:
            messagebox.showwarning(
                "Warning",
                "Please select a student!"
            )
            return

        book_id = book_map[selected_book]
        student_id = student_map[selected_student]

        db = connect_db()

        if db is None:
            messagebox.showerror(
                "Database Error",
                "Unable to connect to database!"
            )
            return

        cursor = db.cursor()

        try:
            # Check karo ki same book pehle se issue toh nahi hai
            cursor.execute(
                """
                SELECT issue_id FROM issued_books
                WHERE book_id = %s
                AND student_id = %s
                AND status = 'Issued'
                """,
                (book_id, student_id)
            )

            if cursor.fetchone():
                messagebox.showwarning(
                    "Already Issued",
                    "This student already has this book issued!"
                )
                return

            # Available quantity ko ek kam kar do
            cursor.execute(
                """
                UPDATE books
                SET available = available - 1
                WHERE book_id = %s AND available > 0
                """,
                (book_id,)
            )

            if cursor.rowcount == 0:
                raise ValueError("Book is no longer available.")

            # Issue ki entry database me save karo
            cursor.execute(
                """
                INSERT INTO issued_books
                (book_id, student_id, issue_date, status)
                VALUES (%s, %s, CURDATE(), 'Issued')
                """,
                (book_id, student_id)
            )

            db.commit()

            messagebox.showinfo(
                "Success",
                "Book Issued Successfully!"
            )

            load_options()
            load_issued_books()

        except Exception as e:
            db.rollback()
            messagebox.showerror("Issue Error", str(e))

        finally:
            cursor.close()
            db.close()

    # Database se issue history load karna
    def load_issued_books(keyword=""):

        for item in tree.get_children():
            tree.delete(item)

        db = connect_db()

        if db is None:
            messagebox.showerror(
                "Database Error",
                "Unable to connect to database!"
            )
            return

        cursor = db.cursor()

        try:
            cursor.execute(
                """
                SELECT
                    ib.issue_id,
                    b.title,
                    s.name,
                    ib.issue_date,
                    ib.return_date,
                    ib.status
                FROM issued_books ib
                JOIN books b ON ib.book_id = b.book_id
                JOIN students s ON ib.student_id = s.student_id
                WHERE b.title LIKE %s
                   OR s.name LIKE %s
                ORDER BY ib.issue_id DESC
                """,
                (
                    "%" + keyword + "%",
                    "%" + keyword + "%"
                )
            )

            records = cursor.fetchall()

            for row in records:
                tree.insert("", "end", values=row)

        except Exception as e:
            messagebox.showerror("History Error", str(e))

        finally:
            cursor.close()
            db.close()

    # Search button ka function
    def search_history():

        keyword = search_entry.get().strip()
        load_issued_books(keyword)

    # Selected book ko return karna
    def return_book():

        selected = tree.selection()

        if not selected:
            messagebox.showwarning(
                "Warning",
                "Please select a book first!"
            )
            return

        values = tree.item(selected[0])["values"]

        issue_id = values[0]
        status = values[5]

        if status != "Issued":
            messagebox.showwarning(
                "Already Returned",
                "This book has already been returned!"
            )
            return

        confirm = messagebox.askyesno(
            "Confirm Return",
            "Are you sure you want to return this book?"
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

        cursor = db.cursor()

        try:
            cursor.execute(
                """
                SELECT book_id FROM issued_books
                WHERE issue_id = %s AND status = 'Issued'
                """,
                (issue_id,)
            )

            record = cursor.fetchone()

            if record is None:
                raise ValueError(
                    "This book has already been returned."
                )

            book_id = record[0]

            # Issue record ka status update karo
            cursor.execute(
                """
                UPDATE issued_books
                SET status = 'Returned',
                    return_date = CURDATE()
                WHERE issue_id = %s AND status = 'Issued'
                """,
                (issue_id,)
            )

            if cursor.rowcount == 0:
                raise ValueError("Return could not be completed.")

            # Book ki available quantity wapas badha do
            cursor.execute(
                """
                UPDATE books
                SET available = available + 1
                WHERE book_id = %s
                """,
                (book_id,)
            )

            if cursor.rowcount == 0:
                raise ValueError("Book record not found.")

            db.commit()

            messagebox.showinfo(
                "Success",
                "Book Returned Successfully!"
            )

            load_options()
            load_issued_books(search_entry.get().strip())

        except Exception as e:
            db.rollback()
            messagebox.showerror("Return Error", str(e))

        finally:
            cursor.close()
            db.close()

    # Neeche wale buttons mode ke hisaab se dikhenge
    buttons = ctk.CTkFrame(
        page,
        fg_color="transparent"
    )
    buttons.pack(pady=10)

    if mode in ("issue", "all"):

        ctk.CTkButton(
            buttons,
            text="Issue Book",
            width=140,
            height=38,
            command=issue_book
        ).pack(side="left", padx=6)

    if mode in ("return", "all"):

        ctk.CTkButton(
            buttons,
            text="Return Selected Book",
            width=180,
            height=38,
            fg_color="#059669",
            hover_color="#047857",
            command=return_book
        ).pack(side="left", padx=6)

    ctk.CTkButton(
        buttons,
        text="Search History",
        width=140,
        height=38,
        command=search_history
    ).pack(side="left", padx=6)

    # Refresh karne par latest records dikhenge
    def refresh_all():

        search_entry.delete(0, "end")
        load_options()
        load_issued_books()

    ctk.CTkButton(
        buttons,
        text="Refresh All",
        width=120,
        height=38,
        fg_color="#475569",
        hover_color="#334155",
        command=refresh_all
    ).pack(side="left", padx=6)

    # Starting me data load kar do
    load_options()
    load_issued_books()
