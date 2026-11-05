"""
录音列表持久化测试 - 阶段2 步骤2.1
TDD第一步：先写测试，确认测试会失败
"""
import unittest
import os
import tempfile
import shutil
import json
import time
from recorder import Recorder
from storage import Storage


class TestStorageBasic(unittest.TestCase):
    """存储基础功能测试"""

    def setUp(self):
        """每个测试前执行：创建临时目录"""
        self.test_dir = tempfile.mkdtemp()
        self.storage = Storage(save_dir=self.test_dir)

    def tearDown(self):
        """每个测试后执行：清理临时目录"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_can_add_recording(self):
        """测试：可以添加录音记录到存储"""
        # 创建一条录音记录
        recording = {
            "id": "20260926_150000",
            "filename": "录音_20260926_150000.wav",
            "title": "测试录音",
            "created_at": "2026-09-26T15:00:00",
            "duration_seconds": 5,
            "file_size_bytes": 440000
        }
        
        # 添加到存储
        self.storage.add(recording)
        
        # 应该能获取到这条记录
        recordings = self.storage.get_all()
        self.assertEqual(len(recordings), 1)
        self.assertEqual(recordings[0]["id"], "20260926_150000")

    def test_can_get_all_recordings(self):
        """测试：可以获取所有录音记录"""
        # 添加多条记录
        for i in range(3):
            recording = {
                "id": f"20260926_15000{i}",
                "filename": f"录音_20260926_15000{i}.wav",
                "title": f"测试录音{i}",
                "created_at": f"2026-09-26T15:00:0{i}",
                "duration_seconds": i + 1,
                "file_size_bytes": (i + 1) * 100000
            }
            self.storage.add(recording)
        
        # 应该能获取所有记录
        recordings = self.storage.get_all()
        self.assertEqual(len(recordings), 3)

    def test_recordings_persist_after_reload(self):
        """测试：录音记录在重新加载后仍然存在"""
        # 添加一条记录
        recording = {
            "id": "20260926_150000",
            "filename": "录音_20260926_150000.wav",
            "title": "测试录音",
            "created_at": "2026-09-26T15:00:00",
            "duration_seconds": 5,
            "file_size_bytes": 440000
        }
        self.storage.add(recording)
        
        # 创建新的Storage实例（模拟重启）
        new_storage = Storage(save_dir=self.test_dir)
        
        # 应该能获取到之前的记录
        recordings = new_storage.get_all()
        self.assertEqual(len(recordings), 1)
        self.assertEqual(recordings[0]["title"], "测试录音")

    def test_json_file_created(self):
        """测试：添加记录后会创建JSON文件"""
        recording = {
            "id": "20260926_150000",
            "filename": "录音_20260926_150000.wav",
            "title": "测试录音",
            "created_at": "2026-09-26T15:00:00",
            "duration_seconds": 5,
            "file_size_bytes": 440000
        }
        self.storage.add(recording)
        
        # JSON文件应该存在
        json_path = os.path.join(self.test_dir, "recordings.json")
        self.assertTrue(os.path.exists(json_path))


class TestStorageDelete(unittest.TestCase):
    """存储删除功能测试"""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.storage = Storage(save_dir=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_can_delete_recording(self):
        """测试：可以删除录音记录"""
        # 添加一条记录
        recording = {
            "id": "20260926_150000",
            "filename": "录音_20260926_150000.wav",
            "title": "测试录音",
            "created_at": "2026-09-26T15:00:00",
            "duration_seconds": 5,
            "file_size_bytes": 440000
        }
        self.storage.add(recording)
        
        # 删除记录
        self.storage.delete("20260926_150000")
        
        # 应该获取不到这条记录
        recordings = self.storage.get_all()
        self.assertEqual(len(recordings), 0)


if __name__ == '__main__':
    unittest.main()
