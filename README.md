# Lab1_p.miyienda-dotcom
# Lab 1 - Grade Evaluator & Archiver

**Course:** Introduction to Python Programming and Databases  
**Programme:** BSE Year 1 - Trimester 2

## Project Structure

'''
lab1   # directory
grade-evaluator.py  # Main Python application
organizer.sh       # Bash archival script
grades.csv       # Input data file
README.md
'''

## 1 - Running the Python Grade Evaluator

### Prerequisites
-Python 3.8+  
-No external packages required (uses `csv`, `os`, `sys` from the standard library)

### Steps

'''bash
Save any changes made in any file individually by pressing Ctrl+S before running
python3 grade-evaluator.py
'''

When prompted, enter the name of the CSV file:
'''
Enter the name of the CSV file to process (e.g., grades.csv): grades.csv
'''

### What it does
1. **Score Validation**  - Flags any score outside 0–100 
2. **Weight Validation**  - Checks total = 100, Summative = 40, Formative = 60
3. **GPA Calculation** - GPA = (Final Grade / 100) × 5.0
4. **Pass / Fail** - Must score ≥ 50% in **both** categories 
5. **Resubmission** - Identifies failed formative assignments with the highest weight

### Expected grades.csv format

'''csv
assignment, group, score, weight
Quiz, Formative,85,20
Group Exercise, Formative,40,20
Functions and Debugging Lab, Formative,45,20
Midterm Project - Simple Calculator, Summative,70,20
Final Project - Text-Based Game, Summative,60,20
'''



## 2 - Running the Shell Script Organizer

### Prerequisites
- Bash (Linux / macOS / WSL)

### Steps

'''
bash
chmod +x organizer.sh   # only needed once
./organizer.sh
'''

### What it does

1. **Creates** an archive directory if it does not exist  
2. **Renames** grades.csv → grades_YYYYMMDD-HHMMSS.csv and moves it to archive directory
3. **Creates** a fresh empty grades.csv ready for the next batch  
4. **Appends** a log entry to organizer.log.

### Sample organizer.log entry

'''
Timestamp: 20251105-170000
Original File: grades.csv
Archived as: archive/grades_20251105-170000.csv
'''



## Sample Output
'''
GRADE EVALUATION REPORT
Score Validation
All scores are valid (0–100)

 **Weight Validation**
Total weight: 100.0%  (expected 100%)
Summative weight: 40.0%  (expected 40%)
Formative weight: 60.0%  (expected 60%)

Final Grade & GPA
Final Grade: 60.00%
GPA         : 3.00 / 5.0

Category Scores
Summative: 65.00%
Formative: 56.67%

FINAL DECISION SUMMARY
Final Grade : 60.00%
GPA            : 3.00 / 5.0
Summative Score: 65.00%
Formative Score: 56.67%

FINAL DECISION: PASSED
The student met the 50% threshold in both categories.

FAILED FORMATIVE ASSIGNMENTS:
-Group Exercise: Score = 40.0%, Weight = 20%
-Functions and Debugging Lab: Score = 45.0%, Weight = 20%

RESUBMISSION ELIGIBLE:
(tied at the highest weight of 20%)
Group Exercise: Score = 40.0%, Weight = 20%
Functions and Debugging Lab: Score = 45.0%, Weight = 20%
'''
