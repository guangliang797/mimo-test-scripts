"""
音频播放器模块 - 阶段3 步骤3.1
TDD第二步：写最少代码让测试通过
"""
import pygame
import os
from typing import Optional


class Player:
    """
    音频播放器
    
    功能：
    - 加载音频文件
    - 播放/暂停/恢复/停止
    - 单曲循环
    """

    def __init__(self):
        """初始化播放器"""
        pygame.mixer.init()
        self._current_file: Optional[str] = None
        self._is_playing = False
        self._is_paused = False
        self._is_looping = False

    def load(self, filepath: str) -> bool:
        """
        加载音频文件
        
        Args:
            filepath: 音频文件路径
            
        Returns:
            是否加载成功
        """
        if not os.path.exists(filepath):
            return False
        
        try:
            # 如果正在播放，先停止
            if self._is_playing:
                pygame.mixer.music.stop()
            
            pygame.mixer.music.load(filepath)
            self._current_file = filepath
            self._is_playing = False
            self._is_paused = False
            return True
        except Exception as e:
            print(f"加载失败: {e}")
            return False

    def play(self) -> None:
        """播放音频"""
        if self._current_file is None:
            return
        
        if self._is_paused:
            # 从暂停恢复
            pygame.mixer.music.unpause()
            self._is_paused = False
            self._is_playing = True
        else:
            # 从头播放
            loops = -1 if self._is_looping else 0
            pygame.mixer.music.play(loops=loops)
            self._is_playing = True
            self._is_paused = False

    def pause(self) -> None:
        """暂停播放"""
        if self._is_playing and not self._is_paused:
            pygame.mixer.music.pause()
            self._is_paused = True
            self._is_playing = False

    def resume(self) -> None:
        """恢复播放"""
        if self._is_paused:
            pygame.mixer.music.unpause()
            self._is_paused = False
            self._is_playing = True

    def stop(self) -> None:
        """停止播放"""
        pygame.mixer.music.stop()
        self._is_playing = False
        self._is_paused = False

    def set_loop(self, enabled: bool) -> None:
        """
        设置循环模式
        
        Args:
            enabled: True开启循环，False关闭
        """
        self._is_looping = enabled
        
        # 如果正在播放，重新设置循环
        if self._is_playing:
            loops = -1 if enabled else 0
            # 获取当前播放位置
            pos = pygame.mixer.music.get_pos()
            pygame.mixer.music.play(loops=loops, start=pos / 1000.0)

    @property
    def is_playing(self) -> bool:
        """是否正在播放"""
        # 检查pygame的实际状态
        if pygame.mixer.music.get_busy():
            self._is_playing = True
            self._is_paused = False
        return self._is_playing

    @property
    def is_paused(self) -> bool:
        """是否暂停"""
        return self._is_paused

    @property
    def is_looping(self) -> bool:
        """是否循环模式"""
        return self._is_looping

    def cleanup(self) -> None:
        """清理资源"""
        self.stop()
        pygame.mixer.quit()

    def __del__(self):
        """析构时清理"""
        try:
            self.cleanup()
        except Exception:
            pass
