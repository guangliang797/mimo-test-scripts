"""
录音管理功能测试 - 阶段4 步骤4.1
TDD第一步：先写测试，确认测试会失败
"""
import unittest
import os
import tempfile
import shutil
import time
from storage import Storage


class TestStorageRename(unittest.TestCase):
    """存储重命名功能测试"""

    def setUp(self):
        """每个测试前执行：创建临时目录"""
        self.test_dir = tempfile.mkdtemp()
        self.storage = Storage(save_dir=self.test_dir)
        
        # 添加一条测试记录
        self.test_recording = {
            "id": "20260926_150000",
            "filename": "录音_20260926_150000.wav",
            "title": "原始标题",
            "created_at": "2026-09-26T15:00:00",
            "duration_seconds": 5,
            "file_size_bytes": 440000
        }
        self.storage.add(self.test_recording)

    def tearDown(self):
        """每个测试后执行：清理临时目录"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_can_rename_title(self):
        """测试：可以重命名标题"""
        # 重命名
        result = self.storage.update("20260926_150000", {"title": "新标题"})
        
        # 应该返回True
        self.assertTrue(result)
        
        # 获取记录，标题应该已更新
        recordings = self.storage.get_all()
        self.assertEqual(recordings[0]["title"], "新标题")
        
        # 文件名不应该改变
        self.assertEqual(recordings[0]["filename"], "录音_20260926_150000.wav")

    def test_rename_nonexistent_returns_false(self):
        """测试：重命名不存在的记录返回False"""
        result = self.storage.update("不存在的ID", {"title": "新标题"})
        self.assertFalse(result)

    def test_rename_persists_after_reload(self):
        """测试：重命名后重新加载仍然有效"""
        # 重命名
        self.storage.update("20260926_150000", {"title": "持久化标题"})
        
        # 创建新的Storage实例（模拟重启）
        new_storage = Storage(save_dir=self.test_dir)
        
        # 标题应该已更新
        recordings = new_storage.get_all()
        self.assertEqual(recordings[0]["title"], "持久化标题")

    def test_rename_empty_title_rejected(self):
        """测试：空标题被拒绝"""
        result = self.storage.update("20260926_150000", {"title": ""})
        
        # 应该返回False或抛出异常
        # 这里我们选择返回False
        self.assertFalse(result)
        
        # 原标题应该不变
        recordings = self.storage.get_all()
        self.assertEqual(recordings[0]["title"], "原始标题")

    def test_rename_whitespace_title_rejected(self):
        """测试：纯空格标题被拒绝"""
        result = self.storage.update("20260926_150000", {"title": "   "})
        self.assertFalse(result)


class TestStorageGetById(unittest.TestCase):
    """存储按ID获取功能测试"""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.storage = Storage(save_dir=self.test_dir)
        
        # 添加多条测试记录
        for i in range(3):
            recording = {
                "id": f"20260926_15000{i}",
                "filename": f"录音_20260926_15000{i}.wav",
                "title": f"录音{i+1}",
                "created_at": f"2026-09-26T15:00:0{i}",
                "duration_seconds": i + 1,
                "file_size_bytes": (i + 1) * 100000
            }
            self.storage.add(recording)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_can_get_by_id(self):
        """测试：可以按ID获取记录"""
        recording = self.storage.get_by_id("20260926_150001")
        
        self.assertIsNotNone(recording)
        self.assertEqual(recording["title"], "录音2")

    def test_get_nonexistent_returns_none(self):
        """测试：获取不存在的记录返回None"""
        recording = self.storage.get_by_id("不存在的ID")
        self.assertIsNone(recording)


if __name__ == '__main__':
    unittest.main()
