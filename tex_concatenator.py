#!/usr/bin/env python3

import os
import re
import shutil
import sys
import argparse
import tempfile
from pathlib import Path

class TexConcatenator:
    def __init__(self, tex_file, flatten_bibliography=False, fix_reference_numbers=False):
        self.tex_file = Path(tex_file)
        self.project_dir = self.tex_file.parent
        self.output_dir = Path.cwd()
        self.output_name = self.project_dir.name
        self.figures_dir = self.output_dir / "figures"
        self.flatten_bibliography = flatten_bibliography
        self.fix_reference_numbers = fix_reference_numbers
        
        # Create figures directory if it doesn't exist
        self.figures_dir.mkdir(exist_ok=True)
        
    def transform_accents(self, text):
        """Transform accented characters to LaTeX escape sequences."""
        accent_map = {
            'á': r'{\'a}',
            'é': r'{\'e}',
            'í': r'{\'i}',
            'ó': r'{\'o}',
            'ú': r'{\'u}',
            'Á': r'{\'A}',
            'É': r'{\'E}',
            'Í': r'{\'I}',
            'Ó': r'{\'O}',
            'Ú': r'{\'U}',
            'ñ': r'{\~n}',
            'Ñ': r'{\~N}',
            'ü': r'{\"u}',
            'Ü': r'{\"U}',
            'ö': r'{\"o}',
            'Ö': r'{\"O}',
            'ä': r'{\"a}',
            'Ä': r'{\"A}',
        }
        for char, replacement in accent_map.items():
            text = text.replace(char, replacement)
        return text

    def process_file(self, file_path):
        """Process a single tex file, respecting comments."""
        try:
            content = file_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            # Fallback for files with different encodings
            content = file_path.read_text(encoding='latin-1')
        
        # Transform accented characters
        content = self.transform_accents(content)
            
        # Process includes/inputs line by line to respect comments
        lines = content.split('\n')
        processed_lines = []
        
        for line in lines:
            # Skip completely empty lines
            if not line.strip():
                processed_lines.append(line)
                continue
                
            # Check if line is commented
            is_commented = line.lstrip().startswith('%')
            if is_commented:
                processed_lines.append(line)
                continue
                
            # Process uncommented input/include commands
            input_match = re.search(r'\\(input|include)\{(.*?)\}', line)
            if input_match:
                indent = line[:len(line) - len(line.lstrip())]
                include_file = input_match.group(2)
                include_path = (file_path.parent / include_file).with_suffix('.tex')
                if include_path.exists():
                    included_content = self.process_file(include_path)
                    # Preserve indentation for included content
                    included_lines = included_content.split('\n')
                    processed_lines.extend(indent + l for l in included_lines)
                else:
                    print(f"Warning: Could not find included file: {include_path}")
                    processed_lines.append(line)
            else:
                processed_lines.append(line)
        
        return '\n'.join(processed_lines)

    def copy_figures(self):
        original_figures = self.project_dir / 'figures'
        if original_figures.exists():
            for fig in original_figures.iterdir():
                if fig.is_file():
                    shutil.copy(fig, self.figures_dir)
                    
    def generate_bbl_content(self):
        """Generate .bbl file by compiling the original document and extract thebibliography environment."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            
            # Copy entire project to temp directory
            shutil.copytree(self.project_dir, temp_dir / self.project_dir.name, dirs_exist_ok=True)
            
            # Change to temp directory and compile
            original_dir = os.getcwd()
            os.chdir(temp_dir / self.project_dir.name)
            
            try:
                # Run latex and bibtex with proper encoding
                os.environ['TEXEDIT'] = 'false'
                os.system(f"pdflatex -interaction=nonstopmode {self.tex_file.name}")
                os.system(f"bibtex {self.tex_file.stem}")
                os.system(f"pdflatex -interaction=nonstopmode {self.tex_file.name}")
                os.system(f"pdflatex -interaction=nonstopmode {self.tex_file.name}")
                
                # Read generated .bbl file and extract thebibliography environment
                bbl_file = Path(f"{self.tex_file.stem}.bbl")
                if bbl_file.exists():
                    try:
                        bbl_content = bbl_file.read_text(encoding='utf-8')
                        # Extract everything between \begin{thebibliography} and \end{thebibliography}
                        bib_match = re.search(r'\\begin{thebibliography}.*?\\end{thebibliography}', 
                                            bbl_content, re.DOTALL)
                        if bib_match:
                            return bib_match.group(0)
                    except UnicodeDecodeError:
                        print("Warning: BBL file encoding issue")
                        return ""
            finally:
                os.chdir(original_dir)
        
        return ""

    def reorder_bibliography(self, bbl_content, citations=None):
        """Reorder bibliography items based on citation order."""
        # Add necessary bibliography style definitions
        bib_definitions = r"""\makeatletter
