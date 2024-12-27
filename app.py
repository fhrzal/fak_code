import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime
import hashlib
import customtkinter as ctk  # Untuk tampilan modern

class Database:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="my-Password",
            database="db_pulsa"
        )
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Tabel Users
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE,
                password VARCHAR(255),
                role VARCHAR(10),
                saldo DECIMAL(10,2) DEFAULT 0.00
            )
        """)

        # Tabel Products
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                price DECIMAL(10,2),
                type VARCHAR(20)
            )
        """)

        # Tabel Transactions
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                product_id INT,
                amount DECIMAL(10,2),
                transaction_date DATETIME,
                type VARCHAR(20),
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)
        self.conn.commit()

class LoginWindow:
    def __init__(self):
        self.db = Database()
        self.window = ctk.CTk()
        self.window.title("Login Sistem Penjualan Pulsa")
        self.window.geometry("400x550")
        
        # Mengatur tema modern
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Frame utama
        self.frame = ctk.CTkFrame(self.window)
        self.frame.pack(pady=20, padx=40, fill="both", expand=True)

        # Label judul
        self.label = ctk.CTkLabel(self.frame, text="Login System", font=("Roboto", 24))
        self.label.pack(pady=12, padx=10)

        # Input username
        self.username = ctk.CTkEntry(self.frame, placeholder_text="Username")
        self.username.pack(pady=12, padx=10)

        # Input password
        self.password = ctk.CTkEntry(self.frame, placeholder_text="Password", show="*")
        self.password.pack(pady=12, padx=10)

        # Tombol login
        self.login_button = ctk.CTkButton(self.frame, text="Login", command=self.login)
        self.login_button.pack(pady=12, padx=10)

        # Tombol register
        self.register_button = ctk.CTkButton(self.frame, text="Register", command=self.show_register)
        self.register_button.pack(pady=12, padx=10)

    def login(self):
        username = self.username.get()
        password = self.password.get()

        # Hash password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        print(f"Input Username: {username}, Hashed Password: {hashed_password}")  # Debugging

        # Query database
        self.db.cursor.execute(
            "SELECT * FROM users WHERE username = %s AND password = %s", 
            (username, hashed_password)
        )
        user = self.db.cursor.fetchone()
        print(f"SQL Query Result: {user}")  # Debugging

        if user:
            role = user[3].strip().lower()  # Normalisasi role
            print(f"User Role: {role}")  # Debugging
            self.window.destroy()
            if role == 'admin':
                AdminWindow(user[0])
            else:
                UserWindow(user[0])
        else:
            messagebox.showerror("Error", "Invalid username or password")



    def show_register(self):
        self.window.destroy()
        RegisterWindow()

class RegisterWindow:
    def __init__(self):
        self.db = Database()
        self.window = ctk.CTk()
        self.window.title("Register")
        self.window.geometry("400x550")

        # Frame utama
        self.frame = ctk.CTkFrame(self.window)
        self.frame.pack(pady=20, padx=40, fill="both", expand=True)

        # Label judul
        self.label = ctk.CTkLabel(self.frame, text="Register", font=("Roboto", 24))
        self.label.pack(pady=12, padx=10)

        # Input fields
        self.username = ctk.CTkEntry(self.frame, placeholder_text="Username")
        self.username.pack(pady=12, padx=10)

        self.password = ctk.CTkEntry(self.frame, placeholder_text="Password", show="*")
        self.password.pack(pady=12, padx=10)

        self.confirm_password = ctk.CTkEntry(self.frame, placeholder_text="Confirm Password", show="*")
        self.confirm_password.pack(pady=12, padx=10)

        # self.role = ctk.CTkEntry(self.frame, placeholder_text="Role", show="*")
        # self.role.pack(pady=12, padx=10)
        
        
        self.role_var = ctk.StringVar(value="user")  # Default ke "User"
        self.role = ctk.CTkLabel(self.frame, text="Pilih Role Anda:", font=("Arial", 14))
        self.role.pack(pady=10)
        
        self.role = ctk.CTkRadioButton(self.frame, text="Admin", variable=self.role_var, value="admin")
        self.role.pack(pady=5, padx=10)

        self.role = ctk.CTkRadioButton(self.frame, text="User", variable=self.role_var, value="user")
        self.role.pack(pady=5, padx=10)

        # Tombol register
        self.register_button = ctk.CTkButton(self.frame, text="Register", command=self.register)
        self.register_button.pack(pady=12, padx=10)

        # Tombol kembali ke login
        self.back_button = ctk.CTkButton(self.frame, text="Back to Login", command=self.back_to_login)
        self.back_button.pack(pady=12, padx=10)

    def register(self):
        username = self.username.get()
        password = self.password.get()
        confirm = self.confirm_password.get()
        role = self.role_var.get()

        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return

        # Hash password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        try:
            self.db.cursor.execute("""
                INSERT INTO users (username, password, role)
                VALUES (%s, %s, %s)
            """, (username, hashed_password, role))
            self.db.conn.commit()
            messagebox.showinfo("Success", "Registration successful!")
            self.back_to_login()
        except mysql.connector.IntegrityError:
            messagebox.showerror("Error", "Username already exists")

    def back_to_login(self):
        self.window.destroy()
        LoginWindow()

