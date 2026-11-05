"""
麦克风测试和音量检测
帮助诊断录音清晰度问题
"""
import pyaudio
import numpy as np
import time

def check_audio_levels():
    """检测麦克风音量"""
    print("=" * 50)
    print("  麦克风音量检测")
    print("=" * 50)
    
    audio = pyaudio.PyAudio()
    
    # 打开音频流
    stream = audio.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=44100,
        input=True,
        frames_per_buffer=1024
    )
    
    print("\n请对着麦克风说话，检测音量...")
    print("（按Ctrl+C停止）\n")
    
    try:
        while True:
            # 读取音频数据
            data = stream.read(1024, exception_on_overflow=False)
            
            # 转换为numpy数组
            audio_data = np.frombuffer(data, dtype=np.int16)
            
            # 计算音量（RMS）
            volume = np.abs(audio_data).mean()
            
            # 音量条（用ASCII字符避免编码问题）
            bar_length = int(volume / 100)
            bar = "#" * bar_length + "-" * (50 - bar_length)
            
            # 判断音量级别
            if volume < 100:
                level = "[太小声]"
            elif volume < 500:
                level = "[正常]"
            elif volume < 2000:
                level = "[良好]"
            else:
                level = "[可能爆音]"
            
            print(f"\r音量: {bar} {volume:6.0f} {level}", end="", flush=True)
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n\n停止检测")
    
    stream.stop_stream()
    stream.close()
    audio.terminate()

if __name__ == "__main__":
    check_audio_levels()