\providecommand \@ifxundefined [1]{%
 \@ifx{#1\undefined}
}%
\providecommand \@ifnum [1]{%
 \ifnum #1\expandafter \@firstoftwo
 \else \expandafter \@secondoftwo
 \fi
}%
\providecommand \@ifx [1]{%
 \ifx #1\expandafter \@firstoftwo
 \else \expandafter \@secondoftwo
 \fi
}%
\providecommand \natexlab [1]{#1}%
\providecommand \enquote  [1]{``#1''}%
\providecommand \bibnamefont  [1]{#1}%
\providecommand \bibfnamefont [1]{#1}%
\providecommand \citenamefont [1]{#1}%
\providecommand \href@noop [0]{\@secondoftwo}%
\providecommand \href [0]{\begingroup \@sanitize@url \@href}%
\providecommand \@href[1]{\@@startlink{#1}\@@href}%
\providecommand \@@href[1]{\endgroup#1\@@endlink}%
\providecommand \@sanitize@url [0]{\catcode `\\12\catcode `\$12\catcode
  `\&12\catcode `\#12\catcode `\^12\catcode `\_12\catcode `\%12\relax}%
\providecommand \@@startlink[1]{}%
\providecommand \@@endlink[0]{}%
\providecommand \url  [0]{\begingroup\@sanitize@url \@url }%
\providecommand \@url [1]{\endgroup\@href {#1}{\urlprefix }}%
\providecommand \urlprefix  [0]{URL }%
\providecommand \Eprint [0]{\href }%
\providecommand \doibase [0]{https://doi.org/}%
\providecommand \selectlanguage [0]{\@gobble}%
\providecommand \bibinfo  [0]{\@secondoftwo}%
\providecommand \bibfield  [0]{\@secondoftwo}%
\providecommand \translation [1]{[#1]}%
\providecommand \BibitemOpen [0]{}%
\providecommand \bibitemStop [0]{}%
\providecommand \bibitemNoStop [0]{.\EOS\space}%
\providecommand \EOS [0]{\spacefactor3000\relax}%
\providecommand \BibitemShut  [1]{\csname bibitem#1\endcsname}%
\let\auto@bib@innerbib\@empty
%</preamble>
"""

        # Extract all bibitem entries with a more robust pattern
        bibitem_pattern = r'\\bibitem\s*(?:\[[^]]*\])?\s*\{([^}]+)\}(.*?)(?=\\bibitem|\s*\\end\{thebibliography\})'
        bibitems = re.finditer(bibitem_pattern, bbl_content, re.DOTALL)
        
        # Create dictionary of bibitem contents keyed by citation key
        bibitem_dict = {match.group(1): match.group(2).strip() for match in bibitems}
        
        # Get the beginning of thebibliography environment
        begin_match = re.search(r'\\begin\{thebibliography\}\{[^}]*\}', bbl_content)
        if not begin_match:
            return bbl_content  # Return unchanged if no bibliography environment found
        
        # Build new bibliography with ordered and renumbered items
        new_bbl = [bib_definitions, begin_match.group(0)]
        
        if self.fix_reference_numbers and citations:
            # Use ordered citations if fixing reference numbers
            for i, cite_key in enumerate(citations, 1):
                if cite_key in bibitem_dict:
                    numbered_bibitem = f'\\bibitem [{{{i}}}] {{{cite_key}}}{bibitem_dict[cite_key]}'
                    new_bbl.append(numbered_bibitem)
        else:
            # Keep original ordering and numbering
            for cite_key in bibitem_dict:
                new_bbl.append(f'\\bibitem {{{cite_key}}}{bibitem_dict[cite_key]}')
        
        new_bbl.append('\\end{thebibliography}')
        return '\n'.join(new_bbl)

    def process_bibliography(self, content):
        """Replace bibliography command with thebibliography environment."""
        bib_match = re.search(r'\\bibliography\{.*?\}', content)
        if not bib_match:
            return content
            
        # Generate bibliography content
        bbl_content = self.generate_bbl_content()
        if not bbl_content:
            print("Warning: Could not generate bibliography")
            return content
            
        # Extract citations in order of appearance
        cite_pattern = r'\\cite\{([^}]+)\}'
        citations = []
        for match in re.finditer(cite_pattern, content):
            # Split multiple citations and add each one
            cites = match.group(1).split(',')
            citations.extend(cite.strip() for cite in cites)
        
        # Remove duplicates while preserving order
        seen = set()
        citations = [x for x in citations if not (x in seen or seen.add(x))]
        
        # Reorder bibliography items
        bbl_content = self.reorder_bibliography(bbl_content, citations)
        
        # Preserve any spacing/newlines around the bibliography command
        full_match = re.search(r'(\s*)\\bibliography\{.*?\}(\s*)', content)
        if (full_match):
            pre_space = full_match.group(1)
            post_space = full_match.group(2)
            # Replace bibliography command with reordered thebibliography environment
            return content.replace(full_match.group(0), f"{pre_space}{bbl_content}{post_space}")
            
        return content

    def get_unique_filename(self, target_path):
        """Generate unique filename if target already exists."""
        if not target_path.exists():
            return target_path
        
        counter = 1
        while True:
            new_name = target_path.with_stem(f"{target_path.stem}_{counter}")
            if not new_name.exists():
                return new_name
            counter += 1

    def copy_bibliography(self, content):
        """Copy bibliography files to output directory."""
        # Dictionary to track filename changes
        filename_map = {}
        
        # Find all bibliography files referenced in the tex file
        bib_matches = re.finditer(r'\\bibliography\{(.*?)\}', content)
        for match in bib_matches:
            bib_files = match.group(1).split(',')
            renamed_files = []
            
            for bib_file in bib_files:
                bib_file = bib_file.strip()
                # Try both with and without .bib extension
                bib_paths = [
                    self.project_dir / f"{bib_file}",
                    self.project_dir / f"{bib_file}.bib"
                ]
                
                # Use first existing file
                for bib_path in bib_paths:
                    if bib_path.exists():
                        # Generate target path and handle conflicts
                        target_name = bib_path.name if bib_path.suffix == '.bib' else f"{bib_path.name}.bib"
                        target_path = self.output_dir / target_name
                        actual_target = self.get_unique_filename(target_path)
                        
                        # Copy file and store the mapping
                        shutil.copy(bib_path, actual_target)
                        print(f"Copied bibliography file to: {actual_target}")
                        
                        # Store the mapping between original and new name
                        orig_name = bib_file.replace('.bib', '')
                        new_name = actual_target.stem
                        filename_map[orig_name] = new_name
                        renamed_files.append(new_name)
                        break
                else:
                    print(f"Warning: Could not find bibliography file: {bib_file}")
                    
            # Update bibliography reference in the tex content if files were renamed
            if renamed_files:
                old_bib = match.group(0)
                new_bib = r'\bibliography{' + ','.join(renamed_files) + '}'
                content = content.replace(old_bib, new_bib)
                
        return content

    def concatenate(self):
        """Concatenate the tex project into a single file."""
        # Process main tex file
        main_content = self.process_file(self.tex_file)
        
        # Process bibliography based on flatten option
        if self.flatten_bibliography:
            main_content = self.process_bibliography(main_content)
        else:
            main_content = self.copy_bibliography(main_content)
        
        # Copy figures
        self.copy_figures()
        
        # Write output with utf8 encoding
        output_path = self.output_dir / f"{self.output_name}.tex"
        output_path.write_text(main_content, encoding='utf-8')
        
        print(f"Created concatenated file: {output_path}")

    def test_compilation(self, tex_file):
        print(f"Testing compilation of {tex_file.name}...")
        
        # Clean up previous compilation artifacts
        for ext in ['.aux', '.log', '.out']:
            if (tex_file.parent / f"{tex_file.stem}{ext}").exists():
                (tex_file.parent / f"{tex_file.stem}{ext}").unlink()
        
        # Quote path to handle spaces
        quoted_path = f'"{tex_file}"'
        
        # Run pdflatex twice to resolve references
        os.system(f"pdflatex -interaction=nonstopmode {quoted_path}")
        os.system(f"pdflatex -interaction=nonstopmode {quoted_path}")
        
        # Clean up invalid characters in .aux file if it exists
        aux_file = tex_file.parent / f"{tex_file.stem}.aux"
        if aux_file.exists():
            with open(aux_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            with open(aux_file, 'w', encoding='utf-8') as f:
                f.write(content)
        
        print("Compilation complete. Check output PDF.")
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Concatenate a LaTeX project into a single file.')
    parser.add_argument('tex_file', help='Path to the main tex file')
    parser.add_argument('--flatten-bib', action='store_true', 
                      help='Flatten bibliography into thebibliography environment')
    parser.add_argument('--fix-ref-numbers', action='store_true',
                      help='Fix bibliography reference numbers based on order of appearance')
    
    args = parser.parse_args()
    
    concatenator = TexConcatenator(args.tex_file, 
                                 args.flatten_bib,
                                 args.fix_ref_numbers)
    concatenator.concatenate()
