import os
import sys
import fitz  # PyMuPDF for PDF processing
import time
from PIL import Image, ImageChops
from time import time


# --- SETTINGS FILE HANDLING --- #
def read_settings_file(settings_file="Settings.txt"):
    """
    Reads Settings.txt to get the base folder and exclusion identifiers based on specific keys.
    Returns:
    - base_path (str): Path to the folder to process, identified by the "Path2Files:" key.
    - exclusion_list (list): List of substrings to exclude from XML line comparisons, identified by the "Exclude:" key.
    """
    app_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
    settings_path = os.path.join(app_dir, settings_file)

    if not os.path.exists(settings_path):
        raise FileNotFoundError(f"Settings file not found: {settings_path}")

    # Initialize variables to store the settings
    base_path = None
    exclusion_list = []

    # Read and parse the settings file
    with open(settings_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):  # Skip empty lines and comments
                continue

            # Check for the "Path2Files:" key
            if line.startswith("Path2Files:"):
                base_path = line.split("Path2Files:", 1)[1].strip()

            # Check for the "Exclude:" key
            elif line.startswith("Exclude:"):
                exclusions = line.split("Exclude:", 1)[1].strip()
                exclusion_list = [item.strip() for item in exclusions.split(",") if item.strip()]

    # Validate that the required settings are present
    if not base_path:
        raise ValueError("Settings.txt must specify a base folder path using the 'Path2Files:' key.")
        input("\nPress Enter to close the application...")
    if not os.path.exists(base_path):
        raise FileNotFoundError(f"Specified folder does not exist: {base_path}")
        input("\nPress Enter to close the application...")

    return base_path, exclusion_list


def validate_folder(base_path):
    """
    Validate that the folder contains only XML or PDF files.
    Returns:
    - xml_files: List of XML files found in the hierarchy.
    - pdf_files: List of PDF files found in the hierarchy.
    - invalid_files: List of unsupported files detected.
    """
    xml_files = []
    pdf_files = []
    invalid_files = []

    for root, _, files in os.walk(base_path):
        for f in files:
            f_path = os.path.join(root, f)
            if f.endswith(".xml"):
                xml_files.append(f_path)
            elif f.endswith(".pdf"):
                pdf_files.append(f_path)
            else:
                invalid_files.append(f_path)

    return xml_files, pdf_files, invalid_files


# --- XML COMPARISON LOGIC --- #
def parse_xml_with_line_numbers(file_path):
    """
    Reads XML preserving line numbers. Returns:
    - List of tuples: [(line_number, line_content)].
    """
    with open(file_path, 'r', encoding="utf-8") as f:
        return [(i + 1, line.strip()) for i, line in enumerate(f)]


def filter_lines(lines, exclusion_list):
    """
    Filters XML lines excluding content containing the specified substrings.
    """
    return [
        (line_num, line_content)
        for line_num, line_content in lines
        if not any(exclusion in line_content for exclusion in exclusion_list)
    ]


def compare_xml_files(file1, file2, output_folder, exclusion_list):
    """
    Compares XML files line-by-line and writes results into output folder.
    """
    lines_file1 = parse_xml_with_line_numbers(file1)
    lines_file2 = parse_xml_with_line_numbers(file2)

    filtered_file1 = filter_lines(lines_file1, exclusion_list)
    filtered_file2 = filter_lines(lines_file2, exclusion_list)

    unique_lines_file1 = [
        (num, content) for num, content in filtered_file1 if content not in {c for _, c in filtered_file2}
    ]
    unique_lines_file2 = [
        (num, content) for num, content in filtered_file2 if content not in {c for _, c in filtered_file1}
    ]

    identical = len(unique_lines_file1) == 0 and len(unique_lines_file2) == 0
    result_file = os.path.join(output_folder, f"xml_comparison_{os.path.basename(file1)}_vs_{os.path.basename(file2)}.txt")
    with open(result_file, 'w', encoding="utf-8") as f:
        f.write(f"Files are identical: {identical}\n\n")
        f.write(f"Total lines in File 1 {file1}: {len(lines_file1)}\n")
        f.write(f"Total lines in File 2 {file2}: {len(lines_file2)}\n\n")

        f.write("Distinctive lines in File 1:\n")
        for num, content in unique_lines_file1:
            f.write(f"  Line {num}: {content}\n")
        f.write("\nDistinctive lines in File 2:\n")
        for num, content in unique_lines_file2:
            f.write(f"  Line {num}: {content}\n")
    print(f"XML comparison result saved: {result_file}")


