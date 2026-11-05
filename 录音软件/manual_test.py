"""
手动测试录音功能
运行后会录5秒，然后保存并播放
"""
import time
import pygame
from recorder import Recorder

def main():
    print("=" * 50)
    print("  录音功能手动测试")
    print("=" * 50)
    
    # 初始化录音器
    recorder = Recorder()
    print(f"\n录音保存目录: {recorder.save_dir}")
    
    # 初始化播放器
    pygame.mixer.init()
    
    print("\n准备录音...")
    print("3...")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1...")
    time.sleep(1)
    
    # 开始录音
    print("\n🎤 开始录音（5秒）...")
    recorder.start()
    
    # 录制5秒
    for i in range(5, 0, -1):
        print(f"  剩余 {i} 秒...")
        time.sleep(1)
    
    # 停止录音
    print("\n⏹ 停止录音...")
    filepath = recorder.stop()
    
    if filepath:
        print(f"\n✅ 录音保存成功!")
        print(f"📁 文件: {filepath}")
        
        # 显示文件信息
        import os
        file_size = os.path.getsize(filepath)
        print(f"📊 大小: {file_size / 1024:.1f} KB")
        
        # 播放录音
        print("\n🔊 正在播放录音...")
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.play()
        
        # 等待播放完成
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        
        print("\n✅ 播放完成!")
        print("\n你可以去目录查看录音文件:")
        print(f"   {recorder.save_dir}")
    else:
        print("\n❌ 录音失败!")
    
    # 清理
    recorder.cleanup()
    pygame.mixer.quit()
    
    print("\n" + "=" * 50)
    input("按回车键退出...")

if __name__ == "__main__":
    main()
