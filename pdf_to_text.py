
#!/usr/bin/env python3

import argparse
import os
import sys
import logging
import multiprocessing
import gzip
import json
import fnmatch
import subprocess
from tqdm import tqdm
import pdfplumber
import hashlib

__version__ = "1.5.0"

def setup_logging(log_file):
    logging.basicConfig(filename=log_file, level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

def extract_text_from_pdf(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ''
            for page in pdf.pages:
                text += page.extract_text() + '\n'
        return text
    except Exception as e:
        logging.error(f"Error extracting text from {pdf_path}: {str(e)}")
        return None

def save_text_to_file(text, output_path, compress=False):
    try:
        if compress:
            with gzip.open(output_path + '.gz', 'wt', encoding='utf-8') as f:
                f.write(text)
        else:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
    except Exception as e:
        logging.error(f"Error saving text to {output_path}: {str(e)}")

def extract_metadata(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            return pdf.metadata
    except Exception as e:
        logging.error(f"Error extracting metadata from {pdf_path}: {str(e)}")
        return None

def should_ignore(file_path, ignore_patterns):
    return any(fnmatch.fnmatch(file_path, pattern) for pattern in ignore_patterns)

def calculate_hash(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def process_pdf(args):
    pdf_path, output_dir, preserve_structure, compress, extract_meta, ignore_patterns, shell_command, hash_check, input_dir = args
    
    if should_ignore(pdf_path, ignore_patterns):
        logging.info(f"Ignoring {pdf_path} based on ignore patterns")
        return

    if preserve_structure:
        rel_path = os.path.relpath(pdf_path, input_dir)
        output_path = os.path.join(output_dir, os.path.splitext(rel_path)[0] + '.txt')
    else:
        output_path = os.path.join(output_dir, os.path.splitext(os.path.basename(pdf_path))[0] + '.txt')

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if hash_check:
        hash_file = output_path + '.md5'
        if os.path.exists(hash_file):
            with open(hash_file, 'r') as f:
                stored_hash = f.read().strip()
            current_hash = calculate_hash(pdf_path)
            if stored_hash == current_hash:
                logging.info(f"Skipping {pdf_path} (unchanged)")
                return

    text = extract_text_from_pdf(pdf_path)
    if text:
        save_text_to_file(text, output_path, compress)
        logging.info(f"Processed {pdf_path} -> {output_path}")

        if hash_check:
            current_hash = calculate_hash(pdf_path)
            with open(hash_file, 'w') as f:
                f.write(current_hash)

        if extract_meta:
            metadata = extract_metadata(pdf_path)
            if metadata:
                meta_path = output_path + '.meta.json'
                with open(meta_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
                logging.info(f"Saved metadata to {meta_path}")

        if shell_command:
            try:
                subprocess.run(shell_command.replace('{}', output_path), shell=True, check=True)
                logging.info(f"Executed shell command on {output_path}")
            except subprocess.CalledProcessError as e:
                logging.error(f"Error executing shell command on {output_path}: {str(e)}")

def process_pdfs(input_dir, output_dir, preserve_structure, compress, extract_meta, ignore_patterns, shell_command, dry_run, hash_check):
    pdf_files = []
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))

    if dry_run:
        print(f"Would process {len(pdf_files)} PDF files")
        return

    with multiprocessing.Pool() as pool:
        args = [(pdf, output_dir, preserve_structure, compress, extract_meta, ignore_patterns, shell_command, hash_check, input_dir) for pdf in pdf_files]
        list(tqdm(pool.imap_unordered(process_pdf, args), total=len(pdf_files), desc="Processing PDFs"))

def main():
    parser = argparse.ArgumentParser(description=f"PDF to Text Converter v{__version__}")
    parser.add_argument("input_dir", help="Input directory containing PDF files")
    parser.add_argument("output_dir", help="Output directory for text files")
    parser.add_argument("--preserve-structure", action="store_true", help="Preserve directory structure in output")
    parser.add_argument("--compress", action="store_true", help="Compress output text files with gzip")
    parser.add_argument("--extract-meta", action="store_true", help="Extract and save PDF metadata")
    parser.add_argument("--ignore", nargs="*", default=[], help="Patterns to ignore (e.g., '*.tmp')")
    parser.add_argument("--shell-command", help="Shell command to run on each output file (use {} as placeholder)")
    parser.add_argument("--dry-run", action="store_true", help="Simulate execution without making changes")
    parser.add_argument("--log-file", default="pdf_to_text.log", help="Log file path")
    parser.add_argument("--hash-check", action="store_true", help="Use MD5 hash to check for changes in PDF files")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    args = parser.parse_args()

    setup_logging(args.log_file)

    try:
        process_pdfs(args.input_dir, args.output_dir, args.preserve_structure, args.compress,
                     args.extract_meta, args.ignore, args.shell_command, args.dry_run, args.hash_check)
        print("All PDF files have been processed.")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        print(f"An error occurred. Check {args.log_file} for details.")
        sys.exit(1)

if __name__ == '__main__':
    main()
