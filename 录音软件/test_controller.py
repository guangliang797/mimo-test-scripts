"""
UI控制器测试 - 阶段6
测试GUI背后的控制逻辑（不依赖Tkinter窗口）
"""
import unittest
import os
import tempfile
import shutil

from controller import AppController
from storage import Storage


class TestControllerInit(unittest.TestCase):
    """控制器初始化测试"""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_controller_creates_storage(self):
        """测试：控制器初始化时创建Storage"""
        controller = AppController(save_dir=self.test_dir)
        self.assertIsNotNone(controller.storage)
        self.assertEqual(controller.get_recording_count(), 0)

    def test_controller_with_existing_data(self):
        """测试：控制器加载已有数据"""
        storage = Storage(save_dir=self.test_dir)
        storage.add({
            "id": "rec_001",
            "title": "测试录音",
            "filename": "录音_001.wav",
            "created_at": "2026-09-27T10:00:00",
            "duration_seconds": 30.0,
            "file_size_bytes": 1024,
        })

        controller = AppController(save_dir=self.test_dir)
        self.assertEqual(controller.get_recording_count(), 1)


class TestControllerRecordings(unittest.TestCase):
    """控制器录音列表测试"""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.controller = AppController(save_dir=self.test_dir)
        for i in range(5):
            self.controller.storage.add({
                "id": f"rec_{i:03d}",
                "title": f"录音_{i}",
                "filename": f"录音_{i:03d}.wav",
                "created_at": f"2026-09-{27 - i:02d}T10:00:00",
                "duration_seconds": 30.0 + i * 10,
                "file_size_bytes": 1024 * (i + 1),
            })

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_get_recordings_returns_all(self):
        """测试：获取全部录音"""
        recordings = self.controller.get_recordings()
        self.assertEqual(len(recordings), 5)

    def test_get_recording_at_valid_index(self):
        """测试：获取有效序号的录音"""
        rec = self.controller.get_recording_at(1)
        self.assertIsNotNone(rec)
        self.assertIn("id", rec)

    def test_get_recording_at_invalid_index(self):
        """测试：获取无效序号返回None"""
        self.assertIsNone(self.controller.get_recording_at(0))
        self.assertIsNone(self.controller.get_recording_at(6))
        self.assertIsNone(self.controller.get_recording_at(-1))

    def test_get_recording_filepath_exists(self):
        """测试：获取录音文件路径（文件不存在时返回None）"""
        result = self.controller.get_recording_filepath(1)
        self.assertIsNone(result)

    def test_get_recording_filepath_with_real_file(self):
        """测试：获取录音文件路径（文件存在时返回路径）"""
        filepath = os.path.join(self.test_dir, "录音_004.wav")
        with open(filepath, 'wb') as f:
            f.write(b'\x00' * 100)

        result = self.controller.get_recording_filepath(5)
        self.assertIsNotNone(result)
        self.assertTrue(result.endswith("录音_004.wav"))


class TestControllerDelete(unittest.TestCase):
    """控制器删除测试"""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.controller = AppController(save_dir=self.test_dir)
        filepath = os.path.join(self.test_dir, "录音_001.wav")
        with open(filepath, 'wb') as f:
            f.write(b'\x00' * 100)

        self.controller.storage.add({
            "id": "rec_001",
            "title": "待删除录音",
            "filename": "录音_001.wav",
            "created_at": "2026-09-27T10:00:00",
            "duration_seconds": 10.0,
            "file_size_bytes": 100,
        })

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_delete_success(self):
        """测试：删除成功"""
        result = self.controller.delete_recording(1)
        self.assertTrue(result["success"])
        self.assertEqual(self.controller.get_recording_count(), 0)
        filepath = os.path.join(self.test_dir, "录音_001.wav")
        self.assertFalse(os.path.exists(filepath))

    def test_delete_invalid_index(self):
        """测试：删除无效序号"""
        result = self.controller.delete_recording(99)
        self.assertFalse(result["success"])
        self.assertIn("不存在", result["message"])

    def test_delete_missing_file(self):
        """测试：删除记录但文件不存在时，只删记录不报错"""
        filepath = os.path.join(self.test_dir, "录音_001.wav")
        os.remove(filepath)

        result = self.controller.delete_recording(1)
        self.assertTrue(result["success"])
        self.assertEqual(self.controller.get_recording_count(), 0)


class TestControllerRename(unittest.TestCase):
    """控制器重命名测试"""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.controller = AppController(save_dir=self.test_dir)
        self.controller.storage.add({
            "id": "rec_001",
            "title": "旧标题",
            "filename": "录音_001.wav",
            "created_at": "2026-09-27T10:00:00",
            "duration_seconds": 10.0,
            "file_size_bytes": 100,
        })

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_rename_success(self):
        """测试：重命名成功"""
        result = self.controller.rename_recording(1, "新标题")
        self.assertTrue(result["success"])
        rec = self.controller.get_recording_at(1)
        self.assertEqual(rec["title"], "新标题")

    def test_rename_empty_title(self):
        """测试：空标题拒绝"""
        result = self.controller.rename_recording(1, "")
        self.assertFalse(result["success"])

    def test_rename_whitespace_title(self):
        """测试：纯空格标题拒绝"""
        result = self.controller.rename_recording(1, "   ")
        self.assertFalse(result["success"])

    def test_rename_invalid_index(self):
        """测试：无效序号"""
        result = self.controller.rename_recording(99, "新标题")
        self.assertFalse(result["success"])


class TestControllerDisplay(unittest.TestCase):
    """控制器UI展示数据测试"""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.controller = AppController(save_dir=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_display_list_empty(self):
        """测试：空列表展示"""
        result = self.controller.get_display_list()
        self.assertEqual(result, [])

    def test_display_list_with_data(self):
        """测试：有数据时展示格式正确"""
        self.controller.storage.add({
            "id": "rec_001",
            "title": "测试录音",
            "filename": "录音_001.wav",
            "created_at": "2026-09-27T10:30:00",
            "duration_seconds": 95.5,
            "file_size_bytes": 1536 * 1024,
        })

        result = self.controller.get_display_list()
        self.assertEqual(len(result), 1)

        item = result[0]
        self.assertEqual(item["index"], 1)
        self.assertEqual(item["title"], "测试录音")
        self.assertEqual(item["duration"], "1:35")
        self.assertEqual(item["size"], "1.5 MB")
        self.assertEqual(item["date"], "2026-09-27")

    def test_format_duration_edge_cases(self):
        """测试：时长格式化边界情况"""
        self.assertEqual(self.controller.format_duration(0), "0:00")
        self.assertEqual(self.controller.format_duration(59), "0:59")
        self.assertEqual(self.controller.format_duration(60), "1:00")
        self.assertEqual(self.controller.format_duration(3661), "61:01")

    def test_format_size_edge_cases(self):
        """测试：文件大小格式化边界情况"""
        self.assertEqual(self.controller.format_size(0), "0 B")
        self.assertEqual(self.controller.format_size(500), "500 B")
        self.assertEqual(self.controller.format_size(1024), "1.0 KB")
        self.assertEqual(self.controller.format_size(1024 * 1024), "1.0 MB")


if __name__ == '__main__':
    unittest.main()
