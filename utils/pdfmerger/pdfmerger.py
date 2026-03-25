"""
PDF MERGER CLI (FLAG-BASED)
---------------------------
USAGE:
python3 pdfmerger.py --folder "my_pdfs" --output "final.pdf"

OPTIONS:
--folder : The directory containing your PDF files.
--output : The name of the resulting file (defaults to 'merged_result.pdf').
"""

import os
import argparse
from PyPDF2 import PdfMerger

def merge_pdfs(input_folder, output_filename):
    # Ensure the output filename ends with .pdf
    if not output_filename.lower().endswith('.pdf'):
        output_filename += '.pdf'

    merger = PdfMerger()
    
    if not os.path.exists(input_folder):
        print(f"Error: The folder '{input_folder}' was not found.")
        return

    # Gather and sort PDF files
    files = sorted([f for f in os.listdir(input_folder) if f.lower().endswith('.pdf')])
    
    if not files:
        print(f"No PDF files found in '{input_folder}'.")
        return

    print(f"--- Processing {len(files)} files ---")

    for file in files:
        file_path = os.path.join(input_folder, file)
        try:
            merger.append(file_path)
            print(f"Added: {file}")
        except Exception as e:
            print(f"Skipping {file}: {e}")

    try:
        merger.write(output_filename)
        merger.close()
        print(f"\nSuccess! Merged file saved as: {output_filename}")
    except Exception as e:
        print(f"Critical Error writing file: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge PDFs using flags.")
    
    # Adding optional flags with '--'
    parser.add_argument("--folder", required=True, help="Path to the PDF folder")
    parser.add_argument("--output", default="merged_result.pdf", help="The output filename")

    args = parser.parse_args()

    merge_pdfs(args.folder, args.output)