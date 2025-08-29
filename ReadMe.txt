ReadMe for XML and PDF Comparison Application
Overview
This application is designed to compare XML and PDF files within a specified folder. It performs pairwise comparisons of files, identifies differences, and generates detailed reports. The application supports text-based comparisons for XML files and both text and image-based comparisons for PDF files. Additionally, it validates metadata differences between PDF files.

Features
XML File Comparison:

Compares XML files line-by-line.
Filters lines based on exclusion substrings specified in the Settings.txt file.
Identifies unique lines in each file and generates a comparison report.
PDF File Comparison:

Compares text content page-by-page.
Extracts and compares embedded images page-by-page.
Compares metadata such as page count and file size.
Generates a detailed comparison report.
File Validation:

Ensures that only XML and PDF files are processed.
Logs unsupported files for review.
Settings File:

Configurable settings via Settings.txt.
Allows specification of the folder to process and exclusion substrings.
Error Handling:

Provides meaningful error messages for missing files, invalid folders, or unsupported file formats.
Installation
Prerequisites
Python 3.7 or higher.
Required Python libraries:
PyMuPDF (fitz) for PDF processing.
Pillow for image manipulation.
Standard libraries (os, sys, time).
Install Dependencies
Run the following command to install the required libraries:

bash


pip install pymupdf pillow
Usage
Step 1: Configure Settings.txt
Create a Settings.txt file in the same directory as the application. Use the following format:



# Path to the folder containing XML and PDF files
Path2Files: /path/to/your/folder

# Substrings to exclude during XML comparisons
Exclude: temp, backup, draft
Path2Files: Specify the folder containing the files to process.
Exclude: Provide a comma-separated list of substrings to exclude during XML comparisons.
Step 2: Run the Application
Run the application using the following command:

bash


python your_script_name.py
Step 3: Review Results
Comparison reports are saved in the same directory as the files being compared.
Reports include detailed differences for XML and PDF files.
Output
XML Comparison Report
File Name: xml_comparison_<file1>_vs_<file2>.txt
Contents:
Whether the files are identical.
Total lines in each file.
Lines unique to each file.
PDF Comparison Report
File Name: pdf_comparison_<file1>_vs_<file2>.txt
Contents:
Text differences (unique text per page).
Image differences (unique images and pixel mismatches).
Metadata differences (page count, file size).
Error Handling
The application handles the following errors gracefully:

Missing Settings.txt:

Error: Settings file not found.
Solution: Ensure Settings.txt exists in the application directory.
Invalid Folder Path:

Error: Specified folder does not exist.
Solution: Verify the folder path in Settings.txt.
Unsupported Files:

Unsupported files are logged but skipped during processing.
Mixed XML and PDF Files:

Folders containing both XML and PDF files are skipped to avoid ambiguity.
Example
Settings File (Settings.txt):


Path2Files: /home/user/documents
Exclude: temp, backup, draft
Folder Structure:


/home/user/documents/
├── file1.xml
├── file2.xml
├── file1.pdf
├── file2.pdf
├── unsupported_file.txt
Output:
XML Comparison Report:

xml_comparison_file1.xml_vs_file2.xml.txt
Contains line-by-line differences.
PDF Comparison Report:

pdf_comparison_file1.pdf_vs_file2.pdf.txt
Contains text, image, and metadata differences.
Performance
The application is optimized for large folders:

Processes files in parallel within the same folder.
Avoids redundant scans and comparisons.
Limitations
Mixed File Types:

Folders containing both XML and PDF files are skipped.
Image Comparison:

Pixel mismatches are detected but not quantified.
Exclusion List:

Exclusion substrings apply only to XML files.
Contact
For questions or issues, please contact:

Email: support@example.com
GitHub: GitHub Repository


