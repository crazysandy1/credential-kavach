#!/usr/bin/env python3
"""
Comprehensive Marks Card OCR System - Final Working Version
Extracts and structures all fields from marks cards using PaddleOCR
"""

import os
import json
import csv
import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from paddlex import create_pipeline
try:
    # When imported as a module (e.g., from Flask app)
    from .preprocessing import preprocess_image
except Exception:
    # When run directly as a script
    from preprocessing import preprocess_image
import argparse

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class StudentInfo:
    """Student information extracted from marks card."""
    name: Optional[str] = None
    roll_number: Optional[str] = None
    registration_number: Optional[str] = None
    parentage: Optional[str] = None
    program: Optional[str] = None
    semester: Optional[str] = None
    batch: Optional[str] = None
    session: Optional[str] = None

@dataclass
class SubjectMarks:
    """Individual subject marks information."""
    course_code: Optional[str] = None
    course_title: Optional[str] = None
    continuous_assessment: Optional[str] = None
    theory_marks: Optional[str] = None
    total_marks: Optional[str] = None

@dataclass
class MarksCardData:
    """Complete marks card data structure."""
    university: Optional[str] = None
    certificate_type: Optional[str] = None
    student_info: StudentInfo = None
    subjects: List[SubjectMarks] = None
    total_marks: Optional[str] = None
    result: Optional[str] = None
    division: Optional[str] = None
    all_extracted_text: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.student_info is None:
            self.student_info = StudentInfo()
        if self.subjects is None:
            self.subjects = []
        if self.all_extracted_text is None:
            self.all_extracted_text = []

