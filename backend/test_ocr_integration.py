#!/usr/bin/env python3
"""
Test script to verify OCR integration with document upload
"""

import os
import sys
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_ocr_integration():
    """Test OCR integration without Flask dependencies"""
    try:
        from final_ocr_system import MarksCardOCRSystem
        
        print("=" * 60)
        print("🧪 TESTING OCR INTEGRATION")
        print("=" * 60)

        # Test OCR system initialization
        ocr_system = MarksCardOCRSystem(confidence_threshold=0.5)
        print("✅ OCR system initialized successfully")

        # Check for sample images in the project
        sample_dir = os.path.join(os.path.dirname(__file__), 'sample_marks_cards')
        if not os.path.exists(sample_dir):
            print("⚠️ No sample_marks_cards directory found")
            return False

        sample_files = [f for f in os.listdir(sample_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]
        
        if not sample_files:
            print("⚠️ No sample image files found")
            return False

        print(f"✅ Found {len(sample_files)} sample image(s)")

        # Test OCR processing on first sample
        sample_file = os.path.join(sample_dir, sample_files[0])
        print(f"📄 Processing: {sample_files[0]}")

        try:
            marks_data = ocr_system.process_marks_card(sample_file, preprocess=True)
            
            # Convert to the same format as the API
            ocr_data = {
                'university': marks_data.university,
                'student_name': marks_data.student_info.name,
                'roll_number': marks_data.student_info.roll_number,
                'subjects': [
                    {
                        'course_code': s.course_code,
                        'course_title': s.course_title,
                        'marks': s.total_marks
                    } for s in marks_data.subjects
                ],
                'result': marks_data.result,
                'total_elements': len(marks_data.all_extracted_text)
            }
            
            extracted_text = ' '.join([item['text'] for item in marks_data.all_extracted_text])

            print("✅ OCR processing completed successfully")
            print(f"   University: {ocr_data.get('university', 'N/A')}")
            print(f"   Student Name: {ocr_data.get('student_name', 'N/A')}")
            print(f"   Roll Number: {ocr_data.get('roll_number', 'N/A')}")
            print(f"   Result: {ocr_data.get('result', 'N/A')}")
            print(f"   Subjects Found: {len(ocr_data.get('subjects', []))}")
            print(f"   Extracted Text Length: {len(extracted_text)} characters")

            # Save test results
            results = {
                'ocr_data': ocr_data,
                'extracted_text': extracted_text,
                'test_successful': True
            }

            with open('ocr_test_results.json', 'w') as f:
                json.dump(results, f, indent=2)
            
            print("✅ Test results saved to ocr_test_results.json")
            return True

        except Exception as ocr_error:
            print(f"❌ OCR processing failed: {ocr_error}")
            return False

    except Exception as e:
        print(f"❌ OCR integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_ocr_integration()
    if success:
        print("\n✅ OCR INTEGRATION TEST PASSED")
        print("🎉 Document upload with OCR processing should work!")
    else:
        print("\n❌ OCR INTEGRATION TEST FAILED")
        print("⚠️ OCR processing may not work correctly")