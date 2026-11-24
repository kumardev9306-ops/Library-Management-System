
import customtkinter as ctk
from tkinter import ttk, messagebox
from database import connect_db


from ui_theme import apply_treeview_theme
# Ye function dashboard ke andar Books page open karega
def open_books_window(parent):

    # Parent frame ke andar books ka page bana rahe hain
    page = ctk.CTkFrame(
        parent,
        fg_color="#080F1E"
    )

    page.pack(
        fill="both",
        expand=True
    )

    # ================= PAGE HEADING =================

    ctk.CTkLabel(
        page,
        text="Book Management",
        font=("Arial", 28, "bold"),
        text_color="#F8FAFC"
    ).pack(pady=20)

    # ================= INPUT FORM =================

    # Book ki details enter karne ke liye form
    form = ctk.CTkFrame(
        page,
        fg_color="#17243A"
    )

    form.pack(
        fill="x",
        padx=25,
        pady=10
    )

    title_entry = ctk.CTkEntry(
        form,
        placeholder_text="Book Title",
        width=200
    )
    title_entry.grid(row=0, column=0, padx=10, pady=15)

    author_entry = ctk.CTkEntry(
        form,
        placeholder_text="Author",
        width=180
    )
    author_entry.grid(row=0, column=1, padx=10)

    category_entry = ctk.CTkEntry(
        form,
        placeholder_text="Category",
        width=150
    )
    category_entry.grid(row=0, column=2, padx=10)

    quantity_entry = ctk.CTkEntry(
        form,
        placeholder_text="Quantity",
        width=100
    )
    quantity_entry.grid(row=0, column=3, padx=10)

    # ================= BOOKS TABLE =================

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

    columns = (
        "ID", "Title", "Author",
        "Category", "Quantity", "Available"
    )

    apply_treeview_theme(page)
    tree = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings"
    )

    # Table ke headings aur columns set kar rahe hain
    for col in columns:

        tree.heading(col, text=col)
        tree.column(col, width=130)

    tree.pack(
        fill="both",
        expand=True
    )

    # ================= SELECT BOOK =================

    # Table mein book select karne par uski details form mein aayengi
    def select_book(event):

        selected = tree.selection()

        if not selected:
            return

        values = tree.item(selected[0])["values"]

        title_entry.delete(0, "end")
        title_entry.insert(0, values[1])

        author_entry.delete(0, "end")
        author_entry.insert(0, values[2])

        category_entry.delete(0, "end")
        category_entry.insert(0, values[3])

        quantity_entry.delete(0, "end")
        quantity_entry.insert(0, values[4])

    tree.bind("<<TreeviewSelect>>", select_book)

    # ================= LOAD BOOKS =================

    # Database se saari books table mein show hongi
    def load_books():

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

            cursor.execute("SELECT * FROM books")

            records = cursor.fetchall()

            for row in records:
                tree.insert("", "end", values=row)

        except Exception as e:

            messagebox.showerror(
                "Load Error",
                str(e)
            )

        finally:

            if cursor:
                cursor.close()

            db.close()

    # ================= ADD BOOK =================

    # New book ki details database mein save karta hai
    def add_book():

        title = title_entry.get().strip()
        author = author_entry.get().strip()
        category = category_entry.get().strip()
        quantity = quantity_entry.get().strip()

        # Pehle check kar rahe hain ki koi field empty toh nahi hai
        if not title or not author or not category or not quantity:

            messagebox.showwarning(
                "Warning",
                "All fields are required!"
            )
            return

        # Quantity ko integer mein convert kar rahe hain
        try:

            quantity = int(quantity)

            if quantity <= 0:

                messagebox.showwarning(
                    "Warning",
                    "Quantity must be greater than zero!"
                )
                return

        except ValueError:

            messagebox.showerror(
                "Error",
                "Quantity must be a valid whole number!"
            )
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

            # Same title, author aur category wali book check kar rahe hain
            cursor.execute(
                """SELECT book_id FROM books
                WHERE LOWER(title) = LOWER(%s)
                AND LOWER(author) = LOWER(%s)
                AND LOWER(category) = LOWER(%s)""",
                (title, author, category)
            )

            if cursor.fetchone():

                messagebox.showwarning(
                    "Duplicate Book",
                    "This book already exists!"
                )
                return

            # New book ka record database mein insert kar rahe hain
            cursor.execute(
                """INSERT INTO books
                (title, author, category, quantity, available)
                VALUES (%s, %s, %s, %s, %s)""",
                (title, author, category, quantity, quantity)
            )

            db.commit()

            messagebox.showinfo(
                "Success",
                "Book Added Successfully!"
            )

            # Book add hone ke baad form empty kar rahe hain
            title_entry.delete(0, "end")
            author_entry.delete(0, "end")
            category_entry.delete(0, "end")
            quantity_entry.delete(0, "end")

            load_books()

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

    # ================= UPDATE BOOK =================

    # Selected book ki details update karne ke liye
    def update_book():

        selected = tree.selection()

        if not selected:

            messagebox.showwarning(
                "Warning",
                "Please select a book first!"
            )
            return

        book_id = tree.item(selected[0])["values"][0]

        title = title_entry.get().strip()
        author = author_entry.get().strip()
        category = category_entry.get().strip()
        quantity = quantity_entry.get().strip()

        if not title or not author or not category or not quantity:

            messagebox.showwarning(
                "Warning",
                "All fields are required!"
            )
            return

        # Quantity ki validation kar rahe hain
        try:

            quantity = int(quantity)

            if quantity <= 0:

                messagebox.showwarning(
                    "Warning",
                    "Quantity must be greater than zero!"
                )
                return

        except ValueError:

            messagebox.showerror(
                "Error",
                "Quantity must be a valid whole number!"
            )
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

            # Old quantity aur available books ki value le rahe hain
            cursor.execute(
                "SELECT quantity, available FROM books WHERE book_id = %s",
                (book_id,)
            )

            old_data = cursor.fetchone()

            if old_data is None:

                messagebox.showerror(
                    "Error",
                    "Book not found!"
                )
                return

            old_quantity, old_available = old_data

            # Kitni books students ke paas issued hain ye calculate kar rahe hain
            issued_count = old_quantity - old_available

            # New quantity issued books se kam nahi honi chahiye
            if quantity < issued_count:

                messagebox.showwarning(
                    "Invalid Quantity",
                    "Quantity cannot be less than issued books!"
                )
                return

            # New available quantity calculate kar rahe hain
            new_available = quantity - issued_count

            cursor.execute(
                """
                UPDATE books
                SET title = %s,
                    author = %s,
                    category = %s,
                    quantity = %s,
                    available = %s
                WHERE book_id = %s
                """,
                (
                    title, author, category,
                    quantity, new_available, book_id
                )
            )

            db.commit()

            messagebox.showinfo(
                "Success",
                "Book Updated Successfully!"
            )

            load_books()

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

    # ================= SEARCH BOOK =================

    # Book title ke basis par search kar rahe hain
    def search_book():

        keyword = title_entry.get().strip()

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
                "SELECT * FROM books WHERE title LIKE %s",
                ("%" + keyword + "%",)
            )

            records = cursor.fetchall()

            for row in records:
                tree.insert("", "end", values=row)

        except Exception as e:

            messagebox.showerror(
                "Search Error",
                str(e)
            )

        finally:

            if cursor:
                cursor.close()

            db.close()

    # ================= DELETE BOOK =================

    # Selected book ko database se delete karta hai
    def delete_book():

        selected = tree.selection()

        if not selected:

            messagebox.showwarning(
                "Warning",
                "Please select a book first!"
            )
            return

        book_id = tree.item(selected[0])["values"][0]

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this book?"
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

            # Check kar rahe hain ki book ka koi issue history record toh nahi hai
            cursor.execute(
                "SELECT COUNT(*) FROM issued_books WHERE book_id = %s",
                (book_id,)
            )

            issue_count = cursor.fetchone()[0]

            if issue_count > 0:

                messagebox.showwarning(
                    "Cannot Delete",
                    "This book has issue history and cannot be deleted!"
                )
                return

            cursor.execute(
                "DELETE FROM books WHERE book_id = %s",
                (book_id,)
            )

            db.commit()

            messagebox.showinfo(
                "Success",
                "Book Deleted Successfully!"
            )

            load_books()

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

    # Saare book operations ke buttons ek hi row mein hain
    buttons = ctk.CTkFrame(
        page,
        fg_color="transparent"
    )

    buttons.pack(pady=10)

    ctk.CTkButton(
        buttons,
        text="Add Book",
        command=add_book,
        width=130
    ).pack(side="left", padx=8)

    ctk.CTkButton(
        buttons,
        text="View All",
        command=load_books,
        width=130
    ).pack(side="left", padx=8)

    ctk.CTkButton(
        buttons,
        text="Search",
        command=search_book,
        width=130
    ).pack(side="left", padx=8)

    ctk.CTkButton(
        buttons,
        text="Delete",
        command=delete_book,
        fg_color="#DC2626",
        hover_color="#991B1B",
        width=130
    ).pack(side="left", padx=8)

    ctk.CTkButton(
        buttons,
        text="Update Book",
        command=update_book,
        fg_color="#D97706",
        hover_color="#B45309",
        width=130
    ).pack(side="left", padx=8)

    # Page open hote hi database se books load hongi
    load_books()
