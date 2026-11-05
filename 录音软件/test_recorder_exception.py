"""
录音功能测试 - 阶段1 步骤1.2
异常处理测试
"""
import unittest
import os
import tempfile
import shutil
import wave
from recorder import Recorder


class TestRecorderException(unittest.TestCase):
    """录音异常处理测试"""

    def setUp(self):
        """每个测试前执行：创建临时目录"""
        self.test_dir = tempfile.mkdtemp()
        self.recorder = Recorder(save_dir=self.test_dir)

    def tearDown(self):
        """每个测试后执行：清理"""
        self.recorder.cleanup()
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_stop_when_not_recording_returns_none(self):
        """测试：没在录音时调用stop()返回None"""
        result = self.recorder.stop()
        self.assertIsNone(result)

    def test_start_twice_raises_error(self):
        """测试：重复开始录音抛出异常"""
        self.recorder.start()
        with self.assertRaises(RuntimeError):
            self.recorder.start()
        self.recorder.stop()

    def test_recording_file_is_valid_wav(self):
        """测试：录音文件是有效的WAV格式"""
        self.recorder.start()
        import time
        time.sleep(0.5)
        filepath = self.recorder.stop()
        
        # 用wave模块验证文件
        with wave.open(filepath, 'rb') as wf:
            # 验证参数
            self.assertEqual(wf.getnchannels(), 1)  # 单声道
            self.assertEqual(wf.getframerate(), 44100)  # 44.1kHz
            self.assertGreater(wf.getnframes(), 0)  # 有数据

    def test_multiple_recordings_have_different_names(self):
        """测试：多次录音文件名不同"""
        import time
        
        # 第一次录音
        self.recorder.start()
        time.sleep(0.3)
        path1 = self.recorder.stop()
        
        # 等待1秒确保时间戳不同
        time.sleep(1)
        
        # 第二次录音
        self.recorder.start()
        time.sleep(0.3)
        path2 = self.recorder.stop()
        
        # 文件名应该不同
        self.assertNotEqual(path1, path2)


class TestRecorderCleanup(unittest.TestCase):
    """录音资源清理测试"""

    def test_cleanup_can_be_called_multiple_times(self):
        """测试：cleanup()可以多次调用不报错"""
        recorder = Recorder(save_dir=tempfile.mkdtemp())
        recorder.cleanup()
        recorder.cleanup()  # 第二次调用不应报错

    def test_cleanup_after_recording(self):
        """测试：录音后cleanup()正常"""
        test_dir = tempfile.mkdtemp()
        recorder = Recorder(save_dir=test_dir)
        recorder.start()
        import time
        time.sleep(0.3)
        recorder.stop()
        recorder.cleanup()  # 不应报错
        shutil.rmtree(test_dir, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
