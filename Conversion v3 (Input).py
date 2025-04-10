import os

def verify_path_format(file_path):
    """ Verifies and corrects the file path format """
    formatted_path = file_path.strip().replace('\\', '/')
    resolved_path = os.path.abspath(formatted_path)

    print(f"Original Path: {file_path}")
    print(f"Formatted Path: {formatted_path}")
    print(f"Resolved Absolute Path: {resolved_path}")
    
    if not os.path.exists(resolved_path):
        raise FileNotFoundError(f"File does not exist: {resolved_path}")

    return resolved_path

# Start the program
try:
    

    # Get and verify the PDF file path
    pdf_file_path = input("Please enter the full path to the PDF file: ")
    pdf_file_path = verify_path_format(pdf_file_path)

    # Get and verify the output folder path
    output_folder_name = input("Please enter the full path to the output folder: ")
    output_folder_name = verify_path_format(output_folder_name)

    # Validate or create the output folder
    if not os.path.exists(output_folder_name):
        response = input("Output folder doesn't exist. Create it? (y/n): ").strip().lower()
        if response == 'y':
            os.makedirs(output_folder_name)
            print(f"Folder created: {output_folder_name}")
        else:
            raise ValueError("Output folder creation declined. Exiting.")

    print("Path verification successful! Proceeding with PDF processing...")
    
    # You can now use `pdf_file_path` and `output_folder_name` safely
except Exception as e:
    print(f"Error: {e}")