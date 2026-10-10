#!/usr/bin/env python3
"""
Test Script for OCR Marks Card Extractor
========================================
This script tests the installation and basic functionality.
"""

import sys
import traceback
from pathlib import Path

def test_imports():
    """Test if all required packages can be imported."""
    print("Testing package imports...")
    
    required_packages = [
        ('paddleocr', 'PaddleOCR'),
        ('cv2', 'OpenCV'),
        ('PIL', 'Pillow'),
        ('numpy', 'NumPy'),
        ('pandas', 'Pandas'),
        ('matplotlib', 'Matplotlib')
    ]
    
    success_count = 0
    for package, name in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {name} imported successfully")
            success_count += 1
        except ImportError as e:
            print(f"  ❌ {name} import failed: {str(e)}")
    
    print(f"\nImport Test Result: {success_count}/{len(required_packages)} packages imported successfully")
    return success_count == len(required_packages)

def test_ocr_extractor():
    """Test if our OCR extractor can be imported and initialized."""
    print("\nTesting OCR Extractor...")
    
    try:
        from ocr_extractor import MarksCardOCRExtractor
        print("  ✅ OCR extractor imported successfully")
        
        # Test initialization
        extractor = MarksCardOCRExtractor()
        print("  ✅ OCR extractor initialized successfully")
        return True
        
    except Exception as e:
        print(f"  ❌ OCR extractor test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_directory_structure():
    """Test if required directories exist or can be created."""
    print("\nTesting directory structure...")
    
    directories = [
        "sample_marks_cards",
        "output",
        "logs"
    ]
    
    success_count = 0
    for dir_name in directories:
        try:
            dir_path = Path(dir_name)
            dir_path.mkdir(exist_ok=True)
            print(f"  ✅ Directory '{dir_name}' ready")
            success_count += 1
        except Exception as e:
            print(f"  ❌ Directory '{dir_name}' failed: {str(e)}")
    
    return success_count == len(directories)

def test_demo_import():
    """Test if demo script can be imported."""
    print("\nTesting demo script...")
    
    try:
        import demo
        print("  ✅ Demo script imported successfully")
        return True
    except Exception as e:
        print(f"  ❌ Demo script import failed: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("🧪 RUNNING INSTALLATION AND FUNCTIONALITY TESTS")
    print("=" * 60)
    
    tests = [
        ("Package Imports", test_imports),
        ("OCR Extractor", test_ocr_extractor),
        ("Directory Structure", test_directory_structure),
        ("Demo Script", test_demo_import)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ {test_name} test crashed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<20}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall Result: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 ALL TESTS PASSED! Your OCR extractor is ready to use.")
        print("\n📖 Next Steps:")
        print("1. Add marks card images to 'sample_marks_cards/' folder")
        print("2. Run: python demo.py")
        print("3. Or process directly: python ocr_extractor.py your_image.jpg")
    else:
        print("\n⚠️ Some tests failed. Please check the error messages above.")
        print("Make sure all dependencies are installed in the virtual environment.")

if __name__ == "__main__":
    main()