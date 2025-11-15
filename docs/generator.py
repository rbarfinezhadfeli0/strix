#!/usr/bin/env python3
"""
World's Best Repo Book Generator
Processes repository files and generates comprehensive documentation.
"""

import os
import json
import hashlib
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from datetime import datetime
from collections import defaultdict

class RepoBookGenerator:
    def __init__(self, repo_path: str, docs_path: str):
        self.repo_path = Path(repo_path)
        self.docs_path = Path(docs_path)
        self.files_scanned = 0
        self.docs_created = 0
        self.words_estimated = 0
        self.bytes_written = 0
        self.errors = []
        self.file_checksums = {}
        self.all_keywords = defaultdict(list)
        self.binary_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.ico', '.pdf', '.zip', '.gz', '.tar', '.exe', '.dll', '.so', '.dylib'}
        self.skip_patterns = {'.git', '__pycache__', '.pyc', 'docs'}

    def is_binary(self, file_path: Path) -> bool:
        """Check if file is binary."""
        if file_path.suffix.lower() in self.binary_extensions:
            return True
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                return b'\0' in chunk
        except:
            return True

    def should_skip(self, path: Path) -> bool:
        """Check if path should be skipped."""
        for pattern in self.skip_patterns:
            if pattern in str(path):
                return True
        return False

    def read_file_safe(self, file_path: Path) -> Tuple[str, str]:
        """Safely read file content."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content, None
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
                return content, "latin-1"
            except Exception as e:
                return None, str(e)
        except Exception as e:
            return None, str(e)

    def extract_keywords(self, content: str, file_ext: str) -> Set[str]:
        """Extract keywords from file content."""
        keywords = set()

        # Python specific
        if file_ext == '.py':
            # Class names
            keywords.update(re.findall(r'class\s+(\w+)', content))
            # Function/method names
            keywords.update(re.findall(r'def\s+(\w+)', content))
            # Imports
            keywords.update(re.findall(r'(?:from|import)\s+([\w.]+)', content))
            # Decorators
            keywords.update(re.findall(r'@(\w+)', content))

        # Common identifiers (camelCase, snake_case)
        keywords.update(re.findall(r'\b([A-Z][a-z]+(?:[A-Z][a-z]+)+)\b', content))
        keywords.update(re.findall(r'\b([a-z]+(?:_[a-z]+)+)\b', content))

        # Filter out common words
        common_words = {'self', 'return', 'import', 'from', 'class', 'def', 'if', 'else', 'for', 'while', 'try', 'except'}
        keywords = {k for k in keywords if k not in common_words and len(k) > 2}

        return keywords

    def count_words(self, text: str) -> int:
        """Count words in text."""
        return len(text.split())

    def generate_file_docs(self, file_path: Path) -> Tuple[str, str]:
        """Generate comprehensive documentation for a file."""
        rel_path = file_path.relative_to(self.repo_path)

        # Read file
        content, error = self.read_file_safe(file_path)

        if error:
            return self.generate_error_docs(rel_path, error)

        if content is None:
            return self.generate_error_docs(rel_path, "Could not read file")

        # Generate documentation
        file_ext = file_path.suffix
        file_size = file_path.stat().st_size

        # Extract keywords
        keywords = self.extract_keywords(content, file_ext)

        # Build docs content
        docs_md = f"""# Documentation: {rel_path}

## File Metadata
- **Path**: `{rel_path}`
- **Size**: {file_size} bytes
- **Extension**: `{file_ext}`
- **Lines**: {len(content.splitlines())}

## Original Source

```{file_ext[1:] if file_ext else 'text'}
{content}
```

## High-Level Overview

This file is located at `{rel_path}` and is part of the Strix security testing framework.

"""

        # Add Python-specific documentation
        if file_ext == '.py':
            docs_md += self.analyze_python_file(content, rel_path)
        elif file_ext == '.md':
            docs_md += self.analyze_markdown_file(content, rel_path)
        elif file_ext == '.jinja':
            docs_md += self.analyze_jinja_file(content, rel_path)
        elif file_ext == '.xml':
            docs_md += self.analyze_xml_file(content, rel_path)
        elif file_ext == '.yaml' or file_ext == '.yml':
            docs_md += self.analyze_yaml_file(content, rel_path)
        elif file_ext == '.toml':
            docs_md += self.analyze_toml_file(content, rel_path)
        elif file_ext == '.sh':
            docs_md += self.analyze_shell_file(content, rel_path)
        else:
            docs_md += f"### File Type\nGeneric text file with extension `{file_ext}`.\n\n"

        docs_md += f"""
## Related Files

*Links will be added during folder processing phase.*

## Testing & Usage

Refer to project documentation and tests for usage examples.

---
*Generated by World's Best Repo Book Generator*
*Date: {datetime.now().isoformat()}*
"""

        # Build keywords content
        kw_md = f"""# Keywords: {rel_path}

