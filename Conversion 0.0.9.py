import os
import fitz  # PyMuPDF
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
import logging
from tkinter import Tk, Button, Label, IntVar
from tkinter.filedialog import askopenfilename, askdirectory
from tkinter import ttk
import threading

# Configure logging
logging.basicConfig(
    filename='pdf_processing.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def normalize_path(file_path):
    return os.path.abspath(os.path.normpath(file_path.strip()))

def create_output_folder(folder_name):
    try:
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        logging.info(f"Output folder '{folder_name}' created successfully.")
    except OSError as e:
        logging.error(f"Error creating folder {folder_name}: {e}")
        return False
    return True

def crop_image(image, crop_ratio=0.95):
    img_width, img_height = image.size
    crop_box = (0, 0, int(img_width * crop_ratio), int(img_height * crop_ratio))
    return image.crop(crop_box)

def find_series_of_numbers(text, pattern=r'\d{10}'):
    import re
    match = re.search(pattern, text)
    return match.group() if match else None

def process_page(args):
    page_number, pdf_path, output_folder, number_pattern, crop_ratio = args
    try:
        pdf_document = fitz.open(pdf_path)
        page = pdf_document[page_number]

        text = page.get_text()
        number_series = find_series_of_numbers(text, pattern=number_pattern)

        if not number_series:
            images = convert_from_path(pdf_path, first_page=page_number + 1, last_page=page_number + 1)
            for image in images:
                ocr_text = pytesseract.image_to_string(image, lang='eng')
                number_series = find_series_of_numbers(ocr_text, pattern=number_pattern)

                if number_series:
                    cropped_image = crop_image(image, crop_ratio=crop_ratio)
                    output_path = os.path.join(output_folder, f"{number_series}.png")
                    cropped_image.save(output_path, "PNG")
                    pdf_document.close()
                    return f"Page {page_number + 1}: Image saved as {output_path}"

        pdf_document.close()
        return f"Page {page_number + 1}: No series found, text extraction performed."
    except Exception as e:
        logging.error(f"Error processing page {page_number + 1}: {e}")
        return f"Error processing page {page_number + 1}: {e}"

def process_pdf_with_progress(pdf_path, output_folder, number_pattern, crop_ratio, update_progress, total_pages):
    try:
        tasks = [(page_number, pdf_path, output_folder, number_pattern, crop_ratio) for page_number in range(total_pages)]

        for i, task in enumerate(tasks):
            process_page(task)
            update_progress(i + 1)

    except Exception as e:
        logging.error(f"An error occurred during multiprocessing: {e}")

def start_convert_pdf():
    try:
        Tk().withdraw()
        pdf_file_path = askopenfilename(title="Select a PDF File", filetypes=[("PDF Files", "*.pdf")])
        if not pdf_file_path:
            raise FileNotFoundError("No file selected. Exiting...")
        pdf_file_path = normalize_path(pdf_file_path)
        if not os.path.exists(pdf_file_path):
            raise FileNotFoundError(f"The PDF file does not exist: {pdf_file_path}")

        output_folder_name = askdirectory(title="Select an Output Folder")
        if not output_folder_name:
            raise ValueError("No output folder selected. Exiting...")
        output_folder_name = normalize_path(output_folder_name)

        if not os.path.exists(output_folder_name):
            if not create_output_folder(output_folder_name):
                raise ValueError("Failed to create output folder.")

        pdf_document = fitz.open(pdf_file_path)
        total_pages = len(pdf_document)
        pdf_document.close()

        progress_var.set(0)
        progress_bar['maximum'] = total_pages

        def update_progress(value):
            progress_var.set(value)
            root.update_idletasks()

        def run_processing():
            process_pdf_with_progress(pdf_file_path, output_folder_name, r'\d{10}', 0.95, update_progress, total_pages)

        threading.Thread(target=run_processing).start()

    except Exception as e:
        logging.error(f"An error occurred: {e}")

def exit_program():
    root.destroy()

root = Tk()
root.title("PDF Processor with Progress Bar")
root.geometry("400x250")

title_label = Label(root, text="PDF Processor", font=("Helvetica", 16))
title_label.pack(pady=10)

convert_button = Button(root, text="Convert PDF", command=start_convert_pdf, width=20)
convert_button.pack(pady=10)

exit_button = Button(root, text="Exit", command=exit_program, width=20)
exit_button.pack(pady=10)

progress_var = IntVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
progress_bar.pack(pady=20, padx=20, fill='x')

root.mainloop()