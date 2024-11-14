import os
import subprocess

def convert_pptx_to_pdf(input_file, output_file):
    """
    Convert a PowerPoint (.pptx) file to PDF using Microsoft PowerPoint on macOS.
    """
    print(f"[INFO] Converting '{input_file}' to PDF...")

    # Prepare AppleScript to automate the conversion in PowerPoint
    applescript = f"""
    tell application "Microsoft PowerPoint"
        with timeout of 300 seconds
            open POSIX file "{input_file}" without password
            set pdfPath to POSIX file "{output_file}"
            save active presentation in pdfPath as save as PDF
            close active presentation saving no
        end timeout
    end tell
    """
    
    try:
        # Run the AppleScript using osascript command
        subprocess.run(["osascript", "-e", applescript], check=True)
        print(f"[SUCCESS] Converted '{input_file}' to '{output_file}'.")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to convert '{input_file}'. Error: {e}")
    except Exception as e:
        print(f"[ERROR] Unexpected error during conversion: {e}")


def find_and_convert_pptx_files(input_dir, output_dir):
    """
    Recursively find all .pptx files in the input directory,
    convert them to PDFs, and maintain the folder structure in the output directory.
    """
    # Validate input and output directories
    if not os.path.isdir(input_dir):
        print(f"[ERROR] Input directory '{input_dir}' does not exist.")
        return
    if not os.path.isdir(output_dir):
        print(f"[ERROR] Output directory '{output_dir}' does not exist.")
        return

    print(f"[INFO] Starting conversion process...")
    print(f"[INFO] Searching for .pptx files in '{input_dir}'...")

    # Traverse the input directory recursively
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith('.pptx'):
                input_file_path = os.path.join(root, file)
                
                print(f"[INFO] Found PowerPoint file: '{input_file_path}'")

                # Create the corresponding output directory structure
                relative_path = os.path.relpath(root, input_dir)
                output_subdir = os.path.join(output_dir, relative_path)
                
                if not os.path.exists(output_subdir):
                    os.makedirs(output_subdir, exist_ok=True)
                    print(f"[INFO] Created output directory: '{output_subdir}'")

                # Define the output PDF file path
                output_file_path = os.path.join(output_subdir, os.path.splitext(file)[0] + '.pdf')

                # Convert the file to PDF
                convert_pptx_to_pdf(input_file_path, output_file_path)

    print("[INFO] Conversion process completed.")

if __name__ == "__main__":
    # Prompt user for input and output directories
    input_directory = '/Users/sidx/workspace/daikon-ai/data_master/powerpoint'
    output_directory = '/Users/sidx/workspace/daikon-ai/data_master/pdf'

    # Run the conversion process
    find_and_convert_pptx_files(input_directory, output_directory)
    print("[DONE] All PowerPoint files have been processed.")
