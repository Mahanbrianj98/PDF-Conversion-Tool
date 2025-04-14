import os
import re
from PyPDF2 import PdfReader
from pdf2image import convert_from_path

# Function to create output directory if it doesn't exist
def create_output_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

# Function to search for a number pattern
def find_series_of_numbers(text, pattern=r'\d{4,}'):  # Change pattern as needed
    match = re.search(pattern, text)
    return match.group() if match else None

# Main function
def process_pdf(pdf_path, output_folder):
    # Read the PDF
    reader = PdfReader(pdf_path)
    create_output_folder(output_folder)

    for i, page in enumerate(reader.pages):
        # Extract text from the current page
        text = page.extract_text()
        # Look for the series of numbers
        number_series = find_series_of_numbers(text)

        if number_series:
            # Convert PDF page to image
            images = convert_from_path(pdf_path, first_page=i + 1, last_page=i + 1)
            for image in images:
                # Save the image using the found number series as the filename
                image.save(os.path.join(output_folder, f"{number_series}.png"), "PNG")
        else:
            print(f"No series of numbers found on page {i + 1}")

# Usage
pdf_file_path = "example.pdf"  # Replace with your PDF path
output_folder_name = "output_images"  # Folder to save the PNG files
process_pdf(pdf_file_path, output_folder_name)
