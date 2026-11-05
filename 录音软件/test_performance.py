"""
性能验证测试 - 阶段5
验证大量录音记录下的加载和查询性能
"""
import unittest
import os
import tempfile
import shutil
import time
from storage import Storage


class TestPerformance100(unittest.TestCase):
    """100条录音性能测试"""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_storage_with_n_records(self, n: int) -> Storage:
        """创建包含n条记录的Storage实例"""
        storage = Storage(save_dir=self.test_dir)
        for i in range(n):
            storage.add({
                "id": f"rec_{i:05d}",
                "title": f"录音标题_{i}",
                "filepath": os.path.join(self.test_dir, f"录音_{i:05d}.wav"),
                "created_at": f"2026-01-{i % 28 + 1:02d}T10:00:00",
                "duration": 30.0 + i * 0.5,
            })
        return storage

    def test_load_100_records_under_1_second(self):
        """测试：加载100条记录应在1秒内完成"""
        # 先写入100条
        self._create_storage_with_n_records(100)

        # 重新加载（模拟冷启动）
        start = time.perf_counter()
        storage = Storage(save_dir=self.test_dir)
        elapsed = time.perf_counter() - start

        self.assertEqual(storage.count, 100)
        self.assertLess(elapsed, 1.0, f"加载100条耗时 {elapsed:.3f}s，超过1秒")
        print(f"  [100条] 加载耗时: {elapsed:.4f}s")

    def test_get_all_100_records_under_0_5_second(self):
        """测试：get_all()获取100条应在0.5秒内"""
        storage = self._create_storage_with_n_records(100)

        start = time.perf_counter()
        result = storage.get_all()
        elapsed = time.perf_counter() - start

        self.assertEqual(len(result), 100)
        self.assertLess(elapsed, 0.5, f"get_all(100)耗时 {elapsed:.3f}s，超过0.5秒")
        print(f"  [100条] get_all耗时: {elapsed:.4f}s")

    def test_get_by_id_100_records_under_0_1_second(self):
        """测试：get_by_id在100条中查找应在0.1秒内"""
        storage = self._create_storage_with_n_records(100)

        start = time.perf_counter()
        result = storage.get_by_id("rec_00099")
        elapsed = time.perf_counter() - start

        self.assertIsNotNone(result)
        self.assertEqual(result["id"], "rec_00099")
        self.assertLess(elapsed, 0.1, f"get_by_id(100)耗时 {elapsed:.3f}s，超过0.1秒")
        print(f"  [100条] get_by_id耗时: {elapsed:.4f}s")


class TestPerformance500(unittest.TestCase):
    """500条录音性能测试"""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_storage_with_n_records(self, n: int) -> Storage:
        storage = Storage(save_dir=self.test_dir)
        for i in range(n):
            storage.add({
                "id": f"rec_{i:05d}",
                "title": f"录音标题_{i}",
                "filepath": os.path.join(self.test_dir, f"录音_{i:05d}.wav"),
                "created_at": f"2026-01-{i % 28 + 1:02d}T10:00:00",
                "duration": 30.0 + i * 0.5,
            })
        return storage

    def test_load_500_records_under_3_seconds(self):
        """测试：加载500条记录应在3秒内完成"""
        self._create_storage_with_n_records(500)

        start = time.perf_counter()
        storage = Storage(save_dir=self.test_dir)
        elapsed = time.perf_counter() - start

        self.assertEqual(storage.count, 500)
        self.assertLess(elapsed, 3.0, f"加载500条耗时 {elapsed:.3f}s，超过3秒")
        print(f"  [500条] 加载耗时: {elapsed:.4f}s")

    def test_get_all_500_records_under_1_second(self):
        """测试：get_all()获取500条应在1秒内"""
        storage = self._create_storage_with_n_records(500)

        start = time.perf_counter()
        result = storage.get_all()
        elapsed = time.perf_counter() - start

        self.assertEqual(len(result), 500)
        self.assertLess(elapsed, 1.0, f"get_all(500)耗时 {elapsed:.3f}s，超过1秒")
        print(f"  [500条] get_all耗时: {elapsed:.4f}s")

    def test_get_by_id_500_records_under_0_1_second(self):
        """测试：get_by_id在500条中查找应在0.1秒内"""
        storage = self._create_storage_with_n_records(500)

        start = time.perf_counter()
        result = storage.get_by_id("rec_00499")
        elapsed = time.perf_counter() - start

        self.assertIsNotNone(result)
        self.assertEqual(result["id"], "rec_00499")
        self.assertLess(elapsed, 0.1, f"get_by_id(500)耗时 {elapsed:.3f}s，超过0.1秒")
        print(f"  [500条] get_by_id耗时: {elapsed:.4f}s")


class TestPerformanceJsonSize(unittest.TestCase):
    """JSON文件大小合理性测试"""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_json_size_100_records_under_100kb(self):
        """测试：100条记录的JSON文件应小于100KB"""
        storage = Storage(save_dir=self.test_dir)
        for i in range(100):
            storage.add({
                "id": f"rec_{i:05d}",
                "title": f"录音标题_{i}",
                "filepath": os.path.join(self.test_dir, f"录音_{i:05d}.wav"),
                "created_at": f"2026-01-{i % 28 + 1:02d}T10:00:00",
                "duration": 30.0 + i * 0.5,
            })

        size = os.path.getsize(storage.json_path)
        size_kb = size / 1024
        self.assertLess(size, 100 * 1024, f"JSON大小 {size_kb:.1f}KB，超过100KB")
        print(f"  [100条] JSON大小: {size_kb:.1f}KB")

    def test_json_size_500_records_under_500kb(self):
        """测试：500条记录的JSON文件应小于500KB"""
        storage = Storage(save_dir=self.test_dir)
        for i in range(500):
            storage.add({
                "id": f"rec_{i:05d}",
                "title": f"录音标题_{i}",
                "filepath": os.path.join(self.test_dir, f"录音_{i:05d}.wav"),
                "created_at": f"2026-01-{i % 28 + 1:02d}T10:00:00",
                "duration": 30.0 + i * 0.5,
            })

        size = os.path.getsize(storage.json_path)
        size_kb = size / 1024
        self.assertLess(size, 500 * 1024, f"JSON大小 {size_kb:.1f}KB，超过500KB")
        print(f"  [500条] JSON大小: {size_kb:.1f}KB")


if __name__ == '__main__':
    unittest.main()
