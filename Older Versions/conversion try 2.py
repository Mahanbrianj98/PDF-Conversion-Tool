import os
import re
import fitz  # PyMuPDF for PDF page dimensions
import pytesseract
from pdfminer.high_level import extract_text
from pdf2image import convert_from_path
from PyPDF2 import PdfReader
from PIL import Image

# Set the path for Tesseract OCR (adjust if needed)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Function to create output directory if it doesn't exist
def create_output_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

# Function to search for a 10-digit number pattern
def find_series_of_numbers(text, pattern=r'\d{10}'):
    match = re.search(pattern, text)
    return match.group() if match else None

# Function to extract text from a PDF page using pdfminer
def extract_text_from_pdf(pdf_path, page_number):
    return extract_text(pdf_path, page_numbers=[page_number - 1])  # PDF pages are 0-indexed

# Function to extract text from an image using OCR
def extract_text_with_ocr(image):
    return pytesseract.image_to_string(image, lang='eng')

# Main function
def process_pdf(pdf_path, output_folder):
    reader = PdfReader(pdf_path)  # Read the PDF
    doc = fitz.open(pdf_path)  # Open with PyMuPDF to get dimensions
    create_output_folder(output_folder)

    for i in range(len(reader.pages)):
        # Extract text using pdfminer
        text = extract_text_from_pdf(pdf_path, i + 1)
        number_series = find_series_of_numbers(text)

        if not number_series:
            # Convert PDF page to image for OCR
            images = convert_from_path(pdf_path, first_page=i + 1, last_page=i + 1)

            for image in images:
                ocr_text = extract_text_with_ocr(image)  # Extract text using OCR
                number_series = find_series_of_numbers(ocr_text)  # Search for 10-digit number

                if number_series:
                    img_width, img_height = image.size
                    crop_box = (0, 0, img_width * 0.95, img_height * 0.95)  # Crop to 95% of the image
                    cropped_image = image.crop(crop_box)
                    cropped_image.save(os.path.join(output_folder, f"{number_series}.png"), "PNG")
                else:
                    print(f"No series of numbers found on page {i + 1}")

# Usage
pdf_file_path = r"C:\\Users\\Brian Mahan\\OneDrive - waynecompany.com\\Documents\\Estes\\JAX\\April 2025\\4.9.25\\Estes JAX 4.9.25.pdf"  # Replace with your PDF path
output_folder_name = r"C:\\Users\Brian Mahan\\OneDrive - waynecompany.com\\Documents\\Estes\\JAX\\April 2025\\4.9.25\\PODs"  # Folder to save the PNG files
process_pdf(pdf_file_path, output_folder_name)
