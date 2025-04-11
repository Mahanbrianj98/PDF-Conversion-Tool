# Conversion Program
# Version 0.0.4
# This program processes PDF files, extracts text, and performs OCR on images.
# It includes a GUI for user interaction and multithreading for performance.
# Changelog from 0.0.3 to 0.0.4:
# - Added Multithreading support for faster processing.
# - Improved error handling and logging.


import os
import fitz
from pdfminer.high_level import extract_text
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
import logging
from tkinter import Tk, Toplevel, ttk
from tkinter.filedialog import askopenfilename, askdirectory
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(
    filename='pdf_processing.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Set the path for Tesseract OCR (adjust if needed)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Function to normalize and resolve file paths
def normalize_path(file_path):
    file_path = file_path.strip()
    normalized_path = os.path.normpath(file_path)
    forward_slash_path = normalized_path.replace("\\", "/")
    resolved_path = os.path.abspath(forward_slash_path)
    return resolved_path

# Function to create output directory if it doesn't exist
def create_output_folder(folder_name):
    try:
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        logging.info(f"Output folder '{folder_name}' created successfully.")
    except OSError as e:
        logging.error(f"Error creating folder {folder_name}: {e}")
        print(f"Error creating folder {folder_name}: {e}")
        return False
    return True

# Function to search for a series of numbers with a configurable pattern
def find_series_of_numbers(text, pattern=r'\d{10}'):
    import re
    match = re.search(pattern, text)
    return match.group() if match else None

# Function to extract text from a PDF page using pdfminer
def extract_text_from_pdf(pdf_path, page_number):
    try:
        return extract_text(pdf_path, page_numbers=[page_number - 1])  # PDF pages are 0-indexed
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {e}")
        return ""

# Function to extract text from an image using OCR
def extract_text_with_ocr(image):
    try:
        return pytesseract.image_to_string(image, lang='eng')
    except Exception as e:
        logging.error(f"Error extracting text with OCR: {e}")
        return ""

# Function to crop an image with user-specified ratio
def crop_image(image, crop_ratio=0.95):
    img_width, img_height = image.size
    crop_box = (0, 0, img_width * crop_ratio, img_height * crop_ratio)
    return image.crop(crop_box)

# Multithreaded PDF Processing Function
def process_pdf_multithreaded(pdf_path, output_folder, number_pattern, crop_ratio):
    try:
        reader = fitz.open(pdf_path)  # Open the PDF
        if not create_output_folder(output_folder):  # Validate output folder
            return

        # Tkinter pop-up for progress tracking
        progress_window = Toplevel()
        progress_window.title("Processing Progress")
        progress_label = ttk.Label(progress_window, text="Processing pages...")
        progress_label.pack(pady=10)

        progress_bar = ttk.Progressbar(progress_window, orient="horizontal", length=300, mode="determinate")
        progress_bar.pack(pady=10)
        progress_bar["maximum"] = len(reader)  # Set max value based on total pages

        # Function to process a single page
        def process_page(page_index):
            try:
                text = extract_text_from_pdf(pdf_path, page_index + 1)
                number_series = find_series_of_numbers(text, pattern=number_pattern)

                # Use OCR if no series is found from text extraction
                if not number_series:
                    images = convert_from_path(pdf_path, first_page=page_index + 1, last_page=page_index + 1)
                    for image in images:
                        ocr_text = extract_text_with_ocr(image)
                        number_series = find_series_of_numbers(ocr_text, pattern=number_pattern)

                        if number_series:  # Save cropped image
                            cropped_image = crop_image(image, crop_ratio=crop_ratio)
                            output_path = os.path.join(output_folder, f"{number_series}.png")
                            cropped_image.save(output_path, "PNG")
                            logging.info(f"Cropped image saved as {output_path}")
                            return f"Page {page_index + 1}: Success"
                else:
                    logging.info(f"Series of numbers '{number_series}' found directly on page {page_index + 1}")
                    return f"Page {page_index + 1}: Success"
            except Exception as e:
                logging.error(f"Error processing page {page_index + 1}: {e}")
                return f"Page {page_index + 1}: Failed"

        # Multithreading setup
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(process_page, i) for i in range(len(reader))]
            for i, future in enumerate(as_completed(futures)):
                progress_bar["value"] = i + 1  # Update progress bar
                progress_label.config(text=f"Processing page {i + 1} of {len(reader)}...")
                progress_window.update_idletasks()  # Refresh GUI dynamically
                print(future.result())  # Output the result of each processed page

        progress_label.config(text="Processing complete!")  # Final message
        progress_window.update_idletasks()
        progress_window.destroy()
        logging.info("All pages processed successfully.")
    except Exception as e:
        logging.error(f"Error in multithreaded processing: {e}")
        print(f"Error in multithreaded processing: {e}")

# Main Program
try:
    # Use tkinter to select the PDF file
    Tk().withdraw()  # Hide the root tkinter window
    pdf_file_path = askopenfilename(title="Select a PDF File", filetypes=[("PDF Files", "*.pdf")])
    if not pdf_file_path:
        raise FileNotFoundError("No file selected. Exiting...")
    pdf_file_path = normalize_path(pdf_file_path)
    if not os.path.exists(pdf_file_path):
        raise FileNotFoundError(f"The PDF file does not exist: {pdf_file_path}")

    # Use tkinter to select the output folder
    output_folder_name = askdirectory(title="Select an Output Folder")
    if not output_folder_name:
        raise ValueError("No output folder selected. Exiting...")
    output_folder_name = normalize_path(output_folder_name)

    # Validate or create the output folder
    if not os.path.exists(output_folder_name):
        if not create_output_folder(output_folder_name):
            raise ValueError("Failed to create output folder.")

    # Get the number pattern and cropping ratio from the user
    number_pattern = r'\d{10}'  # Always search for 10-digit numbers
    crop_ratio = 0.95  # Fixed cropping ratio

    # Process the PDF using multithreading
    process_pdf_multithreaded(pdf_file_path, output_folder_name, number_pattern, crop_ratio)

except Exception as e:
    logging.error(f"An error occurred: {e}")
    print(f"An error occurred: {e}")