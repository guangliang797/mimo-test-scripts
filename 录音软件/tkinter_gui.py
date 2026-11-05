"""
录音软件 - Tkinter图形界面
阶段6：UI集成
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
import threading
from controller import AppController


class RecorderGUI:
    """录音软件图形界面"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("录音管理工具")
        self.root.geometry("700x500")
        self.root.resizable(True, True)

        # 控制器
        save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recordings")
        self.controller = AppController(save_dir=save_dir)

        # 播放器状态
        self._player = None
        self._is_playing = False
        self._is_looping = False
        self._is_recording = False
        self._recorder = None

        self._build_ui()
        self._refresh_list()

    def _build_ui(self):
        """构建界面"""
        # ===== 顶部：录音列表 =====
        list_frame = ttk.Frame(self.root, padding=5)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # 表格
        columns = ("index", "title", "duration", "size", "date")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("index", text="序号")
        self.tree.heading("title", text="标题")
        self.tree.heading("duration", text="时长")
        self.tree.heading("size", text="大小")
        self.tree.heading("date", text="日期")

        self.tree.column("index", width=50, anchor=tk.CENTER)
        self.tree.column("title", width=250, anchor=tk.W)
        self.tree.column("duration", width=80, anchor=tk.CENTER)
        self.tree.column("size", width=100, anchor=tk.CENTER)
        self.tree.column("date", width=100, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 双击播放
        self.tree.bind("<Double-1>", lambda e: self._play_selected())

        # ===== 底部：控制按钮 =====
        btn_frame = ttk.Frame(self.root, padding=5)
        btn_frame.pack(fill=tk.X)

        # 播放控制
        play_frame = ttk.LabelFrame(btn_frame, text="播放控制", padding=5)
        play_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.btn_play = ttk.Button(play_frame, text="▶ 播放", command=self._play_selected)
        self.btn_play.pack(side=tk.LEFT, padx=2)

        self.btn_stop = ttk.Button(play_frame, text="⏹ 停止", command=self._stop_playback)
        self.btn_stop.pack(side=tk.LEFT, padx=2)

        self.btn_loop = ttk.Button(play_frame, text="🔁 循环: 关", command=self._toggle_loop)
        self.btn_loop.pack(side=tk.LEFT, padx=2)

        # 录音控制
        rec_frame = ttk.LabelFrame(btn_frame, text="录音", padding=5)
        rec_frame.pack(side=tk.LEFT, padx=10)

        self.btn_record = ttk.Button(rec_frame, text="⏺ 开始录音", command=self._toggle_recording)
        self.btn_record.pack(side=tk.LEFT, padx=2)

        # 管理按钮
        mgmt_frame = ttk.LabelFrame(btn_frame, text="管理", padding=5)
        mgmt_frame.pack(side=tk.LEFT, padx=10)

        ttk.Button(mgmt_frame, text="✏ 重命名", command=self._rename_selected).pack(side=tk.LEFT, padx=2)
        ttk.Button(mgmt_frame, text="🗑 删除", command=self._delete_selected).pack(side=tk.LEFT, padx=2)

        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _refresh_list(self):
        """刷新录音列表"""
        # 清空
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 填充
        for item in self.controller.get_display_list():
            self.tree.insert("", tk.END, values=(
                item["index"],
                item["title"],
                item["duration"],
                item["size"],
                item["date"],
            ))

        count = self.controller.get_recording_count()
        self.status_var.set(f"共 {count} 条录音")

    def _get_selected_index(self):
        """获取选中的序号"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("提示", "请先选择一条录音")
            return None
        item = self.tree.item(selection[0])
        return item["values"][0]  # index

    def _play_selected(self):
        """播放选中的录音"""
        index = self._get_selected_index()
        if index is None:
            return

        filepath = self.controller.get_recording_filepath(index)
        if filepath is None:
            messagebox.showerror("错误", "录音文件不存在")
            return

        # 停止之前的播放
        self._stop_playback()

        # 启动播放线程
        self._is_playing = True
        self.status_var.set(f"正在播放: {self.controller.get_recording_at(index)['title']}")

        t = threading.Thread(target=self._play_thread, args=(filepath,), daemon=True)
        t.start()

    def _play_thread(self, filepath):
        """播放线程"""
        try:
            from player import Player
            self._player = Player()
            self._player.load(filepath)
            self._player.set_loop(self._is_looping)
            self._player.play()

            while self._is_playing and self._player.is_playing:
                import time
                time.sleep(0.1)

            if self._is_playing:
                self.root.after(0, lambda: self.status_var.set("播放完成"))
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"播放出错: {e}"))
        finally:
            self._is_playing = False
            if self._player:
                self._player.cleanup()
                self._player = None

    def _stop_playback(self):
        """停止播放"""
        self._is_playing = False
        if self._player:
            self._player.stop()
        self.status_var.set("已停止")

    def _toggle_loop(self):
        """切换循环"""
        self._is_looping = not self._is_looping
        self.btn_loop.config(text=f"🔁 循环: {'开' if self._is_looping else '关'}")

        if self._player and self._is_playing:
            self._player.set_loop(self._is_looping)

    def _toggle_recording(self):
        """切换录音状态"""
        if not self._is_recording:
            self._start_recording()
        else:
            self._stop_recording()

    def _start_recording(self):
        """开始录音"""
        from recorder import Recorder

        self._recorder = Recorder()
        self._recorder.start()
        self._is_recording = True
        self.btn_record.config(text="⏹ 停止录音")
        self.status_var.set("录音中... 再次点击停止")

    def _stop_recording(self):
        """停止录音"""
        if self._recorder is None:
            return

        result = self._recorder.stop()
        self._is_recording = False
        self.btn_record.config(text="⏺ 开始录音")

        if result["success"]:
            # 添加到存储
            self.controller.storage.add({
                "id": result["id"],
                "title": result["title"],
                "filename": result["filename"],
                "created_at": result["created_at"],
                "duration_seconds": result["duration_seconds"],
                "file_size_bytes": result["file_size_bytes"],
            })
            self._refresh_list()
            self.status_var.set(f"录音已保存: {result['title']}")
        else:
            messagebox.showerror("录音失败", result.get("message", "未知错误"))
            self.status_var.set("录音失败")

        self._recorder = None

    def _rename_selected(self):
        """重命名选中的录音"""
        index = self._get_selected_index()
        if index is None:
            return

        current = self.controller.get_recording_at(index)
        new_title = simpledialog.askstring(
            "重命名",
            f"当前标题: {current['title']}\n请输入新标题:",
            initialvalue=current["title"]
        )

        if new_title is not None:
            result = self.controller.rename_recording(index, new_title)
            if result["success"]:
                self._refresh_list()
                self.status_var.set(result["message"])
            else:
                messagebox.showerror("重命名失败", result["message"])

    def _delete_selected(self):
        """删除选中的录音"""
        index = self._get_selected_index()
        if index is None:
            return

        rec = self.controller.get_recording_at(index)
        if messagebox.askyesno("确认删除", f"确定要删除「{rec['title']}」吗？"):
            result = self.controller.delete_recording(index)
            if result["success"]:
                self._refresh_list()
                self.status_var.set(result["message"])
            else:
                messagebox.showerror("删除失败", result["message"])

    def run(self):
        """启动界面"""
        self.root.mainloop()


if __name__ == "__main__":
    app = RecorderGUI()
    app.run()
