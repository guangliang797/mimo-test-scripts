"""
播放功能测试 - 阶段3 步骤3.1
TDD第一步：先写测试，确认测试会失败
"""
import unittest
import os
import tempfile
import shutil
import time
from player import Player


class TestPlayerBasic(unittest.TestCase):
    """播放器基础功能测试"""

    def setUp(self):
        """每个测试前执行：创建临时目录和测试文件"""
        self.test_dir = tempfile.mkdtemp()
        self.player = Player()
        
        # 创建一个测试音频文件（使用已有的录音）
        self.test_audio = r"D:\03_开发APP\录音软件\recordings\录音_20260926_142529.wav"
        if not os.path.exists(self.test_audio):
            self.skipTest("测试音频文件不存在")

    def tearDown(self):
        """每个测试后执行：清理"""
        self.player.stop()
        self.player.cleanup()

    def test_can_load_audio(self):
        """测试：可以加载音频文件"""
        result = self.player.load(self.test_audio)
        self.assertTrue(result)

    def test_can_play_audio(self):
        """测试：可以播放音频"""
        self.player.load(self.test_audio)
        self.player.play()
        
        # 应该正在播放
        self.assertTrue(self.player.is_playing)
        
        # 播放一小段时间
        time.sleep(0.5)
        
        self.player.stop()

    def test_can_pause_audio(self):
        """测试：可以暂停音频"""
        self.player.load(self.test_audio)
        self.player.play()
        time.sleep(0.3)
        
        self.player.pause()
        
        # 应该暂停了
        self.assertFalse(self.player.is_playing)
        self.assertTrue(self.player.is_paused)

    def test_can_resume_after_pause(self):
        """测试：暂停后可以恢复播放"""
        self.player.load(self.test_audio)
        self.player.play()
        time.sleep(0.3)
        
        self.player.pause()
        time.sleep(0.2)
        
        self.player.resume()
        
        # 应该继续播放
        self.assertTrue(self.player.is_playing)

    def test_can_stop_audio(self):
        """测试：可以停止音频"""
        self.player.load(self.test_audio)
        self.player.play()
        time.sleep(0.3)
        
        self.player.stop()
        
        # 应该停止了
        self.assertFalse(self.player.is_playing)
        self.assertFalse(self.player.is_paused)


class TestPlayerSwitch(unittest.TestCase):
    """播放器切换功能测试"""

    def setUp(self):
        self.player = Player()
        self.test_audio = r"D:\03_开发APP\录音软件\recordings\录音_20260926_142529.wav"
        if not os.path.exists(self.test_audio):
            self.skipTest("测试音频文件不存在")

    def tearDown(self):
        self.player.stop()
        self.player.cleanup()

    def test_can_switch_audio(self):
        """测试：可以切换音频"""
        # 加载第一个音频
        self.player.load(self.test_audio)
        self.player.play()
        time.sleep(0.3)
        
        # 切换到同一个音频（模拟切换）
        self.player.load(self.test_audio)
        
        # 应该可以正常播放
        self.player.play()
        self.assertTrue(self.player.is_playing)


class TestPlayerLoop(unittest.TestCase):
    """播放器循环功能测试"""

    def setUp(self):
        self.player = Player()
        self.test_audio = r"D:\03_开发APP\录音软件\recordings\录音_20260926_142529.wav"
        if not os.path.exists(self.test_audio):
            self.skipTest("测试音频文件不存在")

    def tearDown(self):
        self.player.stop()
        self.player.cleanup()

    def test_can_set_loop(self):
        """测试：可以设置循环模式"""
        self.player.set_loop(True)
        self.assertTrue(self.player.is_looping)
        
        self.player.set_loop(False)
        self.assertFalse(self.player.is_looping)

    def test_loop_enabled_auto_replay(self):
        """测试：循环开启时播完自动重播"""
        self.player.set_loop(True)
        self.player.load(self.test_audio)
        self.player.play()
        
        # 循环应该在播放结束后自动重播
        # 这里只测试设置是否正确
        self.assertTrue(self.player.is_looping)


if __name__ == '__main__':
    unittest.main()
