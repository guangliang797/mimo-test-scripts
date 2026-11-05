"""
录音管理工具 - 命令行版（集成播放器）
功能：列表、播放（支持单曲循环）、删除录音
"""
import os
import sys
import time
from storage import Storage
from recorder import Recorder
from player import Player

# 默认录音目录
DEFAULT_SAVE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recordings")


def format_duration(seconds: float) -> str:
    """格式化时长"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}:{secs:02d}"


def format_size(size_bytes: int) -> str:
    """格式化文件大小"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def list_recordings(storage: Storage):
    """列出所有录音"""
    recordings = storage.get_all()
    
    if not recordings:
        print("\n  暂无录音记录")
        return []
    
    print("\n" + "=" * 70)
    print("  录音列表")
    print("=" * 70)
    print(f"  {'序号':<6} {'标题':<25} {'时长':<10} {'大小':<10} {'日期':<15}")
    print("-" * 70)
    
    for i, rec in enumerate(recordings, 1):
        title = rec.get("title", "未命名")[:22]
        duration = format_duration(rec.get("duration_seconds", 0))
        size = format_size(rec.get("file_size_bytes", 0))
        created = rec.get("created_at", "")[:10]
        
        print(f"  {i:<6} {title:<25} {duration:<10} {size:<10} {created:<15}")
    
    print("-" * 70)
    print(f"  共 {len(recordings)} 条录音")
    print()
    return recordings


def play_recording(storage: Storage, index: int, loop: bool = False):
    """播放指定序号的录音"""
    recordings = storage.get_all()
    
    if index < 1 or index > len(recordings):
        print(f"\n  错误：序号 {index} 不存在")
        return
    
    recording = recordings[index - 1]
    filepath = os.path.join(storage.save_dir, recording["filename"])
    
    if not os.path.exists(filepath):
        print(f"\n  错误：文件不存在 {filepath}")
        return
    
    player = Player()
    
    print(f"\n  正在播放: {recording['title']}")
    print(f"  时长: {format_duration(recording.get('duration_seconds', 0))}")
    print(f"  循环: {'开启' if loop else '关闭'}")
    print("  按 Ctrl+C 停止播放\n")
    
    try:
        player.load(filepath)
        player.set_loop(loop)
        player.play()
        
        while player.is_playing:
            time.sleep(0.1)
        
        print("\n  播放完成")
        
    except KeyboardInterrupt:
        player.stop()
        print("\n  已停止播放")
    finally:
        player.cleanup()


def delete_recording(storage: Storage, index: int):
    """删除指定序号的录音"""
    recordings = storage.get_all()
    
    if index < 1 or index > len(recordings):
        print(f"\n  错误：序号 {index} 不存在")
        return
    
    recording = recordings[index - 1]
    filepath = os.path.join(storage.save_dir, recording["filename"])
    
    # 确认删除
    print(f"\n  确定要删除以下录音吗？")
    print(f"  标题: {recording['title']}")
    print(f"  时长: {format_duration(recording.get('duration_seconds', 0))}")
    
    confirm = input("\n  输入 y 确认删除，其他键取消: ").strip().lower()
    
    if confirm != 'y':
        print("  已取消")
        return
    
    # 删除文件
    if os.path.exists(filepath):
        os.remove(filepath)
    
    # 删除记录
    storage.delete(recording["id"])
    
    print(f"\n  已删除: {recording['title']}")


def record_new(storage: Storage):
    """录制新录音"""
    recorder = Recorder(save_dir=storage.save_dir)
    
    print("\n  准备录音...")
    print("  按 Enter 开始录音，再按 Enter 停止")
    
    input()
    
    print("\n  录音中... 按 Enter 停止")
    recorder.start()
    
    input()
    
    filepath = recorder.stop()
    recorder.cleanup()
    
    if filepath:
        # 获取文件信息
        import wave
        with wave.open(filepath, 'rb') as wf:
            duration = wf.getnframes() / wf.getframerate()
        
        # 添加到存储
        recording = {
            "id": os.path.splitext(os.path.basename(filepath))[0].replace("录音_", ""),
            "filename": os.path.basename(filepath),
            "title": os.path.basename(filepath).replace(".wav", ""),
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "duration_seconds": round(duration, 2),
            "file_size_bytes": os.path.getsize(filepath)
        }
        storage.add(recording)
        
        print(f"\n  录音已保存: {recording['title']}")
        print(f"  时长: {format_duration(duration)}")
    else:
        print("\n  录音失败")


def rename_recording(storage: Storage, index: int):
    """重命名指定序号的录音"""
    recordings = storage.get_all()
    
    if index < 1 or index > len(recordings):
        print(f"\n  错误：序号 {index} 不存在")
        return
    
    recording = recordings[index - 1]
    
    print(f"\n  当前标题: {recording['title']}")
    new_title = input("  输入新标题（留空取消）: ").strip()
    
    if not new_title:
        print("  已取消")
        return
    
    # 更新标题
    result = storage.update(recording["id"], {"title": new_title})
    
    if result:
        print(f"\n  已重命名为: {new_title}")
    else:
        print("\n  重命名失败（标题不能为空）")


def main():
    """主菜单"""
    storage = Storage(save_dir=DEFAULT_SAVE_DIR)
    
    while True:
        print("\n" + "=" * 40)
        print("  录音管理工具")
        print("=" * 40)
        print("  1. 列出所有录音")
        print("  2. 播放录音")
        print("  3. 循环播放录音")
        print("  4. 删除录音")
        print("  5. 重命名录音")
        print("  6. 录制新录音")
        print("  0. 退出")
        print("-" * 40)
        
        choice = input("  请选择 (0-6): ").strip()
        
        if choice == "0":
            print("\n  再见！")
            break
        elif choice == "1":
            list_recordings(storage)
        elif choice == "2":
            list_recordings(storage)
            try:
                index = int(input("  输入要播放的序号: ").strip())
                play_recording(storage, index, loop=False)
            except ValueError:
                print("\n  错误：请输入数字")
        elif choice == "3":
            list_recordings(storage)
            try:
                index = int(input("  输入要循环播放的序号: ").strip())
                play_recording(storage, index, loop=True)
            except ValueError:
                print("\n  错误：请输入数字")
        elif choice == "4":
            list_recordings(storage)
            try:
                index = int(input("  输入要删除的序号: ").strip())
                delete_recording(storage, index)
            except ValueError:
                print("\n  错误：请输入数字")
        elif choice == "5":
            list_recordings(storage)
            try:
                index = int(input("  输入要重命名的序号: ").strip())
                rename_recording(storage, index)
            except ValueError:
                print("\n  错误：请输入数字")
        elif choice == "6":
            record_new(storage)
        else:
            print("\n  错误：无效选择")


if __name__ == "__main__":
    main()