class MarksCardOCRSystem:
    """Complete OCR system for marks cards with structured field extraction."""
    
    def __init__(self, confidence_threshold: float = 0.5):
        """Initialize the OCR system."""
        self.confidence_threshold = confidence_threshold
        logger.info("Initializing PaddleOCR system...")
        
        try:
            self.ocr = create_pipeline(pipeline="OCR")
            logger.info("✅ PaddleOCR initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize PaddleOCR: {e}")
            raise
    
    def extract_raw_text(self, image_path: str) -> List[Dict[str, Any]]:
        """Extract raw text from image using PaddleOCR."""
        try:
            logger.info(f"🔍 Processing image: {image_path}")
            
            # Perform OCR
            results_generator = self.ocr.predict(image_path)
            results = list(results_generator)
            
            if not results:
                logger.warning("⚠️ No text detected")
                return []
            
            result = results[0]
            
            def find_rec_data(obj, depth=0):
                """Recursively search for rec_texts and rec_scores."""
                if depth > 3:
                    return None
                    
                if isinstance(obj, dict):
                    if 'rec_texts' in obj and 'rec_scores' in obj:
                        return obj
                    
                    for value in obj.values():
                        found = find_rec_data(value, depth + 1)
                        if found:
                            return found
                elif hasattr(obj, '__dict__'):
                    return find_rec_data(obj.__dict__, depth + 1)
                
                return None
            
            # Find the data containing rec_texts and rec_scores
            result_data = find_rec_data(result)
            
            if result_data and 'rec_texts' in result_data:
                texts = result_data['rec_texts']
                scores = result_data['rec_scores']
                
                logger.info(f"📊 Found {len(texts)} text elements")
                
                extracted_text = []
                for i, (text, confidence) in enumerate(zip(texts, scores)):
                    if confidence >= self.confidence_threshold:
                        extracted_text.append({
                            'text': str(text).strip(),
                            'confidence': float(confidence),
                            'index': i
                        })
                
                logger.info(f"✅ Extracted {len(extracted_text)} high-confidence text elements")
                return extracted_text
            else:
                logger.error("❌ Could not find rec_texts and rec_scores in result")
                return []
                
        except Exception as e:
            logger.error(f"❌ OCR extraction failed: {e}")
            return []
    
    def extract_student_info(self, text_elements: List[Dict[str, Any]]) -> StudentInfo:
        """Extract student information from text elements."""
        student_info = StudentInfo()
        
        for item in text_elements:
            text = item['text'].upper()
            
            # Extract name
            if 'NAME' in text and student_info.name is None:
                # Look for patterns like "NameTAHIRAHMAD·KHAN" or "Name: John Doe"
                name_match = re.search(r'NAME\s*[:.\-]*\s*([A-Z\s\-·.]+)', text)
                if name_match:
                    student_info.name = name_match.group(1).strip()
            
            # Extract roll number
            if ('ROLL' in text or 'ROL' in text) and student_info.roll_number is None:
                roll_match = re.search(r'ROL[L]?\s*[N.]?\s*[:.\-]*\s*([A-Z0-9\-]+)', text)
                if roll_match:
                    student_info.roll_number = roll_match.group(1).strip()
            
            # Extract registration number
            if 'REG' in text and student_info.registration_number is None:
                reg_match = re.search(r'REG\.?\s*NO\.?\s*[:.\-]*\s*([A-Z0-9\-]+)', text)
                if reg_match:
                    student_info.registration_number = reg_match.group(1).strip()
            
            # Extract parentage
            if 'PARENTAGE' in text and student_info.parentage is None:
                parent_match = re.search(r'PARENTAGE\s*[:.\-]*\s*([A-Z\s\-·.]+)', text)
                if parent_match:
                    student_info.parentage = parent_match.group(1).strip()
            
            # Extract program
            if ('MASTER' in text or 'BACHELOR' in text or 'MBA' in text) and student_info.program is None:
                student_info.program = text.strip()
            
            # Extract semester
            if 'SEMESTER' in text and student_info.semester is None:
                sem_match = re.search(r'SEMESTER\s*[:.\-]*\s*([A-Z0-9\s]+)', text)
                if sem_match:
                    student_info.semester = sem_match.group(1).strip()
            
            # Extract batch/session
            if ('BATCH' in text or 'SESSION' in text) and student_info.batch is None:
                batch_match = re.search(r'(?:BATCH|SESSION)\s*[:.\-]*\s*([A-Z0-9\s\-]+)', text)
                if batch_match:
                    student_info.batch = batch_match.group(1).strip()
        
        return student_info
    
    def extract_subjects(self, text_elements: List[Dict[str, Any]]) -> List[SubjectMarks]:
        """Extract subject marks from text elements."""
        subjects = []
        
        # Look for course codes (like MBA401, MBA402, etc.)
        course_pattern = re.compile(r'([A-Z]{2,4}\d{3,4})')
        
        for i, item in enumerate(text_elements):
            text = item['text']
            
            if course_pattern.match(text):
                subject = SubjectMarks()
                subject.course_code = text
                
                # Look for course title in next few elements
                for j in range(i + 1, min(i + 3, len(text_elements))):
                    next_text = text_elements[j]['text']
                    # If it's not a number and not another course code, it might be the title
                    if not next_text.isdigit() and not course_pattern.match(next_text) and len(next_text) > 5:
                        subject.course_title = next_text
                        break
                
                # Look for marks in subsequent elements
                marks_found = []
                for j in range(i + 1, min(i + 6, len(text_elements))):
                    next_text = text_elements[j]['text']
                    if next_text.isdigit() and len(next_text) <= 3:
                        marks_found.append(next_text)
                
                # Assign marks based on typical structure
                if len(marks_found) >= 2:
                    subject.continuous_assessment = marks_found[0]
                    subject.theory_marks = marks_found[1]
                    subject.total_marks = marks_found[2] if len(marks_found) > 2 else None
                
                subjects.append(subject)
        
        return subjects
    
    def extract_summary_info(self, text_elements: List[Dict[str, Any]]) -> Tuple[str, str, str]:
        """Extract total marks, result, and division."""
        total_marks = None
        result = None
        division = None
        
        for item in text_elements:
            text = item['text'].upper()
            
            # Extract total marks
            if 'TOTAL' in text and any(char.isdigit() for char in text):
                # Look for numbers in the text
                numbers = re.findall(r'\d+', text)
                if numbers:
                    total_marks = numbers[-1]  # Take the last number
            
            # Extract result
            if text in ['PASS', 'FAIL', 'FIRST CLASS', 'SECOND CLASS']:
                result = text
            
            # Extract division
            if 'DIVISION' in text or text in ['IST', 'IIND', 'IIIRD']:
                division = text
        
        return total_marks, result, division
    
    def process_marks_card(self, image_path: str, *, preprocess: bool = True,
                           do_deskew: bool = True, do_denoise: bool = True,
                           use_adaptive: bool = True, contrast: bool = True,
                           temp_dir: Optional[str] = None) -> MarksCardData:
        """Process complete marks card and return structured data."""
        logger.info(f"🎯 Processing marks card: {image_path}")

        # Optional preprocessing with OpenCV
        img_for_ocr = image_path
        if preprocess:
            try:
                img_for_ocr = preprocess_image(
                    image_path,
                    do_deskew=do_deskew,
                    do_denoise=do_denoise,
                    use_adaptive=use_adaptive,
                    contrast=contrast,
                    output_dir=temp_dir
                )
                logger.info(f"🧪 Preprocessed image saved: {img_for_ocr}")
            except Exception as e:
                logger.warning(f"⚠️ Preprocessing failed ({e}), falling back to original image")
                img_for_ocr = image_path
        
        # Extract raw text
        text_elements = self.extract_raw_text(img_for_ocr)
        
        if not text_elements:
            logger.error("❌ No text elements extracted")
            return MarksCardData()
        
        # Initialize marks card data
        marks_data = MarksCardData()
        marks_data.all_extracted_text = text_elements
        
        # Extract university and certificate type
        if text_elements:
            marks_data.university = text_elements[0]['text']  # Usually the first element
            if len(text_elements) > 1:
                marks_data.certificate_type = text_elements[1]['text']
        
        # Extract structured information
        marks_data.student_info = self.extract_student_info(text_elements)
        marks_data.subjects = self.extract_subjects(text_elements)
        
        # Extract summary information
        total_marks, result, division = self.extract_summary_info(text_elements)
        marks_data.total_marks = total_marks
        marks_data.result = result
        marks_data.division = division
        
        logger.info(f"✅ Extraction complete:")
        logger.info(f"   📚 Student: {marks_data.student_info.name}")
        logger.info(f"   🆔 Roll No: {marks_data.student_info.roll_number}")
        logger.info(f"   📖 Subjects: {len(marks_data.subjects)}")
        logger.info(f"   📊 Total Elements: {len(text_elements)}")
        
        return marks_data
    
    def save_results(self, marks_data: MarksCardData, output_dir: str = "results"):
        """Save results in multiple formats."""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save structured JSON
        json_path = os.path.join(output_dir, "marks_card_structured.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            # Convert dataclass to dict for JSON serialization
            data_dict = asdict(marks_data)
            json.dump(data_dict, f, indent=2, ensure_ascii=False)
        
        # Save CSV of all text
        csv_path = os.path.join(output_dir, "extracted_text.csv")
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Index', 'Text', 'Confidence'])
            for item in marks_data.all_extracted_text:
                writer.writerow([item['index'], item['text'], item['confidence']])
        
        # Save subjects CSV
        if marks_data.subjects:
            subjects_csv = os.path.join(output_dir, "subjects.csv")
            with open(subjects_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Course Code', 'Course Title', 'Continuous Assessment', 'Theory Marks', 'Total Marks'])
                for subject in marks_data.subjects:
                    writer.writerow([
                        subject.course_code,
                        subject.course_title,
                        subject.continuous_assessment,
                        subject.theory_marks,
                        subject.total_marks
                    ])
        
        logger.info(f"💾 Results saved to '{output_dir}' directory:")
        logger.info(f"   📄 {json_path}")
        logger.info(f"   📊 {csv_path}")
        if marks_data.subjects:
            logger.info(f"   📚 {subjects_csv}")

def main():
    """Main function with command-line interface."""
    parser = argparse.ArgumentParser(description='Comprehensive Marks Card OCR System')
    parser.add_argument('image_path', help='Path to the marks card image')
    parser.add_argument('-o', '--output', default='results', help='Output directory')
    parser.add_argument('-c', '--confidence', type=float, default=0.5, help='Confidence threshold')
    # Preprocessing flags
    parser.add_argument('--no-preprocess', action='store_true', help='Disable OpenCV preprocessing')
    parser.add_argument('--no-deskew', action='store_true', help='Disable deskew step in preprocessing')
    parser.add_argument('--no-denoise', action='store_true', help='Disable denoise step in preprocessing')
    parser.add_argument('--otsu', action='store_true', help='Use Otsu threshold instead of adaptive')
    parser.add_argument('--no-contrast', action='store_true', help='Disable CLAHE contrast enhancement')
    parser.add_argument('--temp-dir', default=None, help='Directory to store preprocessed image')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.image_path):
        print(f"❌ Error: Image file '{args.image_path}' not found")
        return
    
    try:
        # Initialize OCR system
        ocr_system = MarksCardOCRSystem(confidence_threshold=args.confidence)
        
        # Process marks card
        marks_data = ocr_system.process_marks_card(
            args.image_path,
            preprocess=not args.no_preprocess,
            do_deskew=not args.no_deskew,
            do_denoise=not args.no_denoise,
            use_adaptive=not args.otsu,
            contrast=not args.no_contrast,
            temp_dir=args.temp_dir
        )
        
        # Save results
        ocr_system.save_results(marks_data, args.output)
        
        # Display summary
        print("\n" + "="*60)
        print("🎓 MARKS CARD OCR EXTRACTION COMPLETE")
        print("="*60)
        print(f"📊 Total Text Elements: {len(marks_data.all_extracted_text)}")
        print(f"🎓 University: {marks_data.university}")
        print(f"👤 Student Name: {marks_data.student_info.name}")
        print(f"🆔 Roll Number: {marks_data.student_info.roll_number}")
        print(f"📚 Subjects Found: {len(marks_data.subjects)}")
        print(f"📋 Result: {marks_data.result}")
        print(f"📂 Output Directory: {args.output}")
        print("="*60)
        
    except Exception as e:
        logger.error(f"❌ Application error: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()