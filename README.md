# Answer Sheet Grading System
### WARNING: This project is a WIP.

A Python-based system for automatically grading multiple-choice answer sheets using computer vision.

## Project Structure

```
.
├── grade_it.py              # Main grading module
├── gen_gabarito.py          # Template generator
├── [testing]mark_gabarito.py # Answer sheet marker
├── test_venv.py            # Environment tester
├── requirements.txt        # Dependencies
└── templates/              # Generated files
    ├── gabarito_demo.png
    ├── gabarito_demo_positions.json
    └── marked_demo.png
```

## Quick Start

### 1. Set up the environment
```bash
# Install dependencies
pip install -r requirements.txt

# Test your environment
python test_venv.py
```

### 2. Generate an answer sheet template
```bash
python gen_gabarito.py
```
This creates:
- `templates/gabarito_demo.png` - Blank answer sheet
- `templates/gabarito_demo_positions.json` - Bubble position data

### 3. Create a marked answer sheet
```bash
python "[testing]mark_gabarito.py"
```
Choose interactive mode to enter answers or quick demo for predefined answers.

### 4. Grade the answer sheet
```bash
python grade_it.py
```

## Usage:

### 1: Generate Template
The system creates a standardized answer sheet with:
- 15 questions by default (configurable)
- 5 choices per question (A-E)
- Alignment marks for precise detection
- Header labels above each choice column

### 2: Mark Answers
Two ways to create marked sheets:

#### Option A: Interactive Mode
```bash
python "[testing]mark_gabarito.py"
```
- Enter answers for each question (A-E)
- Leave blank for unanswered questions
- Saves as `my_marked_sheet.png`

#### Option B: Quick Demo
```bash
python "[testing]mark_gabarito.py"
```
Choose option 2 for a pre-filled demo sheet.

### 3: Automatic Grading
```bash
python grade_it.py
```
The system:
1. Loads the marked answer sheet
2. Uses pre-stored bubble positions
3. Analyzes filled bubbles using computer vision
4. Compares against expected answers
5. Generates detailed grading report

## Configuration

### Customizing the Answer Sheet
Modify `gen_gabarito.py`:
```python
template_path, position_data = generate_gabarito_png_improved(
    "./templates/gabarito_demo.png", 
    num_questions=25,           # Change number of questions
    choices=("A", "B", "C", "D"), # Change choices
    add_reference_marks=True
)
```

### Adjusting Grading Sensitivity
In `grade_it.py`, modify the threshold:
```python
results = grade_gabarito_improved(
    image_path=marked_path,
    expected_answers=expected_answers,
    position_data=position_data,
    threshold=0.2,  # Lower = more sensitive, Higher = less sensitive
    debug=True
)
```

### Setting Expected Answers
Edit the `expected_answers` list in `grade_it.py`:
```python
expected_answers = ["A", "B", "C", "D", "E", "A", "B", "C", "D", "E"]
```

## Output

The grading system provides:

### Visual Debug Output
- **Green**: Correctly marked answer
- **Blue**: Correct answer (should have been marked)
- **Red**: Wrong answer marked by student
- **Orange**: Multiple answers marked
- **Gray**: Unmarked bubble

### Text Report
```
=== GRADE REPORT ===
Score: 8/10
Percentage: 80.0%
Multiple answers: 1
Unanswered: 0

=== DETAILED RESULTS ===
Q01: ○ Student=A    Correct=A
Q02: X Student=B    Correct=A (marked: 0.85, correct: 0.12)
...
```

## Technical Details

### Dependencies
- OpenCV 4.8.1.78 - Image processing
- Pillow 10.0.1 - Image manipulation
- NumPy 1.24.3 - Numerical operations

### Image Processing Pipeline
1. *Preprocessing*: Convert to grayscale + adaptive thresholding
2. *Noise Removal*: Morphological operations to clean image
3. *Bubble Detection*: Use pre-stored positions for precision
4. *Fill Analysis*: Calculate filled pixel ratio per bubble
5. *Grading Logic*: Compare against expected answers

### File Formats
- **PNG Images**: 300 DPI for high resolution
- **JSON Position Data**: Stores exact bubble coordinates
- **Standardized Layout**: Consistent positioning for reliable grading

## Troubleshooting

### Common Issues

**"Template file not found"**
- Run `gen_gabarito.py` first to generate templates

**"Could not load image"**
- Check file paths in the scripts
- Ensure images are in PNG format

**Poor detection accuracy**
- Adjust the `threshold` parameter (0.1-0.3)
- Use high-contrast, clean scans
- Ensure bubbles are fully filled with dark ink

**Font warnings**
- System will use default fonts if Arial not available
- Does not affect functionality

## 📝 Customization

### Adding More Questions
```python
# In gen_gabarito.py
num_questions=50  # Increase as needed
```

### Choice Options
```python
# In both gen_gabarito.py and grade_it.py
choices=("1", "2", "3", "4")  # For numeric choices
```

### Layout
Modify the `generate_gabarito_png_improved` function to adjust:
- Margins and spacing
- Bubble sizes
- Page dimensions
- Header/footer content

## Workflow Summary

1. Setup: Install dependencies → Generate template
2. Preparation: Print template → Students mark answers
3. Digitization: Scan marked sheets as PNG files
4. Grading: Run grading script → Get instant results
5. Analysis: Review detailed reports and visual feedback

The code is designed for educational institutions, standardized testing, and any scenario requiring efficient multiple-choice answer sheet processing.
