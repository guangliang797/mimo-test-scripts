"""
录音存储模块 - 阶段2 重构版
改进：添加类型提示、错误处理、文档字符串
"""
import json
import os
from typing import List, Dict, Optional
from datetime import datetime


class Storage:
    """
    录音存储管理
    
    功能：
    - 添加录音记录
    - 获取所有录音记录
    - 删除录音记录
    - 持久化到JSON文件
    
    用法：
        storage = Storage(save_dir="./recordings")
        storage.add(recording_dict)
        all_recordings = storage.get_all()
        storage.delete(recording_id)
    """

    JSON_FILENAME = "recordings.json"

    def __init__(self, save_dir: str):
        """
        初始化存储
        
        Args:
            save_dir: 录音保存目录
            
        Raises:
            ValueError: 如果save_dir为空
        """
        if not save_dir:
            raise ValueError("save_dir不能为空")
            
        self.save_dir = save_dir
        self.json_path = os.path.join(save_dir, self.JSON_FILENAME)
        self._recordings: List[Dict] = []
        
        # 确保目录存在
        os.makedirs(save_dir, exist_ok=True)
        
        # 加载已有数据
        self._load()

    def _load(self) -> None:
        """从JSON文件加载数据"""
        if not os.path.exists(self.json_path):
            return
            
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    self._recordings = data.get("recordings", [])
                else:
                    self._recordings = []
        except json.JSONDecodeError as e:
            print(f"警告: JSON文件损坏，将创建新文件 ({e})")
            self._recordings = []
        except IOError as e:
            print(f"警告: 无法读取JSON文件 ({e})")
            self._recordings = []

    def _save(self) -> None:
        """
        保存数据到JSON文件
        
        使用临时文件确保写入原子性
        """
        temp_path = self.json_path + ".tmp"
        data = {"recordings": self._recordings, "updated_at": datetime.now().isoformat()}
        
        try:
            # 先写入临时文件
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 原子替换
            if os.path.exists(self.json_path):
                os.replace(temp_path, self.json_path)
            else:
                os.rename(temp_path, self.json_path)
        except IOError as e:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise IOError(f"保存失败: {e}")

    def add(self, recording: Dict) -> None:
        """
        添加录音记录
        
        Args:
            recording: 录音记录字典，必须包含id字段
            
        Raises:
            ValueError: 如果recording缺少id字段
        """
        if not recording or "id" not in recording:
            raise ValueError("录音记录必须包含id字段")
            
        self._recordings.append(recording)
        self._save()

    def get_all(self) -> List[Dict]:
        """
        获取所有录音记录
        
        Returns:
            录音记录列表（按创建时间倒序）
        """
        # 按创建时间倒序排列
        sorted_recordings = sorted(
            self._recordings,
            key=lambda x: x.get("created_at", ""),
            reverse=True
        )
        return sorted_recordings

    def get_by_id(self, recording_id: str) -> Optional[Dict]:
        """
        根据ID获取录音记录
        
        Args:
            recording_id: 录音ID
            
        Returns:
            录音记录，不存在则返回None
        """
        for recording in self._recordings:
            if recording.get("id") == recording_id:
                return recording
        return None

    def delete(self, recording_id: str) -> bool:
        """
        删除录音记录
        
        Args:
            recording_id: 录音ID
            
        Returns:
            是否删除成功
        """
        original_count = len(self._recordings)
        self._recordings = [r for r in self._recordings if r.get("id") != recording_id]
        
        if len(self._recordings) < original_count:
            self._save()
            return True
        return False

    def update(self, recording_id: str, updates: Dict) -> bool:
        """
        更新录音记录

        Args:
            recording_id: 录音ID
            updates: 要更新的字段

        Returns:
            是否更新成功
        """
        # 验证标题不为空
        if "title" in updates:
            title = updates["title"]
            if not title or not title.strip():
                return False
        
        for recording in self._recordings:
            if recording.get("id") == recording_id:
                recording.update(updates)
                self._save()
                return True
        return False

    @property
    def count(self) -> int:
        """录音记录数量"""
        return len(self._recordings)
