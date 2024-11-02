# PDF to Text Converter

Version 1.5.0

This Python script converts PDF files to text, with various options for processing and output.

## Features

- Convert multiple PDF files to text
- Preserve directory structure
- Compress output text files
- Extract and save PDF metadata
- Ignore specific files or patterns
- Execute custom shell commands on output files
- MD5 hash checking to avoid reprocessing unchanged files
- Multiprocessing for improved performance
- Dry run option for simulation
- Detailed logging

## Requirements

- Python 3.6+
- pdfplumber
- tqdm

## Installation

1. Clone this repository or download the `pdf_to_text.py` file.
2. Install the required packages:

```
pip install pdfplumber tqdm
```

## Usage

```
python pdf_to_text.py <input_dir> <output_dir> [options]
```

### Options

- `--preserve-structure`: Preserve the directory structure in the output
- `--compress`: Compress output text files with gzip
- `--extract-meta`: Extract and save PDF metadata
- `--ignore [patterns]`: Patterns to ignore (e.g., '*.tmp')
- `--shell-command <command>`: Shell command to run on each output file (use {} as placeholder)
- `--dry-run`: Simulate execution without making changes
- `--log-file <file>`: Specify a log file (default: pdf_to_text.log)
- `--hash-check`: Use MD5 hash to check for changes in PDF files
- `--version`: Show the version number and exit

## Examples

1. Basic usage:
```
python pdf_to_text.py /path/to/pdfs /path/to/output
```

2. Preserve directory structure and compress output:
```
python pdf_to_text.py /path/to/pdfs /path/to/output --preserve-structure --compress
```

3. Extract metadata and ignore temporary files:
```
python pdf_to_text.py /path/to/pdfs /path/to/output --extract-meta --ignore "*.tmp" "temp/*"
```

4. Use hash checking and run a custom command on each output file:
```
python pdf_to_text.py /path/to/pdfs /path/to/output --hash-check --shell-command "wc -l {}"
```

## License

This project is licensed under the MIT License. See the LICENSE file for details.
