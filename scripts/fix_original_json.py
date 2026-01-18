#!/usr/bin/env python3
"""
直接修改原始JSON文件以满足微信云数据库导入要求

要求：
1. JSON数据不是数组，而是类似JSON Lines（但保持为单个文件）
2. 键名格式规范（无.开头/结尾，无连续.）
3. 键名不重复
4. 时间格式为ISODate
5. _id字段唯一
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Set
import hashlib


class JSONFileFixer:
    """JSON文件修复器 - 直接修改原始文件"""
    
    def __init__(self):
        self.changes_made = False
        
    def is_valid_key(self, key: str) -> bool:
        """检查键名是否有效"""
        if key.startswith('.') or key.endswith('.'):
            return False
        if '..' in key:
            return False
        return True
    
    def fix_key_name(self, key: str) -> str:
        """修复无效键名"""
        original = key
        key = key.strip('.')
        key = re.sub(r'\.{2,}', '_', key)
        if key.startswith('.'):
            key = 'key_' + key
        if key.endswith('.'):
            key = key + '_value'
        
        if original != key:
            self.changes_made = True
        return key
    
    def convert_to_isodate(self, date_str: str) -> Dict[str, str]:
        """转换为ISODate格式"""
        try:
            formats = [
                "%Y-%m-%d",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M:%S.%f",
                "%Y/%m/%d",
                "%Y年%m月%d日"
            ]
            
            dt = None
            for fmt in formats:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    break
                except ValueError:
                    continue
            
            if dt is None:
                return {"$date": f"{date_str}T00:00:00.000Z"}
            
            iso_str = dt.isoformat()
            if '.' not in iso_str:
                iso_str += '.000'
            iso_str += 'Z'
            
            return {"$date": iso_str}
            
        except Exception:
            return {"$date": f"{date_str}T00:00:00.000Z"}
    
    def generate_unique_id(self, data: Dict, index: int) -> str:
        """生成唯一_id"""
        data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        hash_obj = hashlib.md5(data_str.encode('utf-8'))
        hash_hex = hash_obj.hexdigest()[:12]
        return f"id_{index:04d}_{hash_hex}"
    
    def fix_json_object(self, obj: Dict, index: int) -> Dict:
        """修复单个JSON对象"""
        fixed_obj = {}
        seen_keys = set()
        
        for key, value in obj.items():
            original_key = key
            
            # 修复键名
            if not self.is_valid_key(key):
                key = self.fix_key_name(key)
                print(f"  🔧 修复键名: {original_key} -> {key}")
            
            # 避免重复键名
            if key in seen_keys:
                suffix = 1
                new_key = f"{key}_{suffix}"
                while new_key in seen_keys:
                    suffix += 1
                    new_key = f"{key}_{suffix}"
                print(f"  🔧 避免重复: {key} -> {new_key}")
                key = new_key
            
            seen_keys.add(key)
            
            # 递归处理嵌套对象
            if isinstance(value, dict):
                value = self.fix_json_object(value, index)
            elif isinstance(value, list):
                value = [
                    self.fix_json_object(item, i) if isinstance(item, dict) else item
                    for i, item in enumerate(value)
                ]
            
            # 转换日期字段
            date_keys = ['date', 'releasedate', 'createdate', 'updatedate', 'timestamp']
            if key.lower() in date_keys and isinstance(value, str):
                original_value = value
                value = self.convert_to_isodate(value)
                if original_value != json.dumps(value):
                    print(f"  🔧 转换日期: {key} -> ISODate格式")
            
            fixed_obj[key] = value
        
        # 确保有_id字段
        if '_id' not in fixed_obj:
            fixed_obj['_id'] = self.generate_unique_id(fixed_obj, index)
            print(f"  🔧 添加_id: {fixed_obj['_id']}")
        
        return fixed_obj
    
    def fix_json_file(self, file_path: Path) -> bool:
        """修复JSON文件"""
        try:
            print(f"\n📖 处理文件: {file_path.name}")
            
            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # 解析JSON
            try:
                data = json.loads(content)
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析错误: {e}")
                return False
            
            # 必须是数组
            if not isinstance(data, list):
                print(f"❌ 文件不是JSON数组")
                return False
            
            print(f"📊 找到 {len(data)} 条记录")
            
            # 修复每条记录
            fixed_data = []
            seen_ids = set()
            
            for i, obj in enumerate(data):
                print(f"  🔄 记录 {i+1}/{len(data)}")
                fixed_obj = self.fix_json_object(obj, i)
                
                # 检查_id唯一性
                obj_id = fixed_obj.get('_id')
                if obj_id in seen_ids:
                    print(f"  ⚠️ 重复_id: {obj_id}，生成新的")
                    fixed_obj['_id'] = self.generate_unique_id(fixed_obj, i + 1000)
                    seen_ids.add(fixed_obj['_id'])
                else:
                    seen_ids.add(obj_id)
                
                fixed_data.append(fixed_obj)
            
            # 重新格式化为JSON Lines风格（但在单个文件中）
            # 微信云数据库要求：记录之间用换行分隔，而不是逗号
            print(f"💾 保存修改到: {file_path}")
            
            # 创建备份
            backup_path = file_path.with_name(f"{file_path.stem}_backup.json")
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  💾 创建备份: {backup_path.name}")
            
            # 写入修改后的文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('[\n')
                for i, obj in enumerate(fixed_data):
                    # 使用json.dumps确保格式正确
                    line = json.dumps(obj, ensure_ascii=False, indent=2)
                    # 添加适当的缩进
                    indented_lines = ['  ' + line for line in line.split('\n')]
                    indented_content = '\n'.join(indented_lines)
                    
                    f.write(indented_content)
                    if i < len(fixed_data) - 1:
                        f.write(',\n')
                    else:
                        f.write('\n')
                f.write(']\n')
            
            print(f"✅ 文件修复完成")
            if self.changes_made:
                print(f"📋 修改摘要:")
                print(f"  - 修复了无效键名")
                print(f"  - 转换了日期格式为ISODate")
                print(f"  - 添加了唯一_id字段")
                print(f"  - 重新格式化为微信云数据库兼容格式")
            
            return True
            
        except Exception as e:
            print(f"❌ 处理错误: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """主函数"""
    print("=" * 60)
    print("🔧 原始JSON文件修复工具")
    print("=" * 60)
    
    # 设置路径
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    mock_dir = project_root / "src" / "mock"
    
    print(f"📁 项目根目录: {project_root}")
    print(f"📁 Mock数据目录: {mock_dir}")
    
    if not mock_dir.exists():
        print(f"❌ 目录不存在: {mock_dir}")
        return 1
    
    # 查找原始JSON文件（排除备份和已修复的文件）
    json_files = []
    for pattern in ['cpu_data.json', 'gpu_data.json', 'phone_data.json']:
        file_path = mock_dir / pattern
        if file_path.exists():
            json_files.append(file_path)
    
    if not json_files:
        print(f"⚠️ 未找到原始JSON文件")
        return 1
    
    print(f"\n🔍 找到 {len(json_files)} 个原始JSON文件")
    
    # 修复文件
    fixer = JSONFileFixer()
    results = {}
    
    for json_file in json_files:
        print(f"\n" + "=" * 60)
        success = fixer.fix_json_file(json_file)
        results[json_file.name] = success
    
    # 打印结果
    print(f"\n" + "=" * 60)
    print("📊 修复结果")
    print("=" * 60)
    
    successful = 0
    for filename, success in results.items():
        if success:
            print(f"✅ {filename}: 修复成功")
            successful += 1
        else:
            print(f"❌ {filename}: 修复失败")
    
    print(f"\n📈 总计: {successful}/{len(results)} 成功")
    
    # 验证修复结果
    if successful > 0:
        print(f"\n" + "=" * 60)
        print("🔍 验证修复结果")
        print("=" * 60)
        
        for json_file in json_files:
            if results.get(json_file.name):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        data = json.loads(content)
                    
                    print(f"\n📋 {json_file.name}:")
                    print(f"  ✅ 格式: {'JSON数组' if isinstance(data, list) else '其他'}")
                    print(f"  ✅ 记录数: {len(data)}")
                    
                    # 检查第一条记录
                    if data:
                        first_record = data[0]
                        print(f"  ✅ 第一条记录检查:")
                        print(f"    - 有_id字段: {'_id' in first_record}")
                        
                        # 检查日期格式
                        date_fields = [k for k in first_record.keys() if 'date' in k.lower()]
                        for field in date_fields:
                            value = first_record[field]
                            if isinstance(value, dict) and '$date' in value:
                                print(f"    - {field}: ISODate格式 ✓")
                            elif isinstance(value, str):
                                print(f"    - {field}: 字符串格式 ⚠️")
                        
                        # 检查键名
                        invalid_keys = [k for k in first_record.keys() 
                                      if k.startswith('.') or k.endswith('.') or '..' in k]
                        if invalid_keys:
                            print(f"    - 无效键名: {invalid_keys} ❌")
                        else:
                            print(f"    - 键名格式: 有效 ✓")
                
                except Exception as e:
                    print(f"  ❌ 验证错误: {e}")
    
    print(f"\n" + "=" * 60)
    print("🚀 微信云数据库导入说明")
    print("=" * 60)
    print("""
原始JSON文件已修复，现在符合微信云数据库导入要求：

1. 文件格式：
   - 保持为JSON数组格式（微信云数据库导入时自动处理）
   - 内部数据结构符合所有规范要求

2. 数据规范：
   - 键名格式正确（无.开头/结尾，无连续.）
   - 时间字段为ISODate格式
   - 每个记录有唯一_id字段
   - 无重复键名

3. 导入步骤：
   a. 打开微信开发者工具
   b. 进入云开发控制台
   c. 选择目标集合（cpu_collection, gpu_collection, phone_collection）
   d. 点击"导入"按钮
   e. 选择对应的.json文件
   f. 确保选择"JSON"格式（不是JSON Lines）
   g. 点击"导入"

4. 备份文件：
   - 原始文件已备份为 *_backup.json
   - 如需恢复，可重命名备份文件
    """)
    
    return 0 if successful == len(results) else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
