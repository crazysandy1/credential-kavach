#!/usr/bin/env python3
"""
OCR Text Extractor for Marks Cards using PaddleOCR
==================================================
This module provides comprehensive OCR functionality for extracting text
from marks cards with high accuracy and error handling.
"""

import os
import sys
import cv2
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import re
from datetime import datetime
import logging
from PIL import Image, ImageEnhance, ImageFilter
from paddleocr import PaddleOCR
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ocr_extractor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class MarksCardOCRExtractor:
    """
    A comprehensive OCR extractor specifically designed for marks cards.
    Provides image preprocessing, text extraction, and structured data output.
    """
    
    def __init__(self, 
                 lang: str = 'en',
                 use_angle_cls: bool = True,
                 use_gpu: bool = False,
                 confidence_threshold: float = 0.5):
        """
        Initialize the OCR extractor.
        
        Args:
            lang: Language for OCR recognition ('en' for English)
            use_angle_cls: Whether to use angle classification
            use_gpu: Whether to use GPU acceleration (may not be supported in all versions)
            confidence_threshold: Minimum confidence score for text detection
        """
        self.confidence_threshold = confidence_threshold
        self.lang = lang
        
        try:
            # Initialize PaddleOCR with minimal compatible parameters
            # Start with basic parameters that are widely supported
            ocr_params = {}
            
            # Add parameters one by one, handling compatibility issues
            if lang:
                ocr_params['lang'] = lang
            
            # Try angle classification if supported
            try:
                self.ocr = PaddleOCR(use_angle_cls=use_angle_cls, **ocr_params)
            except (TypeError, ValueError):
                # Fallback to basic initialization
                try:
                    self.ocr = PaddleOCR(**ocr_params)
                except:
                    # Ultimate fallback - basic PaddleOCR
                    self.ocr = PaddleOCR()
            
            logger.info(f"PaddleOCR initialized successfully with language: {lang}")
        except Exception as e:
            logger.error(f"Failed to initialize PaddleOCR: {str(e)}")
            raise
        
        # Common patterns for marks card fields
        self.patterns = {
            'roll_number': [
                r'roll\s*no\.?\s*:?\s*(\w+)',
                r'roll\s*number\s*:?\s*(\w+)',
                r'reg\s*no\.?\s*:?\s*(\w+)',
                r'registration\s*no\.?\s*:?\s*(\w+)',
                r'student\s*id\s*:?\s*(\w+)',
                r'id\s*no\.?\s*:?\s*(\w+)'
            ],
            'student_name': [
                r'name\s*:?\s*([A-Za-z\s\.]+)',
                r'student\s*name\s*:?\s*([A-Za-z\s\.]+)',
                r'candidate\s*name\s*:?\s*([A-Za-z\s\.]+)'
            ],
            'class': [
                r'class\s*:?\s*([A-Za-z0-9\s\-]+)',
                r'standard\s*:?\s*([A-Za-z0-9\s\-]+)',
                r'grade\s*:?\s*([A-Za-z0-9\s\-]+)'
            ],
            'school': [
                r'school\s*:?\s*([A-Za-z0-9\s\.,\-]+)',
                r'institution\s*:?\s*([A-Za-z0-9\s\.,\-]+)',
                r'college\s*:?\s*([A-Za-z0-9\s\.,\-]+)'
            ],
            'marks': [
                r'(\w+)\s+(\d+)\s*\/?\s*(\d+)?',
                r'(\w+)\s*:?\s*(\d+)',
                r'(\w+)\s+marks?\s*:?\s*(\d+)'
            ],
            'grade': [
                r'grade\s*:?\s*([A-F][+-]?)',
                r'overall\s*grade\s*:?\s*([A-F][+-]?)',
                r'final\s*grade\s*:?\s*([A-F][+-]?)'
            ],
            'percentage': [
                r'percentage\s*:?\s*(\d+\.?\d*)%?',
                r'(\d+\.?\d*)%',
                r'total\s*percentage\s*:?\s*(\d+\.?\d*)%?'
            ],
            'total_marks': [
                r'total\s*marks?\s*:?\s*(\d+)\s*\/?\s*(\d+)?',
                r'grand\s*total\s*:?\s*(\d+)\s*\/?\s*(\d+)?',
                r'aggregate\s*:?\s*(\d+)\s*\/?\s*(\d+)?'
            ]
        }

    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Preprocess the input image to improve OCR accuracy.
        
        Args:
            image_path: Path to the input image
            
        Returns:
            Preprocessed image as numpy array
        """
        try:
            # Read image
            if isinstance(image_path, str):
                image = cv2.imread(image_path)
            else:
                image = image_path
                
            if image is None:
                raise ValueError(f"Could not load image from {image_path}")
            
            # Convert to PIL Image for better preprocessing
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(pil_image)
            pil_image = enhancer.enhance(1.5)
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(pil_image)
            pil_image = enhancer.enhance(1.2)
            
            # Convert back to OpenCV format
            image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (1, 1), 0)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Morphological operations to clean up the image
            kernel = np.ones((1, 1), np.uint8)
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            # Deskew the image
            cleaned = self._deskew_image(cleaned)
            
            logger.info("Image preprocessing completed successfully")
            return cleaned
            
        except Exception as e:
            logger.error(f"Error in image preprocessing: {str(e)}")
            raise

    def _deskew_image(self, image: np.ndarray) -> np.ndarray:
        """
        Correct image skew by detecting text orientation.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Deskewed image
        """
        try:
            # Find all contours
            contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return image
            
            # Find the largest contour (assuming it's the document)
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Get the minimum area rectangle
            rect = cv2.minAreaRect(largest_contour)
            angle = rect[2]
            
            # Adjust angle for proper rotation
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle
            
            # Only rotate if angle is significant
            if abs(angle) > 0.5:
                height, width = image.shape[:2]
                center = (width // 2, height // 2)
                rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
                rotated = cv2.warpAffine(image, rotation_matrix, (width, height), 
                                       flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
                return rotated
            
            return image
            
        except Exception as e:
            logger.warning(f"Deskewing failed, using original image: {str(e)}")
            return image

    def extract_text(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Extract text from the image using PaddleOCR.
        
        Args:
            image_path: Path to the input image
            
        Returns:
            List of detected text with confidence scores and bounding boxes
        """
        try:
            # Preprocess image
            processed_image = self.preprocess_image(image_path)
            
            # Perform OCR using the recommended method
            try:
                # Try the newer predict method first
                if hasattr(self.ocr, 'predict'):
                    results = self.ocr.predict(processed_image)
                else:
                    results = self.ocr.ocr(processed_image)
            except Exception as e:
                logger.warning(f"OCR method failed: {e}, trying fallback")
                try:
                    results = self.ocr.ocr(processed_image)
                except:
                    results = self.ocr.predict(processed_image)
            
            # Debug: Log the structure of results
            logger.info(f"OCR results structure - Type: {type(results)}, Length: {len(results) if results else 0}")
            
            if not results:
                logger.warning("No text detected in the image")
                return []
            
            # Process results - Handle new PaddleOCR structure
            extracted_text = []
            
            # Get the first result (should be OCRResult object)
            result = results[0]
            
            # Handle different result types
            if hasattr(result, 'rec_texts') and hasattr(result, 'rec_scores'):
                # New PaddleOCR structure with OCRResult object
                texts = result.rec_texts
                scores = result.rec_scores
                bboxes = result.rec_polys if hasattr(result, 'rec_polys') else [[] for _ in texts]
                
                for i, (text, confidence) in enumerate(zip(texts, scores)):
                    # Filter by confidence threshold
                    if confidence >= self.confidence_threshold:
                        bbox = bboxes[i] if i < len(bboxes) else []
                        extracted_text.append({
                            'text': str(text).strip(),
                            'confidence': float(confidence),
                            'bbox': bbox.tolist() if hasattr(bbox, 'tolist') else bbox
                        })
                        
            else:
                # Fallback for older structure (list of lists)
                try:
                    if isinstance(result, list):
                        for line in result:
                            if line is None:
                                continue
                            
                            try:
                                # Handle different line structures
                                if len(line) == 2:
                                    bbox, text_info = line
                                    if isinstance(text_info, (list, tuple)) and len(text_info) == 2:
                                        text, confidence = text_info
                                    else:
                                        text = str(text_info)
                                        confidence = 1.0
                                else:
                                    bbox = line[0] if len(line) > 0 else []
                                    text = line[1] if len(line) > 1 else ""
                                    confidence = line[2] if len(line) > 2 else 1.0
                                
                                # Filter by confidence threshold
                                if confidence >= self.confidence_threshold:
                                    extracted_text.append({
                                        'text': str(text).strip(),
                                        'confidence': float(confidence),
                                        'bbox': bbox
                                    })
                                    
                            except Exception as e:
                                logger.warning(f"Error processing OCR result line: {e}")
                                continue
                except Exception as e:
                    logger.error(f"Error processing OCR results: {e}")
                    return []
            
            logger.info(f"Successfully extracted {len(extracted_text)} text elements")
            return extracted_text
            
        except Exception as e:
            logger.error(f"Error in text extraction: {str(e)}")
            raise

    def extract_marks_card_fields(self, extracted_text: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract specific fields from marks card text.
        
        Args:
            extracted_text: List of extracted text elements
            
        Returns:
            Dictionary containing structured marks card data
        """
        try:
            # Combine all text for pattern matching
            full_text = ' '.join([item['text'] for item in extracted_text]).lower()
            
            # Initialize result structure
            marks_card_data = {
                'student_info': {},
                'academic_info': {},
                'subjects_marks': {},
                'summary': {},
                'extraction_metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'total_text_elements': len(extracted_text),
                    'confidence_scores': [item['confidence'] for item in extracted_text]
                }
            }
            
            # Extract student information
            marks_card_data['student_info'] = self._extract_student_info(full_text, extracted_text)
            
            # Extract academic information
            marks_card_data['academic_info'] = self._extract_academic_info(full_text, extracted_text)
            
            # Extract subject-wise marks
            marks_card_data['subjects_marks'] = self._extract_subject_marks(extracted_text)
            
            # Extract summary information
            marks_card_data['summary'] = self._extract_summary_info(full_text, extracted_text)
            
            logger.info("Successfully extracted marks card fields")
            return marks_card_data
            
        except Exception as e:
            logger.error(f"Error in field extraction: {str(e)}")
            raise

    def _extract_student_info(self, full_text: str, extracted_text: List[Dict[str, Any]]) -> Dict[str, str]:
        """Extract student personal information."""
        student_info = {}
        
        # Extract roll number
        for pattern in self.patterns['roll_number']:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                student_info['roll_number'] = match.group(1).strip()
                break
        
        # Extract student name
        for pattern in self.patterns['student_name']:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                student_info['name'] = match.group(1).strip().title()
                break
        
        # Extract class/grade
        for pattern in self.patterns['class']:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                student_info['class'] = match.group(1).strip()
                break
        
        # Extract school name
        for pattern in self.patterns['school']:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                student_info['school'] = match.group(1).strip().title()
                break
        
        return student_info

    def _extract_academic_info(self, full_text: str, extracted_text: List[Dict[str, Any]]) -> Dict[str, str]:
        """Extract academic session and examination information."""
        academic_info = {}
        
        # Look for academic year patterns
        year_pattern = r'(20\d{2}[-\s]?20\d{2})'
        year_match = re.search(year_pattern, full_text)
        if year_match:
            academic_info['academic_year'] = year_match.group(1)
        
        # Look for examination patterns
        exam_patterns = [
            r'(annual|half\s*yearly|quarterly|unit\s*test|mid\s*term|final)\s*exam',
            r'examination\s*:?\s*([A-Za-z\s]+)',
            r'term\s*:?\s*([A-Za-z\s\d]+)'
        ]
        
        for pattern in exam_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                academic_info['examination'] = match.group(1).strip().title()
                break
        
        return academic_info

    def _extract_subject_marks(self, extracted_text: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Extract subject-wise marks from the text."""
        subjects_marks = {}
        
        # Common subject keywords
        subject_keywords = [
            'english', 'mathematics', 'math', 'science', 'physics', 'chemistry',
            'biology', 'history', 'geography', 'hindi', 'sanskrit', 'computer',
            'social', 'drawing', 'art', 'physical', 'education', 'pe'
        ]
        
        for item in extracted_text:
            text = item['text'].lower().strip()
            
            # Look for subject and marks patterns
            for subject in subject_keywords:
                if subject in text:
                    # Try to find marks in the same line or nearby
                    marks_match = re.search(r'(\d+)\s*[/\\]?\s*(\d+)?', item['text'])
                    if marks_match:
                        obtained_marks = int(marks_match.group(1))
                        total_marks = int(marks_match.group(2)) if marks_match.group(2) else None
                        
                        subjects_marks[subject.title()] = {
                            'obtained_marks': obtained_marks,
                            'total_marks': total_marks,
                            'confidence': item['confidence']
                        }
                        
                        # Calculate percentage if total marks available
                        if total_marks:
                            percentage = round((obtained_marks / total_marks) * 100, 2)
                            subjects_marks[subject.title()]['percentage'] = percentage
        
        return subjects_marks

    def _extract_summary_info(self, full_text: str, extracted_text: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract summary information like total marks, percentage, grade."""
        summary = {}
        
        # Extract total marks
        for pattern in self.patterns['total_marks']:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                summary['total_obtained'] = int(match.group(1))
                if match.group(2):
                    summary['total_maximum'] = int(match.group(2))
                break
        
        # Extract percentage
        for pattern in self.patterns['percentage']:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                summary['percentage'] = float(match.group(1))
                break
        
        # Extract grade
        for pattern in self.patterns['grade']:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                summary['grade'] = match.group(1).upper()
                break
        
        # Calculate percentage if not found but total marks available
        if 'percentage' not in summary and 'total_obtained' in summary and 'total_maximum' in summary:
            summary['percentage'] = round((summary['total_obtained'] / summary['total_maximum']) * 100, 2)
        
        return summary

    def save_results(self, data: Dict[str, Any], output_path: str, format: str = 'json') -> None:
        """
        Save extracted data to file.
        
        Args:
            data: Extracted marks card data
            output_path: Path to save the output file
            format: Output format ('json' or 'csv')
        """
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if format.lower() == 'json':
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                    
            elif format.lower() == 'csv':
                # Flatten the data for CSV format
                flattened_data = self._flatten_data(data)
                df = pd.DataFrame([flattened_data])
                df.to_csv(output_path, index=False)
                
            logger.info(f"Results saved to {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}")
            raise

    def _flatten_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Flatten nested dictionary for CSV output."""
        flattened = {}
        
        for section, content in data.items():
            if isinstance(content, dict):
                for key, value in content.items():
                    if isinstance(value, dict):
                        for subkey, subvalue in value.items():
                            flattened[f"{section}_{key}_{subkey}"] = subvalue
                    else:
                        flattened[f"{section}_{key}"] = value
            else:
                flattened[section] = content
        
        return flattened

    def process_marks_card(self, 
                          image_path: str, 
                          output_path: Optional[str] = None,
                          output_format: str = 'json') -> Dict[str, Any]:
        """
        Complete pipeline to process a marks card image.
        
        Args:
            image_path: Path to the marks card image
            output_path: Optional path to save results
            output_format: Output format ('json' or 'csv')
            
        Returns:
            Extracted marks card data
        """
        try:
            logger.info(f"Processing marks card: {image_path}")
            
            # Validate input file
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            # Extract text from image
            extracted_text = self.extract_text(image_path)
            
            if not extracted_text:
                raise ValueError("No text could be extracted from the image")
            
            # Extract structured data
            marks_card_data = self.extract_marks_card_fields(extracted_text)
            
            # Save results if output path provided
            if output_path:
                self.save_results(marks_card_data, output_path, output_format)
            
            logger.info("Marks card processing completed successfully")
            return marks_card_data
            
        except Exception as e:
            logger.error(f"Error processing marks card: {str(e)}")
            raise


def main():
    """Main function for command line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='OCR Text Extractor for Marks Cards')
    parser.add_argument('image_path', help='Path to the marks card image')
    parser.add_argument('-o', '--output', help='Output file path')
    parser.add_argument('-f', '--format', choices=['json', 'csv'], default='json',
                       help='Output format (default: json)')
    parser.add_argument('-l', '--lang', default='en', help='OCR language (default: en)')
    parser.add_argument('-c', '--confidence', type=float, default=0.5,
                       help='Confidence threshold (default: 0.5)')
    parser.add_argument('--gpu', action='store_true', help='Use GPU acceleration')
    
    args = parser.parse_args()
    
    try:
        # Initialize extractor
        extractor = MarksCardOCRExtractor(
            lang=args.lang,
            use_gpu=args.gpu,
            confidence_threshold=args.confidence
        )
        
        # Process marks card
        result = extractor.process_marks_card(
            args.image_path,
            args.output,
            args.format
        )
        
        # Print summary
        print("\n" + "="*60)
        print("MARKS CARD EXTRACTION SUMMARY")
        print("="*60)
        
        if 'student_info' in result:
            print("\nSTUDENT INFORMATION:")
            for key, value in result['student_info'].items():
                print(f"  {key.replace('_', ' ').title()}: {value}")
        
        if 'academic_info' in result:
            print("\nACADEMIC INFORMATION:")
            for key, value in result['academic_info'].items():
                print(f"  {key.replace('_', ' ').title()}: {value}")
        
        if 'subjects_marks' in result and result['subjects_marks']:
            print("\nSUBJECT MARKS:")
            for subject, marks in result['subjects_marks'].items():
                obtained = marks.get('obtained_marks', 'N/A')
                total = marks.get('total_marks', 'N/A')
                percentage = marks.get('percentage', 'N/A')
                print(f"  {subject}: {obtained}/{total} ({percentage}%)")
        
        if 'summary' in result:
            print("\nSUMMARY:")
            for key, value in result['summary'].items():
                print(f"  {key.replace('_', ' ').title()}: {value}")
        
        print("\n" + "="*60)
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()