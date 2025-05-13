#!/usr/bin/env python3

import sys
import re
import subprocess
from pathlib import Path

def extract_bibliography(text):
    """Extract the bibliography section from latex text."""
    match = re.search(r'\\begin{thebibliography}.*?\\end{thebibliography}', text, re.DOTALL)
    return match.group(0) if match else ''

def fix_bibliography_enumeration(bib_text, final_bib_text):
    """Fix bibliography enumeration based on the final version."""
    final_num = re.search(r'\\begin{thebibliography}{(\d+)}', final_bib_text).group(1)
    return re.sub(r'\\begin{thebibliography}{(\d+)}', 
                 rf'\\begin{{thebibliography}}{{{final_num}}}', 
                 bib_text)

def clean_difcommands(text):
    """Clean up problematic DIFadd/DIFdel commands and fix line breaks in bibliography section."""
    # Remove problematic DIFadd/DIFdel around begin{thebibliography}
    text = re.sub(r'\\DIFdelend\s*\\DIFaddbegin\s*\\?begin{thebibliography}',
                  r'\\begin{thebibliography}',
                  text)
    
    # Fix line breaks and spacing around DIFadd/DIFdel commands
    text = re.sub(r'\\DIFaddbegin\s*\n*', r'\\DIFaddbegin ', text)
    text = re.sub(r'\s*\\DIFaddend\s*\n*', r' \\DIFaddend ', text)
    text = re.sub(r'\\DIFdelbegin\s*\n*', r'\\DIFdelbegin ', text)
    text = re.sub(r'\s*\\DIFdelend\s*\n*', r' \\DIFdelend ', text)
    
    # Fix line breaks inside DIFadd/DIFdel content
    text = re.sub(r'(\\DIFadd{[^}]*})\s*\n\s*', r'\1 ', text)
    text = re.sub(r'(\\DIFdel{[^}]*})\s*\n\s*', r'\1 ', text)
    
    # Fix consecutive spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Fix extra spaces around certain LaTeX commands 
    text = re.sub(r'\\begin\s+{', r'\\begin{', text)
    text = re.sub(r'\\end\s+{', r'\\end{', text)
    
    return text

def process_files(old_file, new_file):
    """Process the latex files and generate improved diff."""
    try:
        # Run latexdiff with explicit UTF-8 encoding
        result = subprocess.run(['latexdiff', old_file, new_file], 
                              capture_output=True, 
                              text=True,
                              encoding='utf-8')
        result.check_returncode()  # Will raise CalledProcessError if return code is non-zero
    except subprocess.CalledProcessError as e:
        print(f"Error running latexdiff: {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}", file=sys.stderr)
        sys.exit(1)
    
    diff_text = result.stdout
    
    # Read the final version to get correct bibliography enumeration
    with open(new_file, 'r', encoding='utf-8') as f:
        new_text = f.read()
    
    # Extract bibliographies
    diff_bib = extract_bibliography(diff_text)
    new_bib = extract_bibliography(new_text)
    
    if diff_bib and new_bib:
        # Fix bibliography enumeration
        fixed_bib = fix_bibliography_enumeration(diff_bib, new_bib)
        # Clean up DIFadd/DIFdel commands
        fixed_bib = clean_difcommands(fixed_bib)
        # Replace bibliography in the diff text
        diff_text = diff_text.replace(diff_bib, fixed_bib)
    
    # Final cleanup of entire document
    diff_text = clean_difcommands(diff_text)
    
    # Ensure the text ends with a newline
    if not diff_text.endswith('\n'):
        diff_text += '\n'
    
    return diff_text

def main():
    if len(sys.argv) != 3:
        print("Usage: latexdiffcite.py old_file.tex new_file.tex")
        sys.exit(1)
    
    old_file = sys.argv[1]
    new_file = sys.argv[2]
    
    # Configure stdout for UTF-8 encoding
    sys.stdout.reconfigure(encoding='utf-8')
    
    # Process files and write result only once
    result = process_files(old_file, new_file)
    sys.stdout.write(result)

if __name__ == '__main__':
    main()
