# Conversion Program
# Version 0.0.5
# This program processes PDF files, extracts text, and performs OCR on images.
# It includes a GUI for user interaction and multithreading for performance.
# Changelog from 0.0.5 to 0.0.6:
# - Implementing Multiprocessing for better performance.

import os
import fitz  # PyMuPDF
from pdfminer.high_level import extract_text
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
import logging
from tkinter import Tk, Button
from tkinter.filedialog import askopenfilename, askdirectory
from multiprocessing import Pool, cpu_count

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

# Function to process a single page (worker function)
def process_page(args):
    try:
        page_number, pdf_path, output_folder = args
        pdf_document = fitz.open(pdf_path)
        page = pdf_document[page_number]

        # Extract text
        text = page.get_text()
        output_file = os.path.join(output_folder, f"page_{page_number + 1}.txt")
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(text)

        pdf_document.close()
        return f"Page {page_number + 1} processed successfully."
    except Exception as e:
        logging.error(f"Error processing page {page_number + 1}: {e}")
        return f"Error processing page {page_number + 1}: {e}"

# Multiprocessing wrapper for PDF processing
def process_pdf_with_multiprocessing(pdf_path, output_folder):
    try:
        pdf_document = fitz.open(pdf_path)
        total_pages = len(pdf_document)
        pdf_document.close()

        # Prepare tasks for multiprocessing
        tasks = [(page_number, pdf_path, output_folder) for page_number in range(total_pages)]

        # Use multiprocessing Pool
        with Pool(processes=cpu_count()) as pool:
            results = pool.map(process_page, tasks)

        # Print results
        for result in results:
            print(result)

    except Exception as e:
        logging.error(f"An error occurred during multiprocessing: {e}")
        print(f"An error occurred: {e}")

# Placeholder function for "Sort and Segregate"
def sort_and_segregate():
    print("Sort and Segregate feature is under development.")

# Function to start PDF processing
def start_convert_pdf():
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

        # Process the PDF using multiprocessing
        process_pdf_with_multiprocessing(pdf_file_path, output_folder_name)

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        print(f"An error occurred: {e}")

# Exit function
def exit_program():
    root.destroy()

# Main Tkinter window
root = Tk()
root.title("PDF Processor")

# Set window dimensions
root.geometry("300x200")

# Add buttons
convert_button = Button(root, text="Convert PDF", command=start_convert_pdf, width=20)
convert_button.pack(pady=10)

sort_button = Button(root, text="Sort and Segregate", command=sort_and_segregate, width=20)
sort_button.pack(pady=10)

exit_button = Button(root, text="Exit", command=exit_program, width=20)
exit_button.pack(pady=10)

# Start the Tkinter event loop
root.mainloop()