# --- PDF COMPARISON LOGIC --- #
def extract_text_by_page(file_path):
    """
    Extracts text from each page of a PDF file.
    Returns a dictionary {page_number: text}.
    """
    pdf = fitz.open(file_path)
    text_by_page = {
        page_num + 1: page.get_text("text").strip()
        for page_num, page in enumerate(pdf)
    }
    pdf.close()
    return text_by_page


def compare_pdf_text(text_file1, text_file2):
    """
    Compares text page-by-page between two PDF files.
    Returns dictionaries of differences for File 1 and File 2.
    """
    unique_texts_file1 = {}
    unique_texts_file2 = {}

    all_pages = set(text_file1.keys()).union(set(text_file2.keys()))  # Union of page numbers
    for page_num in all_pages:
        text1 = text_file1.get(page_num, "")
        text2 = text_file2.get(page_num, "")

        unique_in_file1 = "\n".join(line for line in text1.splitlines() if line not in text2.splitlines())
        unique_in_file2 = "\n".join(line for line in text2.splitlines() if line not in text1.splitlines())

        if unique_in_file1:
            unique_texts_file1[page_num] = unique_in_file1
        if unique_in_file2:
            unique_texts_file2[page_num] = unique_in_file2

    return unique_texts_file1, unique_texts_file2


def compare_metadata(file1, file2):
    """
    Compares PDF metadata: number of pages and file size.
    """
    pdf1 = fitz.open(file1)
    pdf2 = fitz.open(file2)

    differences = {}
    if len(pdf1) != len(pdf2):
        differences["Page Count"] = (len(pdf1), len(pdf2))
    size1 = os.path.getsize(file1)
    size2 = os.path.getsize(file2)
    if size1 != size2:
        differences["File Size"] = (size1, size2)

    pdf1.close()
    pdf2.close()

    return differences


def compare_pdfs(file1, file2, output_folder):
    """
    Compares PDF files (text & metadata) and saves results in output folder.
    """
    text1 = extract_text_by_page(file1)
    text2 = extract_text_by_page(file2)
    unique_text_file1, unique_text_file2 = compare_pdf_text(text1, text2)

    metadata_differences = compare_metadata(file1, file2)

    result_file = os.path.join(output_folder, f"pdf_comparison_{os.path.basename(file1)}_vs_{os.path.basename(file2)}.txt")
    with open(result_file, 'w', encoding="utf-8") as f:

        f.write(f"Comparison result for PDF files:\nFile 1: {file1}\nFile 2: {file2}\n\n")
        f.write("=== TEXT DIFFERENCES ===\n\n")
        f.write("Unique text in File 1:\n\n\n")
        for page, text in unique_text_file1.items():
            f.write(f"Page {page}:\n{text}\n\n")
        f.write("Unique text in File 2:\n\n\n")
        for page, text in unique_text_file2.items():
            f.write(f"Page {page}:\n{text}\n\n")

        f.write("=== METADATA DIFFERENCES ===\n\n")
        for key, value in metadata_differences.items():
            f.write(f"{key}: {value}\n")

    print(f"PDF comparison result saved: {result_file}")


# --- MAIN PROCESSING FUNCTION --- #

def process_files(base_path, exclusion_list):
    """
    Processes XML and PDF files for pairwise comparison.
    Results are stored in the directories where files are found.
    Produces a summary report at the end of processing.
    Optimized to reduce redundant folder scans and comparisons.
    """
    mixed_folders = []  # Track folders with both XML and PDF files
    unsupported_files = []  # Log unsupported files for summary
    processed_xml_count = 0  # Total XML files processed
    processed_pdf_count = 0  # Total PDF files processed

    # Start performance tracking
    start_time = time()

    for root, _, files in os.walk(base_path):
        # Step 1: Classify Files
        xml_files_in_dir = [os.path.join(root, f) for f in files if f.endswith(".xml")]
        pdf_files_in_dir = [os.path.join(root, f) for f in files if f.endswith(".pdf")]
        invalid_files_in_dir = [os.path.join(root, f) for f in files if not f.endswith(".xml") and not f.endswith(".pdf")]

        # Log Unsupported Files
        if invalid_files_in_dir:
            unsupported_files.extend(invalid_files_in_dir)

        # Handle Mixed File Types in the Same Folder
        if xml_files_in_dir and pdf_files_in_dir:
            mixed_folders.append(root)
            print(f"Warning: Mixed XML and PDF files detected in folder '{root}'. Skipping this folder.")
            continue

        # Step 2: Process XML Files
        if xml_files_in_dir:
            print(f"Processing {len(xml_files_in_dir)} XML files in folder '{root}'...")
            processed_xml_count += len(xml_files_in_dir)
            for i in range(len(xml_files_in_dir)):
                for j in range(i + 1, len(xml_files_in_dir)):
                    compare_xml_files(xml_files_in_dir[i], xml_files_in_dir[j], root, exclusion_list)

        # Step 3: Process PDF Files
        if pdf_files_in_dir:
            print(f"Processing {len(pdf_files_in_dir)} PDF files in folder '{root}'...")
            processed_pdf_count += len(pdf_files_in_dir)
            for i in range(len(pdf_files_in_dir)):
                for j in range(i + 1, len(pdf_files_in_dir)):
                    compare_pdfs(pdf_files_in_dir[i], pdf_files_in_dir[j], root)

    # End performance tracking
    end_time = time()
    processing_time = end_time - start_time

    # Generate Summary Report
    print("\n--- Summary Report ---")
    print(f"Total XML files processed: {processed_xml_count}")
    print(f"Total PDF files processed: {processed_pdf_count}")
    if mixed_folders:
        print(f"Folders with mixed XML and PDF files (skipped):")
        for folder in mixed_folders:
            print(f"  {folder}")
    if unsupported_files:
        print(f"Unsupported files detected but skipped:")
        for f in unsupported_files:
            print(f"  {f}")
    print(f"Processing Time: {processing_time:.2f} seconds")
    print("All files processed successfully.")
    input("\nPress Enter to close the application...")


