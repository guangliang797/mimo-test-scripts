"""
录音模块 - 阶段1 重构版
改进：添加类型提示、文档字符串、错误处理
"""
import pyaudio
import wave
import os
import threading
from datetime import datetime
from typing import Optional


class Recorder:
    """
    录音器
    
    功能：
    - 开始/停止录音
    - 保存为WAV格式
    - 线程安全的录音循环
    
    用法：
        recorder = Recorder(save_dir="./recordings")
        recorder.start()
        # ... 录音中 ...
        filepath = recorder.stop()
    """

    # 常量
    SAMPLE_RATE = 44100  # 采样率
    CHANNELS = 1  # 单声道
    CHUNK_SIZE = 1024  # 每次读取的帧数
    FORMAT = pyaudio.paInt16  # 16位采样

    def __init__(self, save_dir: Optional[str] = None):
        """
        初始化录音器
        
        Args:
            save_dir: 录音保存目录，默认为脚本所在目录下的recordings文件夹
        """
        # 默认使用脚本所在目录，而不是当前工作目录
        if save_dir is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            save_dir = os.path.join(script_dir, "recordings")
        self.save_dir = save_dir
        
        self._is_recording = False
        self._audio = None
        self._stream: Optional[pyaudio.Stream] = None
        self._frames: list = []
        self._record_thread: Optional[threading.Thread] = None
        
        # 创建目录和初始化音频
        os.makedirs(self.save_dir, exist_ok=True)
        self._audio = pyaudio.PyAudio()

    @property
    def is_recording(self) -> bool:
        """是否正在录音"""
        return self._is_recording

    def _record_loop(self) -> None:
        """录音循环（在独立线程中运行）"""
        while self._is_recording:
            try:
                data = self._stream.read(self.CHUNK_SIZE, exception_on_overflow=False)
                self._frames.append(data)
            except OSError as e:
                # 音频输入溢出，继续录音
                continue
            except Exception as e:
                print(f"录音错误: {e}")
                break

    def start(self) -> None:
        """
        开始录音
        
        Raises:
            RuntimeError: 如果已经在录音
        """
        if self._is_recording:
            raise RuntimeError("已经在录音中")
        
        self._is_recording = True
        self._frames = []
        
        # 打开音频流
        self._stream = self._audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.SAMPLE_RATE,
            input=True,
            frames_per_buffer=self.CHUNK_SIZE
        )
        
        # 启动录音线程
        self._record_thread = threading.Thread(target=self._record_loop, daemon=True)
        self._record_thread.start()

    def stop(self) -> Optional[str]:
        """
        停止录音，保存为WAV文件
        
        Returns:
            录音文件路径，如果没在录音则返回None
        """
        if not self._is_recording:
            return None
        
        # 停止录音循环
        self._is_recording = False
        
        # 等待线程结束
        if self._record_thread and self._record_thread.is_alive():
            self._record_thread.join(timeout=1)
        
        # 停止并关闭流
        if self._stream:
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None
        
        # 生成文件路径
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"录音_{timestamp}.wav"
        filepath = os.path.join(self.save_dir, filename)
        
        # 保存WAV文件
        if self._frames:
            self._save_wav(filepath)
        
        return filepath

    def _save_wav(self, filepath: str) -> None:
        """保存录音数据为WAV文件"""
        with wave.open(filepath, 'wb') as wf:
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(self._audio.get_sample_size(self.FORMAT))
            wf.setframerate(self.SAMPLE_RATE)
            wf.writeframes(b''.join(self._frames))

    def cleanup(self) -> None:
        """清理资源"""
        self._is_recording = False
        if hasattr(self, '_stream') and self._stream:
            try:
                self._stream.stop_stream()
                self._stream.close()
            except Exception:
                pass
        if hasattr(self, '_audio') and self._audio:
            try:
                self._audio.terminate()
            except Exception:
                pass

    def __del__(self):
        """析构时清理资源"""
        self.cleanup()
