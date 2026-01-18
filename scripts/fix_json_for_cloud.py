#!/usr/bin/env python3
"""
修复JSON数据格式以满足微信云数据库导入要求

要求：
1. JSON Lines格式（每行一个JSON对象）
2. 键名不能以`.`开头或结尾，不能有连续的`.`
3. 键名不能重复
4. 时间格式必须为ISODate格式：{"$date": "ISO字符串"}
5. _id字段必须唯一
6. 处理CSV格式（本脚本主要处理JSON）

输出：符合要求的JSONL文件
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Set
import hashlib


class JSONFixer:
    """JSON数据修复器"""
    
    def __init__(self):
        self.duplicate_keys_warning = False
        self.invalid_keys_warning = False
        
    def is_valid_key(self, key: str) -> bool:
        """
        检查键名是否有效
        要求：不能以`.`开头或结尾，不能有连续的`.`
        """
        if key.startswith('.') or key.endswith('.'):
            return False
        if '..' in key:
            return False
        return True
    
    def fix_key_name(self, key: str) -> str:
        """
        修复无效的键名
        """
        # 移除开头和结尾的.
        key = key.strip('.')
        # 替换连续的.为单个_
        key = re.sub(r'\.{2,}', '_', key)
        # 如果键名仍然以.开头或结尾，添加前缀/后缀
        if key.startswith('.'):
            key = 'key_' + key
        if key.endswith('.'):
            key = key + '_value'
        return key
    
    def check_duplicate_keys(self, obj: Dict) -> bool:
        """
        检查对象中是否有重复键名
        """
        keys = list(obj.keys())
        unique_keys = set(keys)
        if len(keys) != len(unique_keys):
            print(f"⚠️ 发现重复键名: {[k for k in keys if keys.count(k) > 1]}")
            return True
        return False
    
    def check_nested_ambiguity(self, obj: Dict, parent_key: str = "") -> List[str]:
        """
        检查嵌套键名的歧义（如 {"a": {"b": 1}, "a.b": 2}）
        """
        issues = []
        flat_keys = set()
        
        def flatten_dict(d: Dict, prefix: str = ""):
            for k, v in d.items():
                full_key = f"{prefix}.{k}" if prefix else k
                if isinstance(v, dict):
                    flatten_dict(v, full_key)
                else:
                    if full_key in flat_keys:
                        issues.append(full_key)
                    flat_keys.add(full_key)
        
        flatten_dict(obj)
        return issues
    
    def convert_to_isodate(self, date_str: str) -> Dict[str, str]:
        """
        将日期字符串转换为ISODate格式
        格式: {"$date": "2018-08-31T17:30:00.882Z"}
        """
        try:
            # 尝试解析常见日期格式
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
                # 如果无法解析，返回原始字符串
                print(f"⚠️ 无法解析日期: {date_str}")
                return {"$date": f"{date_str}T00:00:00.000Z"}
            
            # 转换为ISO格式并添加Z时区
            iso_str = dt.isoformat()
            if '.' not in iso_str:
                iso_str += '.000'
            iso_str += 'Z'
            
            return {"$date": iso_str}
            
        except Exception as e:
            print(f"❌ 日期转换错误 {date_str}: {e}")
            return {"$date": f"{date_str}T00:00:00.000Z"}
    
    def generate_unique_id(self, data: Dict, index: int) -> str:
        """
        生成唯一的_id字段
        使用数据哈希 + 索引确保唯一性
        """
        # 创建数据的字符串表示
        data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        # 生成MD5哈希
        hash_obj = hashlib.md5(data_str.encode('utf-8'))
        hash_hex = hash_obj.hexdigest()[:12]  # 取前12位
        # 组合索引和哈希
        return f"id_{index:04d}_{hash_hex}"
    
    def fix_object(self, obj: Dict, index: int) -> Dict:
        """
        修复单个JSON对象
        """
        fixed_obj = {}
        seen_keys = set()
        
        # 检查并修复键名
        for key, value in obj.items():
            original_key = key
            
            # 检查键名有效性
            if not self.is_valid_key(key):
                self.invalid_keys_warning = True
                key = self.fix_key_name(key)
                print(f"⚠️ 修复无效键名: {original_key} -> {key}")
            
            # 检查重复键名
            if key in seen_keys:
                self.duplicate_keys_warning = True
                # 添加后缀避免重复
                suffix = 1
                new_key = f"{key}_{suffix}"
                while new_key in seen_keys:
                    suffix += 1
                    new_key = f"{key}_{suffix}"
                print(f"⚠️ 避免重复键名: {key} -> {new_key}")
                key = new_key
            
            seen_keys.add(key)
            
            # 递归处理嵌套对象
            if isinstance(value, dict):
                value = self.fix_object(value, index)
            elif isinstance(value, list):
                # 处理列表中的对象
                value = [self.fix_object(item, i) if isinstance(item, dict) else item 
                        for i, item in enumerate(value)]
            
            # 检查日期字段并转换
            if key.lower() in ['date', 'releasedate', 'createdate', 'updatedate', 'timestamp']:
                if isinstance(value, str):
                    value = self.convert_to_isodate(value)
            
            fixed_obj[key] = value
        
        # 确保有_id字段且唯一
        if '_id' not in fixed_obj:
            fixed_obj['_id'] = self.generate_unique_id(fixed_obj, index)
        
        return fixed_obj
    
    def fix_json_file(self, input_path: Path, output_path: Path) -> bool:
        """
        修复JSON文件
        """
        try:
            print(f"📖 读取文件: {input_path}")
            
            # 读取JSON文件
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # 尝试解析为JSON数组
            try:
                data = json.loads(content)
                if not isinstance(data, list):
                    print(f"❌ 文件不是JSON数组: {input_path}")
                    return False
            except json.JSONDecodeError:
                # 可能是JSON Lines格式，尝试逐行解析
                print(f"⚠️ 尝试作为JSON Lines解析: {input_path}")
                lines = [line.strip() for line in content.split('\n') if line.strip()]
                data = []
                for line in lines:
                    try:
                        obj = json.loads(line)
                        data.append(obj)
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON解析错误: {e}")
                        return False
            
            print(f"📊 找到 {len(data)} 条记录")
            
            # 修复每条记录
            fixed_data = []
            seen_ids = set()
            
            for i, obj in enumerate(data):
                print(f"🔧 修复记录 {i+1}/{len(data)}")
                fixed_obj = self.fix_object(obj, i)
                
                # 检查_id唯一性
                obj_id = fixed_obj.get('_id')
                if obj_id in seen_ids:
                    print(f"⚠️ 发现重复_id: {obj_id}，生成新的_id")
                    fixed_obj['_id'] = self.generate_unique_id(fixed_obj, i + 1000)
                    seen_ids.add(fixed_obj['_id'])
                else:
                    seen_ids.add(obj_id)
                
                fixed_data.append(fixed_obj)
            
            # 写入JSON Lines格式
            print(f"💾 写入文件: {output_path}")
            with open(output_path, 'w', encoding='utf-8') as f:
                for i, obj in enumerate(fixed_data):
                    json_line = json.dumps(obj, ensure_ascii=False)
                    f.write(json_line)
                    if i < len(fixed_data) - 1:
                        f.write('\n')
            
            # 打印修复摘要
            print(f"\n📋 修复摘要:")
            print(f"  ✅ 总记录数: {len(fixed_data)}")
            print(f"  ✅ 唯一_id数量: {len(seen_ids)}")
            if self.duplicate_keys_warning:
                print(f"  ⚠️ 发现并修复了重复键名")
            if self.invalid_keys_warning:
                print(f"  ⚠️ 发现并修复了无效键名")
            
            return True
            
        except Exception as e:
            print(f"❌ 处理文件时出错 {input_path}: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """主函数"""
    print("=" * 60)
    print("🔧 JSON数据修复工具 - 微信云数据库导入优化")
    print("=" * 60)
    
    # 设置路径
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    mock_dir = project_root / "src" / "mock"
    
    print(f"📁 项目根目录: {project_root}")
    print(f"📁 Mock数据目录: {mock_dir}")
    
    # 检查目录是否存在
    if not mock_dir.exists():
        print(f"❌ Mock目录不存在: {mock_dir}")
        return
    
    # 查找JSON文件
    json_files = list(mock_dir.glob("*.json"))
    if not json_files:
        print(f"⚠️ 未找到JSON文件: {mock_dir}")
        return
    
    print(f"\n🔍 找到 {len(json_files)} 个JSON文件")
    
    # 创建修复器实例
    fixer = JSONFixer()
    
    # 处理每个文件
    results = {}
    for json_file in json_files:
        print(f"\n" + "=" * 60)
        print(f"🔄 处理文件: {json_file.name}")
        print("=" * 60)
        
        # 创建输出文件名（添加_fixed后缀）
        output_file = json_file.with_name(f"{json_file.stem}_fixed.jsonl")
        
        # 修复文件
        success = fixer.fix_json_file(json_file, output_file)
        results[json_file.name] = (success, output_file)
    
    # 打印结果摘要
    print(f"\n" + "=" * 60)
    print("📊 处理结果摘要")
    print("=" * 60)
    
    successful = 0
    failed = 0
    
    for filename, (success, output_file) in results.items():
        if success:
            print(f"✅ {filename} -> {output_file.name}")
            successful += 1
        else:
            print(f"❌ {filename}: 处理失败")
            failed += 1
    
    print(f"\n📈 总计: {successful} 成功, {failed} 失败")
    
    # 提供导入说明
    if successful > 0:
        print(f"\n" + "=" * 60)
        print("🚀 微信云数据库导入说明")
        print("=" * 60)
        print("""
修复后的文件已符合微信云数据库导入要求：

1. 格式要求：
   - JSON Lines格式（每行一个完整JSON对象）
   - 键名符合规范（无.开头/结尾，无连续.）
   - 时间字段已转换为ISODate格式
   - _id字段唯一

2. 导入步骤：
   a. 打开微信开发者工具
   b. 进入云开发控制台
   c. 选择目标集合
   d. 点击"导入"按钮
   e. 选择对应的_fixed.jsonl文件
   f. 确保选择"JSON Lines"格式
   g. 点击"导入"

3. 冲突处理：
   - 使用"Insert"模式时，_id字段会自动去重
   - 建议先清空集合再导入，避免_id冲突
        """)
    
    if failed > 0:
        print(f"\n⚠️ 部分文件处理失败，请检查错误信息")
        return 1
    else:
        print(f"\n🎉 所有文件处理成功！")
        return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
