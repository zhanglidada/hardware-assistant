#!/usr/bin/env python3
"""
JSON to JSONL Converter Script

This script converts JSON array files to JSON Lines format for WeChat Cloud Database import.
JSON Lines format: One JSON object per line, no commas, no enclosing brackets.

Usage:
    python scripts/convert_to_jsonl.py
"""

import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any


def convert_json_to_jsonl(input_path: Path, output_path: Path) -> bool:
    """
    Convert a JSON array file to JSON Lines format.
    
    Args:
        input_path: Path to input JSON file
        output_path: Path to output JSONL file
        
    Returns:
        True if conversion successful, False otherwise
    """
    try:
        print(f"📖 Reading: {input_path}")
        
        # Read JSON file
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate that data is a list
        if not isinstance(data, list):
            print(f"❌ Error: {input_path} does not contain a JSON array")
            return False
        
        print(f"📊 Found {len(data)} objects in {input_path.name}")
        
        # Write JSON Lines format
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, obj in enumerate(data):
                # Write each object as a separate line
                json_line = json.dumps(obj, ensure_ascii=False)
                f.write(json_line)
                
                # Add newline except for the last line
                if i < len(data) - 1:
                    f.write('\n')
        
        print(f"✅ Successfully converted to: {output_path}")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error in {input_path}: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error processing {input_path}: {e}")
        return False


def scan_and_convert_json_files(mock_dir: Path) -> Dict[str, bool]:
    """
    Scan directory for JSON files and convert them to JSONL format.
    
    Args:
        mock_dir: Path to mock directory
        
    Returns:
        Dictionary mapping filenames to conversion success status
    """
    results = {}
    
    # Find all JSON files in the directory
    json_files = list(mock_dir.glob("*.json"))
    
    if not json_files:
        print(f"⚠️ No JSON files found in {mock_dir}")
        return results
    
    print(f"🔍 Found {len(json_files)} JSON files in {mock_dir}")
    
    for json_file in json_files:
        # Skip if already a JSONL file
        if json_file.suffix == '.jsonl':
            continue
            
        # Create output filename with .jsonl extension
        output_file = json_file.with_suffix('.jsonl')
        
        # Convert the file
        success = convert_json_to_jsonl(json_file, output_file)
        results[json_file.name] = success
    
    return results


def validate_jsonl_file(jsonl_path: Path) -> bool:
    """
    Validate that a JSONL file is correctly formatted.
    
    Args:
        jsonl_path: Path to JSONL file
        
    Returns:
        True if valid, False otherwise
    """
    try:
        print(f"🔍 Validating: {jsonl_path}")
        
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Check each line is valid JSON
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line:  # Skip empty lines
                continue
                
            try:
                json.loads(line)
            except json.JSONDecodeError as e:
                print(f"❌ Line {i} is not valid JSON: {e}")
                print(f"   Line content: {line[:100]}...")
                return False
        
        print(f"✅ {jsonl_path.name} is valid JSONL format")
        print(f"   Total lines: {len(lines)}")
        return True
        
    except Exception as e:
        print(f"❌ Error validating {jsonl_path}: {e}")
        return False


def main():
    """Main function to run the JSON to JSONL conversion."""
    print("=" * 60)
    print("📦 JSON to JSONL Converter")
    print("=" * 60)
    
    # Set up paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    mock_dir = project_root / "src" / "mock"
    
    print(f"📁 Project root: {project_root}")
    print(f"📁 Mock directory: {mock_dir}")
    
    # Check if mock directory exists
    if not mock_dir.exists():
        print(f"❌ Mock directory not found: {mock_dir}")
        print("Please ensure the directory structure is correct.")
        sys.exit(1)
    
    # Scan and convert JSON files
    print("\n" + "=" * 60)
    print("🔄 Converting JSON files to JSONL format...")
    print("=" * 60)
    
    results = scan_and_convert_json_files(mock_dir)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Conversion Summary")
    print("=" * 60)
    
    successful = 0
    failed = 0
    
    for filename, success in results.items():
        if success:
            print(f"✅ {filename}: Success")
            successful += 1
        else:
            print(f"❌ {filename}: Failed")
            failed += 1
    
    print(f"\n📈 Total: {successful} successful, {failed} failed")
    
    # Validate converted files
    if successful > 0:
        print("\n" + "=" * 60)
        print("🔍 Validating JSONL files...")
        print("=" * 60)
        
        jsonl_files = list(mock_dir.glob("*.jsonl"))
        validation_results = []
        
        for jsonl_file in jsonl_files:
            is_valid = validate_jsonl_file(jsonl_file)
            validation_results.append((jsonl_file.name, is_valid))
        
        # Print validation summary
        print("\n" + "=" * 60)
        print("📊 Validation Summary")
        print("=" * 60)
        
        valid_count = sum(1 for _, is_valid in validation_results if is_valid)
        invalid_count = len(validation_results) - valid_count
        
        for filename, is_valid in validation_results:
            status = "✅ Valid" if is_valid else "❌ Invalid"
            print(f"{status}: {filename}")
        
        print(f"\n📈 Validation: {valid_count} valid, {invalid_count} invalid")
    
    # Provide usage instructions for WeChat Cloud Database
    print("\n" + "=" * 60)
    print("🚀 WeChat Cloud Database Import Instructions")
    print("=" * 60)
    print("""
To import the JSONL files into WeChat Cloud Database:

1. Open WeChat Developer Tools
2. Go to Cloud Development Console
3. Select your database collection
4. Click "Import" button
5. Select the corresponding .jsonl file
6. Ensure "JSON Lines" format is selected
7. Click "Import"

Note: Each line in the .jsonl file will become a separate document.
    """)
    
    # Exit with appropriate code
    if failed > 0:
        print("\n⚠️ Some files failed to convert. Please check the errors above.")
        sys.exit(1)
    else:
        print("\n🎉 All files converted successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()
