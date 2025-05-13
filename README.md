# LaTeXDiff Tools

A collection of tools to help with LaTeX document comparison and preparation for `latexdiff`.

## Tools Included

### 1. latexdiffcite.py

A wrapper around the `latexdiff` utility that provides improved handling of bibliographies in LaTeX documents. It fixes common issues with bibliography enumeration and LaTeX command spacing that can occur when using `latexdiff` directly.

### 2. tex_concatenator.py

A tool to concatenate a multi-file LaTeX project into a single file for easier comparison with tools like `latexdiff`. It handles input files, bibliography processing, and figure management.

## Requirements

- Python 3.6+
- LaTeX installation (including `latexdiff` utility)
- Standard LaTeX utilities: `pdflatex`, `bibtex`

## Installation

Clone this repository:

```bash
git clone https://github.com/diego-bernal/latexdiff-tools.git
cd latexdiff-tools
```

No additional installation is required as the tools are Python scripts.

## Usage

### latexdiffcite.py

This script improves bibliography handling in LaTeX diff files:

```bash
python latexdiffcite.py old_file.tex new_file.tex > diff_result.tex
```

or make it executable:

```bash
chmod +x latexdiffcite.py
./latexdiffcite.py old_file.tex new_file.tex > diff_result.tex
```

#### Parameters:

- `old_file.tex`: Path to the original LaTeX file
- `new_file.tex`: Path to the modified LaTeX file

The result will be written to stdout, which can be redirected to a file.

### tex_concatenator.py

This script concatenates multi-file LaTeX projects into a single file:

```bash
python tex_concatenator.py path/to/main.tex [options]
```

or make it executable:

```bash
chmod +x tex_concatenator.py
./tex_concatenator.py path/to/main.tex [options]
```

#### Parameters:

- `path/to/main.tex`: Path to the main LaTeX file of your project

#### Options:

- `--flatten-bib`: Flatten bibliography into thebibliography environment
- `--fix-ref-numbers`: Fix bibliography reference numbers based on order of appearance

#### Output:

- The script creates a new file named after the parent directory (e.g., `your_project.tex`) in your current working directory.
- All figure files referenced by `\includegraphics` are copied to a local `./figures/` folder.
- **Controlling Output Location**: To place output in a specific directory (e.g., the tests directory), change your working directory before running the command:

```bash
# Change to the tests directory to make output files go there
cd /path/to/latexdiff-tools/tests

# Run the command with relative paths
python ../tex_concatenator.py ../path/to/project/main.tex --flatten-bib
```

#### Example:

```bash
# Concatenate the first version with flattened bibliography and fixed reference numbers
python tex_concatenator.py path/to/old_project/main.tex --flatten-bib --fix-ref-numbers

# Concatenate the second version with the same options
python tex_concatenator.py path/to/new_project/main.tex --flatten-bib --fix-ref-numbers
```

## Typical Workflow

### For Multi-file LaTeX Projects (Most Common Case)

Most LaTeX projects consist of multiple files (main file with included sections, separate bibliography files, etc.). To compare such projects:

1. **Important First Step**: Use `tex_concatenator.py` to create single-file versions of both the old and new versions of your document:

```bash
# To place output files in a specific directory (e.g., tests/), first change to that directory
cd /path/to/latexdiff-tools/tests

# Concatenate the first version with flattened bibliography
python ../tex_concatenator.py ../path/to/old_project/main.tex --flatten-bib --fix-ref-numbers

# Concatenate the second version with flattened bibliography
python ../tex_concatenator.py ../path/to/new_project/main.tex --flatten-bib --fix-ref-numbers
```

2. Then use `latexdiffcite.py` to generate a clean diff with properly handled bibliography:

```bash
python latexdiffcite.py old_project.tex new_project.tex > diff_result.tex
```

3. Compile the result to see the changes:

```bash
pdflatex diff_result.tex
```

4. Clean up auxiliary files while keeping the PDF:

```bash
# For a clean compilation
pdflatex diff_result.tex

# Remove auxiliary files
rm -f *.aux *.log *.out *.toc *.lof *.lot *.bbl *.blg *.fdb_latexmk *.fls *.synctex.gz *.soc *.loc
```

Alternatively, on macOS/Linux, you can use `latexmk` for a more streamlined process:

```bash
# Compile with latexmk
latexmk -pdf diff_result.tex

# Clean up auxiliary files but keep the PDF
latexmk -c
```

### For Single-file LaTeX Documents

If your LaTeX documents are already single files (not using `\input` or `\include`), you can skip the concatenation step and directly use:

```bash
python latexdiffcite.py old_file.tex new_file.tex > diff_result.tex
pdflatex diff_result.tex
```

## Testing

To test the tools with your own files:

1. Place your test files in the `tests/` directory
2. Run the tools on these files to verify they work correctly
3. Check the output for any issues

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
