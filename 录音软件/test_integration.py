"""
录音集成测试 - 阶段2 步骤2.2
测试Recorder和Storage的集成
"""
import unittest
import os
import tempfile
import shutil
import time
from recorder import Recorder
from storage import Storage


class TestRecorderStorageIntegration(unittest.TestCase):
    """录音器和存储集成测试"""

    def setUp(self):
        """每个测试前执行：创建临时目录"""
        self.test_dir = tempfile.mkdtemp()
        self.recorder = Recorder(save_dir=self.test_dir)
        self.storage = Storage(save_dir=self.test_dir)

    def tearDown(self):
        """每个测试后执行：清理"""
        self.recorder.cleanup()
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_recording_saved_to_storage(self):
        """测试：录音完成后自动保存到存储"""
        # 开始录音
        self.recorder.start()
        time.sleep(0.5)
        
        # 停止录音
        filepath = self.recorder.stop()
        
        # 提取录音信息并保存到存储
        if filepath:
            import wave
            with wave.open(filepath, 'rb') as wf:
                duration = wf.getnframes() / wf.getframerate()
            
            recording = {
                "id": os.path.splitext(os.path.basename(filepath))[0].replace("录音_", ""),
                "filename": os.path.basename(filepath),
                "title": os.path.basename(filepath).replace(".wav", ""),
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "duration_seconds": round(duration, 2),
                "file_size_bytes": os.path.getsize(filepath)
            }
            self.storage.add(recording)
        
        # 存储应该有一条记录
        recordings = self.storage.get_all()
        self.assertEqual(len(recordings), 1)
        
        # 记录的文件应该存在
        saved_file = os.path.join(self.test_dir, recordings[0]["filename"])
        self.assertTrue(os.path.exists(saved_file))

    def test_multiple_recordings_in_storage(self):
        """测试：多次录音都能保存到存储"""
        for i in range(3):
            self.recorder.start()
            time.sleep(0.3)
            filepath = self.recorder.stop()
            
            if filepath:
                import wave
                with wave.open(filepath, 'rb') as wf:
                    duration = wf.getnframes() / wf.getframerate()
                
                recording = {
                    "id": os.path.splitext(os.path.basename(filepath))[0].replace("录音_", ""),
                    "filename": os.path.basename(filepath),
                    "title": f"测试录音{i+1}",
                    "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "duration_seconds": round(duration, 2),
                    "file_size_bytes": os.path.getsize(filepath)
                }
                self.storage.add(recording)
            
            time.sleep(0.5)  # 确保时间戳不同
        
        # 存储应该有三条记录
        recordings = self.storage.get_all()
        self.assertEqual(len(recordings), 3)


class TestStorageFormatDuration(unittest.TestCase):
    """存储格式化工具测试"""

    def test_format_duration_seconds(self):
        """测试：格式化时长（秒）"""
        # 这个功能可以添加到Storage中
        duration = 65  # 65秒
        expected = "1:05"  # 1分5秒
        # 暂时跳过，后续实现

    def test_format_file_size(self):
        """测试：格式化文件大小"""
        size = 1024 * 1024  # 1MB
        expected = "1.0 MB"
        # 暂时跳过，后续实现


if __name__ == '__main__':
    unittest.main()