# --- Text Extraction and Comparison Functions --- #
def extract_text_by_page(file_path):
    """
    Extract text content from each page of a PDF file.
    Returns:
    - Dictionary {page_number: normalized text}.
    """
    pdf_document = fitz.open(file_path)
    text_by_page = {}

    for page_num, page in enumerate(pdf_document, start=1):
        text = page.get_text("text").strip()  # Extract plain text from the page
        text_by_page[page_num] = normalize_text(text)  # Normalize text for comparison

    pdf_document.close()
    return text_by_page


def normalize_text(text):
    """
    Normalize text by removing extra whitespace and sorting lines.
    This helps avoid false-positive differences caused by formatting inconsistencies.
    """
    normalized = "\n".join(sorted(line.strip() for line in text.splitlines() if line.strip()))
    return normalized


def compare_text_by_page(file1_text, file2_text):
    """
    Compare text between two PDF files page-by-page.
    Returns:
    - Dictionary of unique text lines in File 1 per page.
    - Dictionary of unique text lines in File 2 per page.
    """
    unique_text_file1 = {}
    unique_text_file2 = {}

    all_pages = set(file1_text.keys()).union(set(file2_text.keys()))  # Combine all pages
    for page_num in all_pages:
        text1 = file1_text.get(page_num, "")
        text2 = file2_text.get(page_num, "")

        # Lines unique to File 1
        unique_in_file1 = "\n".join(line for line in text1.splitlines() if line not in text2.splitlines())
        # Lines unique to File 2
        unique_in_file2 = "\n".join(line for line in text2.splitlines() if line not in text1.splitlines())

        if unique_in_file1.strip():
            unique_text_file1[page_num] = unique_in_file1
        if unique_in_file2.strip():
            unique_text_file2[page_num] = unique_in_file2

    return unique_text_file1, unique_text_file2


# --- Image Extraction and Comparison Functions --- #
def extract_images_by_page(file_path, output_folder):
    """
    Extract images embedded in each page of a PDF file and save them to a temporary folder.
    Returns:
    - Dictionary {page_number: [image_paths]}.
    """
    pdf_document = fitz.open(file_path)
    images_by_page = {}

    for page_num, page in enumerate(pdf_document, start=1):
        images = page.get_images(full=True)
        image_paths = []

        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            output_file = os.path.join(output_folder, f"page_{page_num}_img_{img_index + 1}.{image_ext}")

            with open(output_file, "wb") as img_file:
                img_file.write(image_bytes)

            image_paths.append(output_file)  # Add to the list of extracted images

        if image_paths:
            images_by_page[page_num] = image_paths

    pdf_document.close()
    return images_by_page


