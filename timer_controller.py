# timer_controller.py
class TimerController:
    """管理倒计时、周期计数、随机获取条目等核心逻辑，与 UI 解耦"""

    def __init__(self, get_random_func, on_update):
        """
        get_random_func: 无参函数，返回随机条目的字符串或 None
        on_update: 回调函数，签名为 on_update(cycles, counter, message, play_sound)
        """
        self._get_random = get_random_func
        self._on_update = on_update

        self.running = False
        self.cycle_length = 10
        self.counter = 10
        self.cycles = 0

        self._scheduler = None    # 用于安排下一次 tick：scheduler(delay_ms, callback)
        self._canceller = None    # 用于取消已安排的 tick：canceller(token)
        self._after_token = None

    def set_scheduler(self, schedule_func, cancel_func):
        """注入外部调度器（例如 tkinter 的 after / after_cancel）"""
        self._scheduler = schedule_func
        self._canceller = cancel_func

    def set_cycle_length(self, length: int):
        """更新周期时长，立即重置当前倒计时数字"""
        self.cycle_length = length
        self.counter = length
        self._notify_update()

    def start(self):
        """开始计时（如果尚未运行）"""
        if self.running:
            return
        self.running = True
        self._tick()

    def pause(self):
        """暂停计时"""
        self.running = False
        if self._after_token is not None and self._canceller:
            self._canceller(self._after_token)
            self._after_token = None

    def toggle(self):
        """切换开始/暂停"""
        if self.running:
            self.pause()
        else:
            self.start()

    def _tick(self):
        """每秒钟执行一次，更新倒计时并检查周期结束"""
        # 如果中途被暂停，立即终止
        if not self.running:
            self._after_token = None
            return

        self.counter -= 1
        if self.counter < 0:
            # 一个周期结束
            self.counter = self.cycle_length
            self.cycles += 1
            message = None
            if self._get_random:
                try:
                    message = self._get_random()
                except Exception:
                    message = None
            self._notify_update(message=message, play_sound=True)
        else:
            self._notify_update()

        # 安排下一秒（如果还在运行中）
        if self.running and self._scheduler:
            self._after_token = self._scheduler(1000, self._tick)

    def _notify_update(self, message=None, play_sound=False):
        """通过回调通知显示层更新"""
        if self._on_update:
            self._on_update(self.cycles, self.counter, message, play_sound)