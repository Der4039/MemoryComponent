# timer_app.py
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import subprocess
import os

from data_provider import DataProvider
from random_entry import get_random_entry
from timer_controller import TimerController
from timer_ui import TimerUI

class TimerApp:
    """主程序，处理 extra 属性的显示"""

    def __init__(self):
        self.root = tk.Tk()
        self.data = DataProvider()
        self.ui = None
        self.controller = None
        self.current_extra = ""       # 新增：保存当前条目的 extra 属性

        self.build_ui()
        self.init_controller()
        self.update_db_status()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    def build_ui(self):
        self.ui = TimerUI(
            self.root,
            on_select_db=self.select_database,
            on_toggle=self.toggle_timer,
            on_set_length=self.set_cycle_length,
            on_show_extra=self.show_current_extra   # 绑定新回调
        )

    def init_controller(self):
        def random_func():
            # 现在返回字典 {'content':..., 'extra':...} 或 None
            return get_random_entry(self.data.connection, self.data.entry_count)

        def on_update(cycles, counter, message, play_sound):
            self.ui.set_counter(counter)
            self.ui.set_cycle_count(cycles)

            if message is not None:
                # message 是字典，提取 content 和 extra
                content = message.get('content', '')
                extra = message.get('extra', '')
                self.ui.set_message(content)
                self.current_extra = extra          # 保存 extra
            else:
                # 没有新消息（普通计时中），保持当前显示不变
                pass

            if play_sound:
                self.play_sound()

        self.controller = TimerController(random_func, on_update)
        self.controller.set_scheduler(
            lambda delay, cb: self.root.after(delay, cb),
            lambda token: self.root.after_cancel(token)
        )

    def select_database(self):
        path = filedialog.askopenfilename(
            title="选择数据库文件",
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")]
        )
        if not path:
            return
        try:
            self.data.open_database(path)
            self.current_extra = ""          # 切换数据库时清空 extra
            self.update_db_status()
        except Exception as e:
            messagebox.showerror("数据库错误", f"无法打开数据库：{str(e)}")
            self.data.close()
            self.update_db_status()

    def toggle_timer(self):
        self.controller.toggle()
        if self.controller.running:
            self.ui.set_toggle_button_text("暂停")
        else:
            self.ui.set_toggle_button_text("开始")

    def set_cycle_length(self, length):
        if length is None or length < 1:
            messagebox.showerror("输入错误", "请输入一个大于0的整数")
            return
        self.controller.set_cycle_length(length)
        self.ui.set_hint_text(f"每{length}秒响铃一次")
        self.ui.set_counter(self.controller.counter)

    def show_current_extra(self):
        """显示当前条目的额外属性"""
        if self.current_extra:
            messagebox.showinfo("当前属性", self.current_extra)
        else:
            messagebox.showinfo("当前属性", "（无额外属性或尚未加载条目）")

    def update_db_status(self):
        if self.data.has_database():
            basename = os.path.basename(self.data.db_path)
            self.ui.set_db_status(f"数据库：{basename}")
            if self.data.has_entries():
                self.ui.set_message("数据库已就绪，点击“开始”运行")
            else:
                self.ui.set_message("数据库中暂无条目")
        else:
            self.ui.set_db_status("数据库：未选择")
            self.ui.set_message("未载入数据库，将只播放提示音")

    # ---------- 声音播放（不变）----------
    def play_sound(self):
        threading.Thread(target=self._play_sound_thread, daemon=True).start()

    def _play_sound_thread(self):
        try:
            sound_path = "/usr/share/sounds/freedesktop/stereo/complete.oga"
            if os.path.exists(sound_path):
                subprocess.run(["paplay", sound_path],
                               check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                subprocess.run(["canberra-gtk-play", "-i", "complete"],
                               check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            print('\a')

    def on_close(self):
        if self.controller:
            self.controller.pause()
        self.data.close()
        self.root.destroy()

if __name__ == "__main__":
    TimerApp()