## Extracted Keywords

"""
        for kw in sorted(keywords):
            kw_md += f"### {kw}\n\nFound in: `{rel_path}`\n\n"

        kw_md += f"""
---
*Total keywords: {len(keywords)}*
*Generated: {datetime.now().isoformat()}*
"""

        return docs_md, kw_md

    def analyze_python_file(self, content: str, rel_path: Path) -> str:
        """Analyze Python file and extract detailed information."""
        output = "### Python File Analysis\n\n"

        # Extract classes
        classes = re.findall(r'class\s+(\w+)(?:\(([^)]*)\))?:', content)
        if classes:
            output += "#### Classes\n\n"
            for class_name, bases in classes:
                output += f"- **{class_name}**"
                if bases:
                    output += f" (inherits from: {bases})"
                output += "\n"
            output += "\n"

        # Extract functions
        functions = re.findall(r'def\s+(\w+)\s*\((.*?)\):', content)
        if functions:
            output += "#### Functions/Methods\n\n"
            for func_name, params in functions:
                output += f"- **{func_name}**({params})\n"
            output += "\n"

        # Extract imports
        imports = re.findall(r'^(?:from\s+[\w.]+\s+)?import\s+.+$', content, re.MULTILINE)
        if imports:
            output += "#### Imports\n\n"
            for imp in imports[:20]:  # Limit to first 20
                output += f"- `{imp.strip()}`\n"
            if len(imports) > 20:
                output += f"\n*... and {len(imports) - 20} more imports*\n"
            output += "\n"

        # Extract docstrings
        docstrings = re.findall(r'"""(.*?)"""', content, re.DOTALL)
        if docstrings:
            output += "#### Documentation Strings\n\n"
            output += f"Found {len(docstrings)} docstring(s) in this file.\n\n"

        return output

    def analyze_markdown_file(self, content: str, rel_path: Path) -> str:
        """Analyze Markdown file."""
        output = "### Markdown File Analysis\n\n"

        # Extract headers
        headers = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
        if headers:
            output += "#### Headers\n\n"
            for header in headers:
                output += f"- {header}\n"
            output += "\n"

        # Count links
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        output += f"#### Links\n\nFound {len(links)} link(s).\n\n"

        return output

    def analyze_jinja_file(self, content: str, rel_path: Path) -> str:
        """Analyze Jinja template file."""
        output = "### Jinja Template Analysis\n\n"

        # Extract variables
        variables = set(re.findall(r'\{\{\s*(\w+)', content))
        if variables:
            output += "#### Template Variables\n\n"
            for var in sorted(variables):
                output += f"- `{var}`\n"
            output += "\n"

        # Extract blocks
        blocks = re.findall(r'\{%\s*block\s+(\w+)', content)
        if blocks:
            output += "#### Template Blocks\n\n"
            for block in blocks:
                output += f"- `{block}`\n"
            output += "\n"

        return output

    def analyze_xml_file(self, content: str, rel_path: Path) -> str:
        """Analyze XML file."""
        output = "### XML File Analysis\n\n"

        # Extract root element
        root_match = re.search(r'<(\w+)', content)
        if root_match:
            output += f"Root element: `{root_match.group(1)}`\n\n"

        # Count elements
        elements = set(re.findall(r'<(\w+)', content))
        output += f"Unique elements: {len(elements)}\n\n"

        return output

    def analyze_yaml_file(self, content: str, rel_path: Path) -> str:
        """Analyze YAML file."""
        output = "### YAML Configuration Analysis\n\n"

        # Extract top-level keys
        keys = re.findall(r'^(\w+):', content, re.MULTILINE)
        if keys:
            output += "#### Top-level keys\n\n"
            for key in keys:
                output += f"- `{key}`\n"
            output += "\n"

        return output

    def analyze_toml_file(self, content: str, rel_path: Path) -> str:
        """Analyze TOML file."""
        output = "### TOML Configuration Analysis\n\n"

        # Extract sections
        sections = re.findall(r'^\[([^\]]+)\]', content, re.MULTILINE)
        if sections:
            output += "#### Sections\n\n"
            for section in sections:
                output += f"- `[{section}]`\n"
            output += "\n"

        return output

    def analyze_shell_file(self, content: str, rel_path: Path) -> str:
        """Analyze shell script."""
        output = "### Shell Script Analysis\n\n"

        # Extract functions
        functions = re.findall(r'^(\w+)\s*\(\)', content, re.MULTILINE)
        if functions:
            output += "#### Functions\n\n"
            for func in functions:
                output += f"- `{func}()`\n"
            output += "\n"

        return output

    def generate_error_docs(self, rel_path: Path, error: str) -> Tuple[str, str]:
        """Generate docs for files that couldn't be read."""
        docs_md = f"""# Documentation: {rel_path}

## Error

Could not process this file: {error}

## File Metadata
- **Path**: `{rel_path}`

---
*Generated: {datetime.now().isoformat()}*
"""
        kw_md = f"""# Keywords: {rel_path}

No keywords extracted (file error).

---
*Generated: {datetime.now().isoformat()}*
"""
        return docs_md, kw_md

    def generate_binary_docs(self, file_path: Path) -> str:
        """Generate documentation for binary files."""
        rel_path = file_path.relative_to(self.repo_path)
        file_size = file_path.stat().st_size

        docs_md = f"""# Binary File: {rel_path}

## File Metadata
- **Path**: `{rel_path}`
- **Size**: {file_size} bytes ({file_size / 1024:.2f} KB)
- **Type**: Binary file
- **Extension**: `{file_path.suffix}`

## Description

This is a binary file and cannot be displayed as text. Based on the extension:
"""

        if file_path.suffix == '.png':
            docs_md += "- **Type**: PNG Image\n- **Handling**: View with image viewer\n"
        elif file_path.suffix in {'.jpg', '.jpeg'}:
            docs_md += "- **Type**: JPEG Image\n- **Handling**: View with image viewer\n"
        else:
            docs_md += f"- **Type**: {file_path.suffix} file\n- **Handling**: Use appropriate application\n"

        docs_md += f"""
---
*Generated: {datetime.now().isoformat()}*
"""
        return docs_md

    def process_file(self, file_path: Path) -> bool:
        """Process a single file."""
        try:
            rel_path = file_path.relative_to(self.repo_path)

            # Create docs directory structure
            docs_dir = self.docs_path / rel_path.parent
            docs_dir.mkdir(parents=True, exist_ok=True)

            self.files_scanned += 1

            # Handle binary files
            if self.is_binary(file_path):
                docs_content = self.generate_binary_docs(file_path)
                docs_file = docs_dir / f"{file_path.name}_docs.md"

                with open(docs_file, 'w', encoding='utf-8') as f:
                    f.write(docs_content)

                self.docs_created += 1
                self.bytes_written += len(docs_content.encode('utf-8'))
                self.words_estimated += self.count_words(docs_content)

                # Calculate checksum
                checksum = hashlib.sha256(docs_content.encode('utf-8')).hexdigest()
                self.file_checksums[str(docs_file.relative_to(self.docs_path))] = checksum

                return True

            # Process text files
            docs_content, kw_content = self.generate_file_docs(file_path)

            # Write docs file
            docs_file = docs_dir / f"{file_path.name}_docs.md"
            with open(docs_file, 'w', encoding='utf-8') as f:
                f.write(docs_content)

            # Write keywords file
            kw_file = docs_dir / f"{file_path.name}_kw.md"
            with open(kw_file, 'w', encoding='utf-8') as f:
                f.write(kw_content)

            self.docs_created += 2
            self.bytes_written += len(docs_content.encode('utf-8')) + len(kw_content.encode('utf-8'))
            self.words_estimated += self.count_words(docs_content) + self.count_words(kw_content)

            # Calculate checksums
            checksum_docs = hashlib.sha256(docs_content.encode('utf-8')).hexdigest()
            checksum_kw = hashlib.sha256(kw_content.encode('utf-8')).hexdigest()

            self.file_checksums[str(docs_file.relative_to(self.docs_path))] = checksum_docs
            self.file_checksums[str(kw_file.relative_to(self.docs_path))] = checksum_kw

            # Store keywords for global index
            keywords = self.extract_keywords(docs_content, file_path.suffix)
            for kw in keywords:
                self.all_keywords[kw].append(str(rel_path))

            return True

        except Exception as e:
            self.errors.append(f"Error processing {file_path}: {str(e)}")
            return False

    def process_all_files(self):
        """Process all files in repository."""
        print("Processing repository files...")

        for root, dirs, files in os.walk(self.repo_path):
            root_path = Path(root)

            # Skip docs directory
            if self.should_skip(root_path):
                continue

            for file_name in files:
                file_path = root_path / file_name

                if self.should_skip(file_path):
                    continue

                print(f"  Processing: {file_path.relative_to(self.repo_path)}")
                self.process_file(file_path)

        print(f"\nProcessed {self.files_scanned} files, created {self.docs_created} documentation files")

def main():
    """Main entry point."""
    repo_path = "/home/user/strix"
    docs_path = "/home/user/strix/docs"

    generator = RepoBookGenerator(repo_path, docs_path)
    generator.process_all_files()

    # Print summary
    print("\n=== SUMMARY ===")
    print(f"Files scanned: {generator.files_scanned}")
    print(f"Docs created: {generator.docs_created}")
    print(f"Words estimated: {generator.words_estimated}")
    print(f"Bytes written: {generator.bytes_written}")
    print(f"Errors: {len(generator.errors)}")

    if generator.errors:
        print("\nErrors encountered:")
        for error in generator.errors:
            print(f"  - {error}")

if __name__ == "__main__":
    main()
