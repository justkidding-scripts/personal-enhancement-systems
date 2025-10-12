#!/usr/bin/env python3
"""
OCR Integration Script
Automatically apply OCR timeout fixes to your existing projects
"""

import os
import sys
import shutil
from pathlib import Path
from typing import List, Dict, Any
import re

# Import our working fix
from tesseract_timeout_fix_working import WorkingQuickOCR, WorkingFastScreenOCR

class OCRIntegrationHelper:
    """Helper to integrate OCR timeout fixes into existing projects"""
    
    def __init__(self):
        self.home_dir = Path.home()
        self.projects_to_fix = [
            "personal_ai_assistant_v3.py",
            "enhanced_personal_ai_assistant.py", 
            "enhanced_personal_ai_assistant_v2.py",
            "test_ocr.py",
            "simple_background_monitor.py",
            "realtime_monitor.py"
        ]
        
        # Common OCR patterns that need fixing
        self.ocr_patterns = [
            r"pytesseract\.image_to_string\([^)]*timeout=\d+[^)]*\)",
            r"pytesseract\.image_to_string\([^)]*config=[^)]*tessedit_timeout[^)]*\)",
            r"future\.result\(timeout=\d+\)",
            r"ThreadPoolExecutor.*pytesseract",
        ]
        
    def scan_files_for_ocr_usage(self) -> Dict[str, List[str]]:
        """Scan files for OCR usage that needs fixing"""
        ocr_files = {}
        
        for file_name in self.projects_to_fix:
            file_path = self.home_dir / file_name
            if file_path.exists():
                try:
                    content = file_path.read_text(encoding='utf-8')
                    
                    issues = []
                    if 'pytesseract' in content:
                        issues.append("Uses pytesseract")
                    
                    if 'timeout' in content.lower() and 'tesseract' in content.lower():
                        issues.append("Has timeout-related OCR code")
                    
                    for pattern in self.ocr_patterns:
                        if re.search(pattern, content, re.MULTILINE):
                            issues.append(f"Pattern match: {pattern[:50]}...")
                    
                    if issues:
                        ocr_files[str(file_path)] = issues
                        
                except Exception as e:
                    print(f"⚠️ Could not scan {file_path}: {e}")
        
        return ocr_files
    
    def create_backup(self, file_path: Path) -> Path:
        """Create backup of original file"""
        backup_path = file_path.with_suffix(file_path.suffix + '.backup')
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def generate_fixed_import(self) -> str:
        """Generate the import statement for the fix"""
        return """
# OCR Timeout Fix Integration
try:
    from tesseract_timeout_fix_working import WorkingQuickOCR, WorkingFastScreenOCR
    print("✅ OCR timeout fix available")
    
    # Initialize global OCR instances
    _quick_ocr = WorkingQuickOCR()
    _fast_ocr = WorkingFastScreenOCR()
    
    def extract_text_safe(image, fast_mode=False):
        \"\"\"Safe OCR extraction with timeout handling\"\"\"
        if fast_mode:
            return _fast_ocr.extract_screen_text(image)
        else:
            return _quick_ocr.extract_text(image)
            
except ImportError as e:
    print(f"⚠️ OCR timeout fix not available: {e}")
    
    def extract_text_safe(image, fast_mode=False):
        \"\"\"Fallback OCR extraction\"\"\"
        import pytesseract
        try:
            return pytesseract.image_to_string(image, config='--psm 6')
        except Exception as e:
            print(f"OCR fallback error: {e}")
            return None
"""
    
    def generate_replacement_patterns(self) -> List[Dict[str, str]]:
        """Generate common replacement patterns"""
        return [
            {
                'pattern': r'pytesseract\.image_to_string\(([^,]+)(?:,\s*config=[^)]+)?\)',
                'replacement': r'extract_text_safe(\1, fast_mode=False)',
                'description': 'Replace basic pytesseract calls'
            },
            {
                'pattern': r'pytesseract\.image_to_string\(([^,]+),\s*timeout=\d+\)',
                'replacement': r'extract_text_safe(\1, fast_mode=True)',
                'description': 'Replace timeout-based pytesseract calls'
            },
            {
                'pattern': r'text = pytesseract\.image_to_string\(img, config=.*?\)',
                'replacement': r'text = extract_text_safe(img, fast_mode=False)',
                'description': 'Replace config-based OCR calls'
            }
        ]
    
    def apply_fixes_to_file(self, file_path: Path) -> bool:
        """Apply OCR timeout fixes to a specific file"""
        try:
            # Create backup
            backup_path = self.create_backup(file_path)
            print(f"📋 Created backup: {backup_path}")
            
            # Read original content
            content = file_path.read_text(encoding='utf-8')
            original_content = content
            
            # Add import at the top (after existing imports)
            import_section = self.generate_fixed_import()
            
            # Find good place to insert import (after last import)
            import_lines = []
            other_lines = []
            found_import_section = False
            
            for line in content.split('\n'):
                if line.startswith('import ') or line.startswith('from ') or line.strip().startswith('try:'):
                    import_lines.append(line)
                    found_import_section = True
                elif found_import_section and line.strip() == '':
                    import_lines.append(line)
                else:
                    if found_import_section and not import_lines[-1].strip() == '':
                        import_lines.append('')  # Add blank line before imports
                    other_lines.append(line)
                    found_import_section = False
            
            # Reconstruct with new import
            new_content = '\n'.join(import_lines) + import_section + '\n' + '\n'.join(other_lines)
            
            # Apply replacement patterns
            patterns = self.generate_replacement_patterns()
            changes_made = 0
            
            for pattern_info in patterns:
                old_content = new_content
                new_content = re.sub(pattern_info['pattern'], pattern_info['replacement'], new_content)
                if new_content != old_content:
                    changes_made += 1
                    print(f"✅ Applied: {pattern_info['description']}")
            
            # Manual fixes for specific known issues
            if 'ThreadPoolExecutor' in new_content and 'pytesseract' in new_content:
                # Replace complex timeout implementations
                complex_pattern = r'with ThreadPoolExecutor.*?future\.result\(timeout=\d+\)'
                if re.search(complex_pattern, new_content, re.DOTALL):
                    new_content = re.sub(
                        r'with ThreadPoolExecutor\(max_workers=1\) as executor:\s*future = executor\.submit\(pytesseract\.image_to_string, ([^,]+)(?:,\s*[^)]+)?\)\s*try:\s*([^=]+) = future\.result\(timeout=\d+\)',
                        r'\2 = extract_text_safe(\1, fast_mode=True)',
                        new_content,
                        flags=re.MULTILINE | re.DOTALL
                    )
                    changes_made += 1
                    print("✅ Fixed complex ThreadPoolExecutor timeout implementation")
            
            if changes_made > 0:
                # Write the fixed content
                file_path.write_text(new_content, encoding='utf-8')
                print(f"🔧 Applied {changes_made} fixes to {file_path.name}")
                return True
            else:
                # Restore from backup if no changes needed
                shutil.copy2(backup_path, file_path)
                backup_path.unlink()  # Remove backup
                print(f"ℹ️ No OCR fixes needed for {file_path.name}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to fix {file_path}: {e}")
            # Restore from backup on error
            if 'backup_path' in locals() and backup_path.exists():
                shutil.copy2(backup_path, file_path)
            return False
    
    def create_integration_demo(self) -> Path:
        """Create a demo script showing the integration"""
        demo_path = self.home_dir / "ocr_integration_demo.py"
        
        demo_content = '''#!/usr/bin/env python3
"""
OCR Integration Demo
Shows how to use the OCR timeout fix in your applications
"""

import sys
from pathlib import Path
from PIL import Image, ImageDraw
import time

# OCR Timeout Fix Integration
try:
    from tesseract_timeout_fix_working import WorkingQuickOCR, WorkingFastScreenOCR
    print("✅ OCR timeout fix available")
    
    # Initialize global OCR instances
    _quick_ocr = WorkingQuickOCR()
    _fast_ocr = WorkingFastScreenOCR()
    
    def extract_text_safe(image, fast_mode=False):
        """Safe OCR extraction with timeout handling"""
        if fast_mode:
            return _fast_ocr.extract_screen_text(image)
        else:
            return _quick_ocr.extract_text(image)
            
except ImportError as e:
    print(f"⚠️ OCR timeout fix not available: {e}")
    sys.exit(1)

def create_test_image():
    """Create test image for demonstration"""
    img = Image.new('RGB', (500, 120), color='white')
    draw = ImageDraw.Draw(img)
    draw.text((20, 30), "OCR Integration Demo - No More Timeouts!", fill='black')
    draw.text((20, 70), "This text should be extracted safely.", fill='black')
    return img

def demo_integration():
    """Demonstrate the integration working"""
    print("🚀 OCR Integration Demo")
    print("=" * 40)
    
    # Create test image
    test_image = create_test_image()
    print("✅ Created test image")
    
    # Test 1: Quick OCR (balanced)
    print("\\n📝 Testing Quick OCR (recommended for most use cases):")
    start_time = time.time()
    result1 = extract_text_safe(test_image, fast_mode=False)
    elapsed1 = time.time() - start_time
    
    print(f"Result: {repr(result1)}")
    print(f"Time: {elapsed1:.2f}s")
    
    # Test 2: Fast OCR (for real-time applications)
    print("\\n⚡ Testing Fast OCR (for screen captures):")
    start_time = time.time()
    result2 = extract_text_safe(test_image, fast_mode=True)
    elapsed2 = time.time() - start_time
    
    print(f"Result: {repr(result2)}")
    print(f"Time: {elapsed2:.2f}s")
    
    # Summary
    success_count = sum([1 for r in [result1, result2] if r])
    print(f"\\n📊 Success Rate: {success_count}/2 ({success_count/2*100:.0f}%)")
    
    if success_count > 0:
        print("🎉 Integration working correctly!")
        print("💡 Use extract_text_safe() in your applications")
        print("💡 Set fast_mode=True for real-time screen captures")
        print("💡 Set fast_mode=False for better accuracy on documents")
    else:
        print("⚠️ Integration needs attention")
    
    return success_count > 0

if __name__ == "__main__":
    success = demo_integration()
    sys.exit(0 if success else 1)
'''
        
        demo_path.write_text(demo_content, encoding='utf-8')
        demo_path.chmod(0o755)
        return demo_path
    
    def run_integration(self) -> Dict[str, Any]:
        """Run the complete integration process"""
        print("🔧 OCR Timeout Fix Integration")
        print("=" * 50)
        
        # Step 1: Scan for OCR usage
        print("🔍 Scanning for OCR usage...")
        ocr_files = self.scan_files_for_ocr_usage()
        
        if not ocr_files:
            print("ℹ️ No files with OCR usage found")
            return {'success': True, 'files_processed': 0, 'files_fixed': 0}
        
        print(f"📋 Found {len(ocr_files)} files with OCR usage:")
        for file_path, issues in ocr_files.items():
            print(f"  📄 {Path(file_path).name}: {', '.join(issues)}")
        
        # Step 2: Apply fixes
        print(f"\n🔧 Applying fixes...")
        files_fixed = 0
        
        for file_path in ocr_files.keys():
            path_obj = Path(file_path)
            print(f"\n🛠️ Processing {path_obj.name}...")
            
            if self.apply_fixes_to_file(path_obj):
                files_fixed += 1
        
        # Step 3: Create demo
        print(f"\n📋 Creating integration demo...")
        demo_path = self.create_integration_demo()
        print(f"✅ Created demo: {demo_path}")
        
        # Summary
        print(f"\n📊 Integration Summary:")
        print(f"├── Files scanned: {len(ocr_files)}")
        print(f"├── Files fixed: {files_fixed}")
        print(f"└── Demo created: {demo_path.name}")
        
        if files_fixed > 0:
            print(f"\n🎉 SUCCESS! Applied OCR timeout fixes to {files_fixed} files")
            print("💡 Run the demo to verify integration: python ocr_integration_demo.py")
            print("💡 Use extract_text_safe() instead of pytesseract.image_to_string()")
        
        return {
            'success': True,
            'files_processed': len(ocr_files),
            'files_fixed': files_fixed,
            'demo_path': str(demo_path)
        }


def main():
    """Main integration function"""
    try:
        integrator = OCRIntegrationHelper()
        result = integrator.run_integration()
        
        if result['success'] and result['files_fixed'] > 0:
            print(f"\n✅ Integration complete! Fixed {result['files_fixed']} files.")
            print("🚀 Your OCR timeout issues are resolved!")
        elif result['success']:
            print(f"\n✅ Integration scan complete. No fixes needed.")
        else:
            print(f"\n❌ Integration failed.")
        
        return result['success']
        
    except Exception as e:
        print(f"❌ Integration error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)