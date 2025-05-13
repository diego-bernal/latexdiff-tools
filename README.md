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
git clone https://github.com/YOUR-USERNAME/latexdiff-tools.git
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

The concatenated file will be created in the current directory with the name of the parent directory of the main file.

## Typical Workflow

1. For multi-file LaTeX projects, first use `tex_concatenator.py` to create single-file versions of both the old and new versions of your document:

```bash
python tex_concatenator.py path/to/old_project/main.tex --flatten-bib
python tex_concatenator.py path/to/new_project/main.tex --flatten-bib
```

2. Then use `latexdiffcite.py` to generate a clean diff with properly handled bibliography:

```bash
python latexdiffcite.py old_project.tex new_project.tex > diff_result.tex
```

3. Compile the result to see the changes:

```bash
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
