# db.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import sqlite3
import os

class DBManagerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SQLite 多数据库管理器 (支持 extra 属性)")
        self.root.geometry("650x480")
        self.root.resizable(True, True)

        self.conn = None
        self.db_path = None

        # 菜单
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="新建数据库...", command=self.create_database)
        file_menu.add_command(label="打开数据库...", command=self.open_database)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.on_close)
        menubar.add_cascade(label="文件", menu=file_menu)

        # 状态栏
        self.status_var = tk.StringVar(value="当前数据库：未打开")
        tk.Label(self.root, textvariable=self.status_var, font=("Arial", 10, "bold"),
                 anchor="w", bg="#f0f0f0").pack(fill=tk.X, padx=5, pady=5)

        # 列表（使用 Treeview 显示多列）
        list_frame = tk.Frame(self.root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("ID", "Content", "Extra")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Content", text="内容")
        self.tree.heading("Extra", text="额外属性")
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Content", width=250)
        self.tree.column("Extra", width=200)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 双击条目编辑 extra
        self.tree.bind("<Double-1>", self.edit_extra)

        # 底部操作区
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(fill=tk.X, padx=5, pady=(0, 5))

        # 输入框（内容 + extra）
        tk.Label(bottom_frame, text="内容:", font=("Arial", 11)).grid(row=0, column=0, sticky="e", padx=(0, 2))
        self.content_var = tk.StringVar()
        content_entry = tk.Entry(bottom_frame, textvariable=self.content_var, font=("Arial", 11), width=30)
        content_entry.grid(row=0, column=1, padx=2, pady=2)
        content_entry.bind("<Return>", lambda e: self.insert_entry())

        tk.Label(bottom_frame, text="额外属性:", font=("Arial", 11)).grid(row=0, column=2, sticky="e", padx=(10, 2))
        self.extra_var = tk.StringVar()
        extra_entry = tk.Entry(bottom_frame, textvariable=self.extra_var, font=("Arial", 11), width=20)
        extra_entry.grid(row=0, column=3, padx=2, pady=2)
        extra_entry.bind("<Return>", lambda e: self.insert_entry())

        insert_btn = tk.Button(bottom_frame, text="插入", command=self.insert_entry,
                               font=("Arial", 11), width=8)
        insert_btn.grid(row=0, column=4, padx=5)

        delete_btn = tk.Button(bottom_frame, text="删除选中", command=self.delete_selected,
                               font=("Arial", 11), width=8)
        delete_btn.grid(row=0, column=5, padx=5)

        # 删除快捷键
        self.tree.bind("<Delete>", lambda e: self.delete_selected())
        self.tree.bind("<BackSpace>", lambda e: self.delete_selected())

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    # ---------- 数据库操作 ----------
    def create_database(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")],
            title="新建数据库文件"
        )
        if not file_path:
            return
        if os.path.exists(file_path):
            if not messagebox.askyesno("覆盖确认", "文件已存在，是否覆盖？"):
                return
        try:
            conn = sqlite3.connect(file_path)
            conn.execute("CREATE TABLE IF NOT EXISTS entries (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT NOT NULL, extra TEXT DEFAULT '')")
            conn.commit()
            conn.close()
            messagebox.showinfo("成功", f"数据库已创建：{file_path}")
            self.open_specific_db(file_path)
        except Exception as e:
            messagebox.showerror("创建失败", str(e))

    def open_database(self):
        file_path = filedialog.askopenfilename(
            defaultextension=".db",
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")],
            title="选择数据库文件"
        )
        if file_path:
            self.open_specific_db(file_path)

    def open_specific_db(self, path):
        if self.conn:
            self.conn.close()
        try:
            self.conn = sqlite3.connect(path)
            # 确保表及列存在
            self.conn.execute("CREATE TABLE IF NOT EXISTS entries (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT NOT NULL, extra TEXT DEFAULT '')")
            # 兼容旧表
            cursor = self.conn.execute("PRAGMA table_info(entries)")
            columns = [col[1] for col in cursor]
            if 'extra' not in columns:
                self.conn.execute("ALTER TABLE entries ADD COLUMN extra TEXT DEFAULT ''")
            self.conn.commit()
            self.db_path = path
            self.status_var.set(f"当前数据库：{os.path.basename(path)}  ({path})")
            self.refresh_list()
        except Exception as e:
            messagebox.showerror("打开数据库失败", str(e))
            self.conn = None
            self.db_path = None

    def insert_entry(self):
        if not self.conn:
            messagebox.showwarning("未打开数据库", "请先创建或打开一个数据库")
            return
        content = self.content_var.get().strip()
        if not content:
            messagebox.showwarning("内容为空", "请输入内容")
            return
        extra = self.extra_var.get().strip()
        try:
            self.conn.execute("INSERT INTO entries (content, extra) VALUES (?, ?)", (content, extra))
            self.conn.commit()
            self.content_var.set("")
            self.extra_var.set("")
            self.refresh_list()
        except Exception as e:
            messagebox.showerror("插入失败", str(e))

    def delete_selected(self):
        if not self.conn:
            return
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("未选中", "请先选中要删除的条目")
            return
        item = self.tree.item(selected[0])
        entry_id = item['values'][0]  # ID 是第一列
        try:
            self.conn.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
            self.conn.commit()
            self.refresh_list()
        except Exception as e:
            messagebox.showerror("删除失败", str(e))

    def edit_extra(self, event):
        """双击条目编辑 extra 属性"""
        if not self.conn:
            return
        selected = self.tree.selection()
        if not selected:
            return
        item = self.tree.item(selected[0])
        entry_id = item['values'][0]
        current_extra = item['values'][2] if len(item['values']) > 2 else ""

        new_extra = simpledialog.askstring("编辑额外属性", f"为条目 {entry_id} 输入新属性值:",
                                           initialvalue=current_extra)
        if new_extra is not None:
            try:
                self.conn.execute("UPDATE entries SET extra = ? WHERE id = ?", (new_extra.strip(), entry_id))
                self.conn.commit()
                self.refresh_list()
            except Exception as e:
                messagebox.showerror("更新失败", str(e))

    def refresh_list(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        if not self.conn:
            return
        try:
            cursor = self.conn.execute("SELECT id, content, extra FROM entries ORDER BY id")
            for row in cursor:
                self.tree.insert("", tk.END, values=(row[0], row[1], row[2] if row[2] else ""))
        except Exception as e:
            messagebox.showerror("读取失败", str(e))

    def on_close(self):
        if self.conn:
            self.conn.close()
        self.root.destroy()

if __name__ == "__main__":
    DBManagerApp()