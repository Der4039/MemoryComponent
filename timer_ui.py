# timer_ui.py
import tkinter as tk

class TimerUI:
    """纯显示界面，增加查看 extra 属性的按钮"""

    def __init__(self, root,
                 on_select_db=None,
                 on_toggle=None,
                 on_set_length=None,
                 on_show_extra=None):          # 新增回调
        self.root = root
        self.root.title("桌面计时器 + 随机提醒")
        self.root.geometry("360x480")          # 高度增加以容纳按钮
        self.root.resizable(False, False)

        self.on_select_db = on_select_db
        self.on_toggle = on_toggle
        self.on_set_length = on_set_length
        self.on_show_extra = on_show_extra    # 存储回调

        # ---- 创建所有控件（同上，最后添加按钮） ----
        self.label = tk.Label(root, text="10", font=("Arial", 72, "bold"))
        self.label.pack(expand=False, pady=(10, 5))

        self.hint_text = tk.StringVar(value="每10秒响铃一次")
        tk.Label(root, textvariable=self.hint_text,
                 font=("Arial", 12)).pack(pady=(0, 5))

        self.cycle_label = tk.Label(root, text="已完成周期：0",
                                    font=("Arial", 12, "bold"), fg="#555555")
        self.cycle_label.pack(pady=(0, 10))

        self.message_var = tk.StringVar(value="未载入数据库，将只播放提示音")
        tk.Label(root, textvariable=self.message_var,
                 font=("Arial", 14, "italic"), wraplength=320,
                 justify="center", fg="#007acc", height=3).pack(pady=(0, 10))

        # 数据库状态与选择按钮
        db_frame = tk.Frame(root)
        db_frame.pack(pady=(0, 5), fill=tk.X, padx=10)

        self.db_status_var = tk.StringVar(value="数据库：未选择")
        tk.Label(db_frame, textvariable=self.db_status_var,
                 font=("Arial", 9), anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.select_db_btn = tk.Button(db_frame, text="选择数据库",
                                       font=("Arial", 9), width=10,
                                       command=self._on_select_db)
        self.select_db_btn.pack(side=tk.RIGHT)

        # 开始 / 暂停按钮
        self.toggle_button = tk.Button(root, text="开始", font=("Arial", 12),
                                       command=self._on_toggle)
        self.toggle_button.pack(pady=(5, 5))

        # 时长设置
        setting_frame = tk.Frame(root)
        setting_frame.pack(pady=(0, 10))

        tk.Label(setting_frame, text="循环时长(秒):", font=("Arial", 12)).pack(side=tk.LEFT)

        self.length_var = tk.StringVar(value="10")
        self.length_entry = tk.Spinbox(setting_frame, from_=1, to=9999,
                                       textvariable=self.length_var,
                                       width=5, font=("Arial", 12), justify="center")
        self.length_entry.pack(side=tk.LEFT, padx=5)

        self.set_btn = tk.Button(setting_frame, text="设置", font=("Arial", 12),
                                 command=self._on_set_length)
        self.set_btn.pack(side=tk.LEFT)

        # ---- 新增“查看属性”按钮 ----
        self.show_extra_btn = tk.Button(root, text="查看当前属性",
                                        font=("Arial", 11),
                                        command=self._on_show_extra)
        self.show_extra_btn.pack(pady=(5, 10))

    # ---- 内部回调转发 ----
    def _on_select_db(self):
        if self.on_select_db:
            self.on_select_db()

    def _on_toggle(self):
        if self.on_toggle:
            self.on_toggle()

    def _on_set_length(self):
        if self.on_set_length:
            try:
                new_len = int(self.length_var.get())
            except ValueError:
                new_len = None
            self.on_set_length(new_len)

    def _on_show_extra(self):
        if self.on_show_extra:
            self.on_show_extra()

    # ---- 视图更新方法（未变）----
    def set_counter(self, value: int):
        self.label.config(text=str(value))

    def set_cycle_count(self, cycles: int):
        self.cycle_label.config(text=f"已完成周期：{cycles}")

    def set_message(self, text: str):
        self.message_var.set(text)

    def set_db_status(self, text: str):
        self.db_status_var.set(text)

    def set_toggle_button_text(self, text: str):
        self.toggle_button.config(text=text)

    def set_hint_text(self, text: str):
        self.hint_text.set(text)

    def get_length_input(self) -> str:
        return self.length_var.get()