def compare_images_by_page(images1, images2):
    """
    Compare images page-by-page between two PDF files.
    Identifies unique images and pixel mismatched images.
    Returns:
    - Unique images in File 1 (dictionary by page).
    - Unique images in File 2 (dictionary by page).
    - Pixel-mismatched images.
    """
    unique_images_file1 = {}
    unique_images_file2 = {}
    mismatched_images = []

    all_pages = set(images1.keys()).union(set(images2.keys()))  # Union of pages
    for page_num in all_pages:
        images_file1 = images1.get(page_num, [])
        images_file2 = images2.get(page_num, [])

        # Find unique images on corresponding pages
        unique_to_file1 = set(images_file1) - set(images_file2)
        unique_to_file2 = set(images_file2) - set(images_file1)

        if unique_to_file1:
            unique_images_file1[page_num] = list(unique_to_file1)
        if unique_to_file2:
            unique_images_file2[page_num] = list(unique_to_file2)

        # Compare images pixel-by-pixel
        for img1, img2 in zip(images_file1, images_file2):
            try:
                image1 = Image.open(img1).convert("RGB")
                image2 = Image.open(img2).convert("RGB")

                # Compare pixel mismatches
                diff = ImageChops.difference(image1, image2)
                if diff.getbbox():  # If there's a visible mismatch
                    mismatched_images.append({
                        "page": page_num,
                        "file1_image": img1,
                        "file2_image": img2
                    })
            except Exception as e:
                print(f"Error comparing images {img1} vs {img2}: {e}")

    return unique_images_file1, unique_images_file2, mismatched_images


# --- Metadata Comparison --- #
def compare_metadata(file1, file2):
    """
    Compare PDF metadata: number of pages and file size.
    Returns:
    - Dictionary containing metadata differences.
    """
    pdf1 = fitz.open(file1)
    pdf2 = fitz.open(file2)

    differences = {}
    if len(pdf1) != len(pdf2):
        differences["Page Count"] = (len(pdf1), len(pdf2))
    size1 = os.path.getsize(file1)
    size2 = os.path.getsize(file2)
    if size1 != size2:
        differences["File Size (bytes)"] = (size1, size2)

    pdf1.close()
    pdf2.close()
    return differences


# --- PDF Comparison Driver --- #
def compare_pdfs(file1, file2, output_folder):
    """
    Compares text, images, and metadata between two PDF files.
    Stores results in the directory where the files reside.
    """
    # Extract and compare text
    text_file1 = extract_text_by_page(file1)
    text_file2 = extract_text_by_page(file2)
    unique_text_file1, unique_text_file2 = compare_text_by_page(text_file1, text_file2)

    # Extract images
    folder1 = os.path.join(output_folder, f"images_{os.path.basename(file1).split('.')[0]}")
    folder2 = os.path.join(output_folder, f"images_{os.path.basename(file2).split('.')[0]}")
    os.makedirs(folder1, exist_ok=True)
    os.makedirs(folder2, exist_ok=True)
    images_file1 = extract_images_by_page(file1, folder1)
    images_file2 = extract_images_by_page(file2, folder2)

    # Compare images
    unique_images_file1, unique_images_file2, mismatched_images = compare_images_by_page(images_file1, images_file2)

    # Compare metadata
    metadata_differences = compare_metadata(file1, file2)

    # Write results
    result_file = os.path.join(output_folder, f"pdf_comparison_{os.path.basename(file1)}_vs_{os.path.basename(file2)}.txt")
    with open(result_file, 'w', encoding="utf-8") as f:
        f.write(f"Comparison result for PDF files:\nFile 1: {file1}\nFile 2: {file2}\n\n")

        f.write("=== TEXT DIFFERENCES ===\n")
        f.write("Unique text in File 1:\n")
        for page, text in unique_text_file1.items():
            f.write(f"\n Page {page}:\n{text}\n")
        f.write("\nUnique text in File 2:\n")
        for page, text in unique_text_file2.items():
            f.write(f"\n Page {page}:\n{text}\n\n")

        f.write("=== IMAGE DIFFERENCES ===\n")
        f.write("Unique images in File 1:\n")
        for page, images in unique_images_file1.items():
            f.write(f"Page {page}: {', '.join(images)}\n")
        f.write("\nUnique images in File 2:\n")
        for page, images in unique_images_file2.items():
            f.write(f"Page {page}: {', '.join(images)}\n")
        f.write("\nMismatched Images:\n")
        for mismatch in mismatched_images:
            f.write(f"Page {mismatch['page']}:\nFile 1 Image: {mismatch['file1_image']}\nFile 2 Image: {mismatch['file2_image']}\n\n")

        f.write("=== METADATA DIFFERENCES ===\n")
        for key, value in metadata_differences.items():
            f.write(f"{key}: {value}\n")

    print(f"PDF comparison result saved: {result_file}")

# --- ENTRY POINT --- #
if __name__ == "__main__":
    try:
        base_path, exclusion_list = read_settings_file()
        process_files(base_path, exclusion_list)
    except Exception as e:
        print(f"Error: {e}")
        input("\nPress Enter to close the application...")