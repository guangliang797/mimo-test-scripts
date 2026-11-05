"""
录音功能测试 - 阶段1 步骤1.1
TDD第一步：先写测试，确认测试会失败
"""
import unittest
import os
import tempfile
import shutil
from recorder import Recorder


class TestRecorderBasic(unittest.TestCase):
    """录音基础功能测试"""

    def setUp(self):
        """每个测试前执行：创建临时目录"""
        self.test_dir = tempfile.mkdtemp()
        self.recorder = Recorder(save_dir=self.test_dir)

    def tearDown(self):
        """每个测试后执行：清理临时目录"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_can_start_recording(self):
        """测试：可以开始录音，状态变为录音中"""
        # 初始状态应该是空闲
        self.assertFalse(self.recorder.is_recording)
        
        # 开始录音
        self.recorder.start()
        
        # 状态应该变为录音中
        self.assertTrue(self.recorder.is_recording)
        
        # 停止录音（清理）
        self.recorder.stop()

    def test_can_stop_recording(self):
        """测试：可以停止录音，生成音频文件"""
        # 开始录音
        self.recorder.start()
        
        # 录制一小段时间
        import time
        time.sleep(0.5)
        
        # 停止录音
        output_path = self.recorder.stop()
        
        # 应该返回文件路径
        self.assertIsNotNone(output_path)
        
        # 文件应该存在
        self.assertTrue(os.path.exists(output_path))
        
        # 文件应该在指定目录
        self.assertTrue(output_path.startswith(self.test_dir))

    def test_recording_file_has_wav_extension(self):
        """测试：录音文件是WAV格式"""
        self.recorder.start()
        import time
        time.sleep(0.3)
        output_path = self.recorder.stop()
        
        # 文件扩展名应该是.wav
        self.assertTrue(output_path.endswith('.wav'))

    def test_recording_file_not_empty(self):
        """测试：录音文件不为空"""
        self.recorder.start()
        import time
        time.sleep(0.5)
        output_path = self.recorder.stop()
        
        # 文件大小应该大于0
        file_size = os.path.getsize(output_path)
        self.assertGreater(file_size, 0)


if __name__ == '__main__':
    unittest.main()
