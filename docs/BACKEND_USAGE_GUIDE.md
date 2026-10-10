# OCR Marks Card Extractor - Usage Guide

## 🚀 Quick Start

### 1. Activate Virtual Environment
Always run commands from within the virtual environment:

```bash
# Windows
myenv\Scripts\activate
```

### 2. Basic Usage Examples

#### Command Line Usage
```bash
# Extract from a single image
python ocr_extractor.py path/to/marks_card.jpg

# Save results to JSON file
python ocr_extractor.py path/to/marks_card.jpg -o results.json

# Save results to CSV file  
python ocr_extractor.py path/to/marks_card.jpg -o results.csv -f csv

# Use higher confidence threshold for better accuracy
python ocr_extractor.py path/to/marks_card.jpg -c 0.8
```

#### Python Script Usage
```python
from ocr_extractor import MarksCardOCRExtractor

# Initialize extractor
extractor = MarksCardOCRExtractor()

# Process a marks card
result = extractor.process_marks_card("marks_card.jpg")

# Print extracted data
print(result)

# Save results
extractor.save_results(result, "output.json", "json")
```

### 3. Expected Output Structure

The extractor returns structured data in this format:

```json
{
  "student_info": {
    "name": "John Doe",
    "roll_number": "2023001",
    "class": "12th Science",
    "school": "ABC High School"
  },
  "academic_info": {
    "academic_year": "2023-2024",
    "examination": "Annual Examination"
  },
  "subjects_marks": {
    "Mathematics": {
      "obtained_marks": 95,
      "total_marks": 100,
      "percentage": 95.0,
      "confidence": 0.95
    },
    "Physics": {
      "obtained_marks": 88,
      "total_marks": 100,
      "percentage": 88.0,
      "confidence": 0.92
    }
  },
  "summary": {
    "total_obtained": 450,
    "total_maximum": 500,
    "percentage": 90.0,
    "grade": "A+"
  }
}
```

### 4. File Structure
```
Sih-2025/
├── myenv/                  # Virtual environment
├── ocr_extractor.py        # Main OCR module
├── demo.py                 # Demo script
├── test_installation.py    # Test script
├── requirements.txt        # Dependencies
├── README.md               # Documentation
├── sample_marks_cards/     # Input images folder
├── output/                 # Results folder
└── logs/                   # Log files
```

### 5. Supported Features

✅ **Text Extraction**: High-accuracy OCR using PaddleOCR  
✅ **Field Detection**: Automatic extraction of student info, marks, grades  
✅ **Image Preprocessing**: Noise reduction, contrast enhancement, deskewing  
✅ **Multiple Formats**: JSON and CSV output  
✅ **Batch Processing**: Process multiple images at once  
✅ **Error Handling**: Robust error management and logging  
✅ **Confidence Scoring**: Quality metrics for extracted text  

### 6. Tips for Best Results

1. **Image Quality**: Use clear, well-lit images
2. **Resolution**: Higher resolution images work better
3. **Orientation**: Ensure marks cards are properly oriented
4. **Format**: JPG, PNG, TIFF formats are recommended
5. **Confidence**: Use higher confidence thresholds (0.7-0.9) for critical applications

### 7. Troubleshooting

#### Common Issues:
- **No text extracted**: Check image quality and orientation
- **Low accuracy**: Increase confidence threshold or improve image quality
- **Missing fields**: Verify marks card format is supported
- **Import errors**: Ensure virtual environment is activated

#### Error Logs:
Check `ocr_extractor.log` for detailed error information.

### 8. Advanced Usage

#### Custom Configuration:
```python
# High accuracy mode
extractor = MarksCardOCRExtractor(
    confidence_threshold=0.8,
    lang='en'
)

# Batch processing
for image_file in image_list:
    result = extractor.process_marks_card(image_file)
    # Process result...
```

### 9. Performance Notes

- **First Run**: Initial model download may take 5-10 minutes
- **Subsequent Runs**: Much faster as models are cached locally
- **Processing Time**: Typically 2-5 seconds per image on CPU
- **Memory Usage**: ~500MB-1GB during processing

### 10. Support

For issues or questions:
1. Check the log files in `logs/` directory
2. Run `python test_installation.py` to verify setup
3. Review the demo script for examples: `python demo.py`