class UserWindow:
    def __init__(self, user_id):
        self.db = Database()
        self.user_id = user_id
        self.window = ctk.CTk()
        self.window.title("User Dashboard")
        self.window.geometry("800x600")

        # Sidebar frame
        self.sidebar = ctk.CTkFrame(self.window, width=200)
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)

        # Info saldo
        self.update_saldo_label()

        # Tombol-tombol menu
        self.buy_button = ctk.CTkButton(self.sidebar, text="Beli Produk", command=self.show_products)
        self.buy_button.pack(pady=10)

        self.topup_button = ctk.CTkButton(self.sidebar, text="Top Up Saldo", command=self.show_topup)
        self.topup_button.pack(pady=10)

        self.history_button = ctk.CTkButton(self.sidebar, text="Riwayat Transaksi", 
                                          command=self.show_history)
        self.history_button.pack(pady=10)

        self.logout_button = ctk.CTkButton(self.sidebar, text="Logout", command=self.logout)
        self.logout_button.pack(pady=10)

        # Main content frame
        self.main_frame = ctk.CTkFrame(self.window)
        self.main_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.show_products()  # Tampilkan produk sebagai default view

    def update_saldo_label(self):
        self.db.cursor.execute("SELECT saldo FROM users WHERE id = %s", (self.user_id,))
        saldo = self.db.cursor.fetchone()[0]
        try:
            self.saldo_label.destroy()
        except:
            pass
        self.saldo_label = ctk.CTkLabel(self.sidebar, 
                                       text=f"Saldo: Rp {saldo:,.2f}", 
                                       font=("Roboto", 16))
        self.saldo_label.pack(pady=20)

    def show_products(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Label judul
        title = ctk.CTkLabel(self.main_frame, text="Daftar Produk", font=("Roboto", 20))
        title.pack(pady=10)

        # Treeview untuk produk
        columns = ('ID', 'Nama', 'Harga', 'Tipe')
        tree = ttk.Treeview(self.main_frame, columns=columns, show='headings')

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        self.db.cursor.execute("SELECT * FROM products")
        for product in self.db.cursor.fetchall():
            tree.insert('', 'end', values=product)

        tree.pack(pady=10, fill='both', expand=True)

        # Frame untuk pembelian
        buy_frame = ctk.CTkFrame(self.main_frame)
        buy_frame.pack(pady=10)

        ctk.CTkLabel(buy_frame, text="ID Produk:").pack(side='left', padx=5)
        product_id = ctk.CTkEntry(buy_frame)
        product_id.pack(side='left', padx=5)

        ctk.CTkButton(buy_frame, text="Beli", 
                     command=lambda: self.buy_product(product_id.get())).pack(side='left', padx=5)

    def buy_product(self, product_id):
        try:
            product_id = int(product_id)
            # Cek produk
            self.db.cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
            product = self.db.cursor.fetchone()
            
            if not product:
                messagebox.showerror("Error", "Produk tidak ditemukan")
                return

            # Cek saldo
            self.db.cursor.execute("SELECT saldo FROM users WHERE id = %s", (self.user_id,))
            saldo = self.db.cursor.fetchone()[0]

            if saldo < product[2]:
                messagebox.showerror("Error", "Saldo tidak mencukupi")
                return

            # Proses transaksi
            self.db.cursor.execute("""
                INSERT INTO transactions (user_id, product_id, amount, transaction_date, type)
                VALUES (%s, %s, %s, %s, %s)
            """, (self.user_id, product_id, product[2], datetime.now(), 'purchase'))

            # Update saldo
            self.db.cursor.execute("""
                UPDATE users SET saldo = saldo - %s WHERE id = %s
            """, (product[2], self.user_id))

            self.db.conn.commit()
            messagebox.showinfo("Success", "Pembelian berhasil!")
            self.update_saldo_label()

        except ValueError:
            messagebox.showerror("Error", "ID Produk harus berupa angka")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_topup(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Label judul
        title = ctk.CTkLabel(self.main_frame, text="Top Up Saldo", font=("Roboto", 20))
        title.pack(pady=20)

        # Frame untuk input
        input_frame = ctk.CTkFrame(self.main_frame)
        input_frame.pack(pady=20)

        ctk.CTkLabel(input_frame, text="Jumlah Top Up:").pack(pady=10)
        amount = ctk.CTkEntry(input_frame)
        amount.pack(pady=10)

        ctk.CTkButton(input_frame, text="Top Up", 
                     command=lambda: self.process_topup(amount.get())).pack(pady=10)

    def process_topup(self, amount):
        try:
            amount = float(amount)
            if amount <= 0:
                messagebox.showerror("Error", "Jumlah harus lebih dari 0")
                return

            # Proses top up
            self.db.cursor.execute("""
                UPDATE users SET saldo = saldo + %s WHERE id = %s
            """, (amount, self.user_id))

            # Catat transaksi
            self.db.cursor.execute("""
                INSERT INTO transactions (user_id, amount, transaction_date, type)
                VALUES (%s, %s, %s, %s)
            """, (self.user_id, amount, datetime.now(), 'topup'))

            self.db.conn.commit()
            messagebox.showinfo("Success", "Top up berhasil!")
            self.update_saldo_label()

        except ValueError:
            messagebox.showerror("Error", "Jumlah harus berupa angka")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_history(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Label judul
        title = ctk.CTkLabel(self.main_frame, text="Riwayat Transaksi", font=("Roboto", 20))
        title.pack(pady=10)

        # Treeview untuk riwayat
        columns = ('ID', 'Tanggal', 'Tipe', 'Jumlah', 'Detail')
        tree = ttk.Treeview(self.main_frame, columns=columns, show='headings')

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        # Ambil data transaksi
        self.db.cursor.execute("""
            SELECT t.id, t.transaction_date, t.type, t.amount, 
                   COALESCE(p.name, 'Top Up') as detail
            FROM transactions t
            LEFT JOIN products p ON t.product_id = p.id
            WHERE t.user_id = %s
            ORDER BY t.transaction_date DESC
        """, (self.user_id,))

        for transaction in self.db.cursor.fetchall():
            tree.insert('', 'end', values=transaction)

        tree.pack(pady=10, fill='both', expand=True)

    def logout(self):
        self.window.destroy()
        LoginWindow()

class AdminWindow:
    def __init__(self, user_id):
        self.db = Database()
        self.user_id = user_id
        self.window = ctk.CTk()
        self.window.title("Admin Dashboard")
        self.window.geometry("800x600")

        # Sidebar frame
        self.sidebar = ctk.CTkFrame(self.window, width=200)
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)

        # Tombol-tombol menu
        self.products_button = ctk.CTkButton(self.sidebar, text="Kelola Produk", 
                                           command=self.show_products)
        self.products_button.pack(pady=10)

        self.add_product_button = ctk.CTkButton(self.sidebar, text="Tambah Produk", 
                                              command=self.show_add_product)
        self.add_product_button.pack(pady=10)

        self.logout_button = ctk.CTkButton(self.sidebar, text="Logout", command=self.logout)
        self.logout_button.pack(pady=10)

        # Main content frame
        self.main_frame = ctk.CTkFrame(self.window)
        self.main_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.show_products()  # Tampilkan produk sebagai default view

    def show_products(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Label judul
        title = ctk.CTkLabel(self.main_frame, text="Kelola Produk", font=("Roboto", 20))
        title.pack(pady=10)

        # Treeview untuk produk
        columns = ('ID', 'Nama', 'Harga', 'Tipe')
        tree = ttk.Treeview(self.main_frame, columns=columns, show='headings')

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        self.db.cursor.execute("SELECT * FROM products")
        for product in self.db.cursor.fetchall():
            tree.insert('', 'end', values=product)

        tree.pack(pady=10, fill='both', expand=True)

        # Frame untuk aksi
        action_frame = ctk.CTkFrame(self.main_frame)
        action_frame.pack(pady=10)

        # Input fields untuk edit/hapus
        ctk.CTkLabel(action_frame, text="ID Produk:").grid(row=0, column=0, padx=5)
        product_id = ctk.CTkEntry(action_frame)
        product_id.grid(row=0, column=1, padx=5)

        edit_button = ctk.CTkButton(action_frame, text="Edit", 
                                  command=lambda: self.edit_product(product_id.get()))
        edit_button.grid(row=0, column=2, padx=5)

        delete_button = ctk.CTkButton(action_frame, text="Hapus", 
                                    command=lambda: self.delete_product(product_id.get()))
        delete_button.grid(row=0, column=3, padx=5)

    def show_add_product(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Label judul
        title = ctk.CTkLabel(self.main_frame, text="Tambah Produk", font=("Roboto", 20))
        title.pack(pady=20)

        # Form frame
        form_frame = ctk.CTkFrame(self.main_frame)
        form_frame.pack(pady=20)

        # Input fields
        ctk.CTkLabel(form_frame, text="Nama Produk:").pack(pady=5)
        name = ctk.CTkEntry(form_frame)
        name.pack(pady=5)

        ctk.CTkLabel(form_frame, text="Harga:").pack(pady=5)
        price = ctk.CTkEntry(form_frame)
        price.pack(pady=5)

        ctk.CTkLabel(form_frame, text="Tipe:").pack(pady=5)
        type_var = tk.StringVar(value="Pulsa")
        type_options = ["Pulsa", "Kuota Internet"]
        type_menu = ctk.CTkOptionMenu(form_frame, values=type_options, variable=type_var)
        type_menu.pack(pady=5)

        # Tombol submit
        submit_button = ctk.CTkButton(form_frame, text="Tambah", 
                                    command=lambda: self.add_product(name.get(), price.get(), 
                                                                   type_var.get()))
        submit_button.pack(pady=20)

    def add_product(self, name, price, type_):
        try:
            price = float(price)
            if price <= 0:
                messagebox.showerror("Error", "Harga harus lebih dari 0")
                return

            self.db.cursor.execute("""
                INSERT INTO products (name, price, type)
                VALUES (%s, %s, %s)
            """, (name, price, type_))
            
            self.db.conn.commit()
            messagebox.showinfo("Success", "Produk berhasil ditambahkan!")
            self.show_products()

        except ValueError:
            messagebox.showerror("Error", "Harga harus berupa angka")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def edit_product(self, product_id):
        try:
            product_id = int(product_id)
            self.db.cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
            product = self.db.cursor.fetchone()
            
            if not product:
                messagebox.showerror("Error", "Produk tidak ditemukan")
                return

            # Buat window baru untuk edit
            edit_window = ctk.CTkToplevel(self.window)
            edit_window.title("Edit Produk")
            edit_window.geometry("300x400")

            # Form fields
            ctk.CTkLabel(edit_window, text="Nama Produk:").pack(pady=5)
            name = ctk.CTkEntry(edit_window)
            name.insert(0, product[1])
            name.pack(pady=5)

            ctk.CTkLabel(edit_window, text="Harga:").pack(pady=5)
            price = ctk.CTkEntry(edit_window)
            price.insert(0, str(product[2]))
            price.pack(pady=5)

            ctk.CTkLabel(edit_window, text="Tipe:").pack(pady=5)
            type_var = tk.StringVar(value=product[3])
            type_options = ["Pulsa", "Kuota Internet"]
            type_menu = ctk.CTkOptionMenu(edit_window, values=type_options, variable=type_var)
            type_menu.pack(pady=5)

            # Tombol update
            update_button = ctk.CTkButton(edit_window, text="Update", 
                                        command=lambda: self.update_product(product_id, 
                                                                         name.get(), 
                                                                         price.get(), 
                                                                         type_var.get(), 
                                                                         edit_window))
            update_button.pack(pady=20)

        except ValueError:
            messagebox.showerror("Error", "ID Produk harus berupa angka")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_product(self, product_id, name, price, type_, window):
        try:
            price = float(price)
            if price <= 0:
                messagebox.showerror("Error", "Harga harus lebih dari 0")
                return

            self.db.cursor.execute("""
                UPDATE products 
                SET name = %s, price = %s, type = %s
                WHERE id = %s
            """, (name, price, type_, product_id))
            
            self.db.conn.commit()
            messagebox.showinfo("Success", "Produk berhasil diupdate!")
            window.destroy()
            self.show_products()

        except ValueError:
            messagebox.showerror("Error", "Harga harus berupa angka")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_product(self, product_id):
        try:
            product_id = int(product_id)
            if messagebox.askyesno("Konfirmasi", "Anda yakin ingin menghapus produk ini?"):
                self.db.cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
                self.db.conn.commit()
                messagebox.showinfo("Success", "Produk berhasil dihapus!")
                self.show_products()

        except ValueError:
            messagebox.showerror("Error", "ID Produk harus berupa angka")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def logout(self):
        self.window.destroy()
        LoginWindow()

if __name__ == "__main__":
    LoginWindow().window.mainloop()
  
