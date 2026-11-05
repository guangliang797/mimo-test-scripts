"""
录音应用控制器 - 阶段6
连接UI和底层模块（Storage/Recorder/Player）
所有方法返回数据而非print，方便UI和测试共用
"""
import os
from storage import Storage


class AppController:
    """
    录音应用控制器

    职责：
    - 管理录音列表的增删改查
    - 提供UI展示所需的数据格式
    - 不依赖任何UI框架（Tkinter/CLI均可对接）
    """

    def __init__(self, save_dir: str):
        self.storage = Storage(save_dir=save_dir)
        self._recorder = None
        self._player = None

    def get_recordings(self):
        """获取录音列表（按时间倒序）"""
        return self.storage.get_all()

    def get_recording_count(self):
        """获取录音数量"""
        return self.storage.count

    def get_recording_at(self, index: int):
        """获取指定序号的录音（1-based）"""
        recordings = self.storage.get_all()
        if index < 1 or index > len(recordings):
            return None
        return recordings[index - 1]

    def get_recording_filepath(self, index: int):
        """获取指定序号录音的完整文件路径"""
        rec = self.get_recording_at(index)
        if rec is None:
            return None
        filepath = os.path.join(self.storage.save_dir, rec.get("filename", ""))
        if not os.path.exists(filepath):
            return None
        return filepath

    def delete_recording(self, index: int) -> dict:
        """
        删除指定序号录音
        Returns: {"success": bool, "message": str}
        """
        rec = self.get_recording_at(index)
        if rec is None:
            return {"success": False, "message": f"序号 {index} 不存在"}

        filepath = os.path.join(self.storage.save_dir, rec.get("filename", ""))

        # 删除文件
        if os.path.exists(filepath):
            os.remove(filepath)

        # 删除记录
        self.storage.delete(rec["id"])
        return {"success": True, "message": f"已删除: {rec['title']}"}

    def rename_recording(self, index: int, new_title: str) -> dict:
        """
        重命名指定序号录音
        Returns: {"success": bool, "message": str}
        """
        if not new_title or not new_title.strip():
            return {"success": False, "message": "标题不能为空"}

        rec = self.get_recording_at(index)
        if rec is None:
            return {"success": False, "message": f"序号 {index} 不存在"}

        result = self.storage.update(rec["id"], {"title": new_title.strip()})
        if result:
            return {"success": True, "message": f"已重命名为: {new_title.strip()}"}
        return {"success": False, "message": "重命名失败"}

    def format_duration(self, seconds: float) -> str:
        """格式化时长"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}:{secs:02d}"

    def format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"

    def get_display_list(self):
        """
        获取用于UI展示的录音列表
        Returns: list of dict with display fields
        """
        recordings = self.storage.get_all()
        result = []
        for i, rec in enumerate(recordings, 1):
            result.append({
                "index": i,
                "title": rec.get("title", "未命名"),
                "duration": self.format_duration(rec.get("duration_seconds", 0)),
                "size": self.format_size(rec.get("file_size_bytes", 0)),
                "date": rec.get("created_at", "")[:10],
            })
        return result
