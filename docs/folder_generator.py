#!/usr/bin/env python3
"""
Folder Documentation Generator
Creates index.md, doc.md, and sub.md for each folder.
"""

import os
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class FolderDocGenerator:
    def __init__(self, docs_path: str):
        self.docs_path = Path(docs_path)
        self.folders_processed = 0

    def get_folder_description(self, folder_name: str, parent_path: str) -> str:
        """Get a description for a folder based on its name and location."""
        descriptions = {
            'agents': 'Contains agent implementations for the Strix security testing framework',
            'StrixAgent': 'Main Strix agent implementation with system prompts',
            'interface': 'User interface components including CLI and TUI',
            'tool_components': 'Rendering components for various tool outputs',
            'assets': 'Static assets including stylesheets',
            'llm': 'Language model integration and configuration',
            'prompts': 'Prompt templates for various security testing scenarios',
            'coordination': 'Coordination and orchestration prompts',
            'frameworks': 'Framework-specific security testing prompts',
            'protocols': 'Protocol-specific testing prompts',
            'technologies': 'Technology-specific testing prompts',
            'vulnerabilities': 'Vulnerability-specific testing prompts',
            'runtime': 'Runtime environment and tool server implementation',
            'telemetry': 'Telemetry and tracing functionality',
            'tools': 'Tool implementations for various security testing tasks',
            'agents_graph': 'Agent graph visualization and management',
            'browser': 'Browser automation and interaction tools',
            'file_edit': 'File editing and manipulation tools',
            'finish': 'Task completion and finalization tools',
            'notes': 'Note-taking and documentation tools',
            'proxy': 'Proxy management and interception tools',
            'python': 'Python code execution tools',
            'reporting': 'Reporting and documentation generation tools',
            'terminal': 'Terminal emulation and command execution',
            'thinking': 'Reasoning and planning tools',
            'web_search': 'Web search and reconnaissance tools',
            'containers': 'Docker containerization files',
        }

        return descriptions.get(folder_name, f'Contains files related to {folder_name}')

    def generate_folder_index(self, folder_path: Path) -> str:
        """Generate index.md for a folder."""
        rel_path = folder_path.relative_to(self.docs_path)

        # Get all files and subdirectories
        files = []
        subdirs = []

        try:
            for item in sorted(folder_path.iterdir()):
                if item.name.startswith('.'):
                    continue

                if item.is_file():
                    files.append(item.name)
                elif item.is_dir():
                    subdirs.append(item.name)
        except:
            pass

        # Build index content
        index_md = f"""# Index: {rel_path if str(rel_path) != '.' else 'Root'}

## Overview

This folder contains documentation for: `{rel_path if str(rel_path) != '.' else 'root directory'}`

"""

        if subdirs:
            index_md += "## Subdirectories\n\n"
            for subdir in subdirs:
                index_md += f"- [{subdir}/](./{subdir}/index.md)\n"
            index_md += "\n"

        if files:
            # Separate doc files from source files
            doc_files = [f for f in files if f.endswith('_docs.md')]
            kw_files = [f for f in files if f.endswith('_kw.md')]
            other_files = [f for f in files if not f.endswith(('_docs.md', '_kw.md'))]

            if doc_files:
                index_md += "## Documentation Files\n\n"
                for doc_file in sorted(doc_files):
                    # Extract original filename
                    orig_name = doc_file.replace('_docs.md', '')
                    index_md += f"- [{orig_name}](./{doc_file})"

                    # Check if kw file exists
                    kw_file = doc_file.replace('_docs.md', '_kw.md')
                    if kw_file in kw_files:
                        index_md += f" ([keywords](./{kw_file}))"
                    index_md += "\n"
                index_md += "\n"

            if other_files:
                index_md += "## Other Files\n\n"
                for other_file in sorted(other_files):
                    index_md += f"- [{other_file}](./{other_file})\n"
                index_md += "\n"

        # Add navigation
        index_md += "## Navigation\n\n"
        if str(rel_path) != '.':
            parent = rel_path.parent
            if str(parent) == '.':
                index_md += "- [⬆ Parent: Root](../index.md)\n"
            else:
                index_md += f"- [⬆ Parent: {parent.name}](../index.md)\n"

        index_md += "- [🏠 Documentation Home](/docs/index.md)\n"

        index_md += f"""
---
*Generated: {datetime.now().isoformat()}*
"""

        return index_md

    def generate_folder_doc(self, folder_path: Path) -> str:
        """Generate doc.md for a folder."""
        rel_path = folder_path.relative_to(self.docs_path)
        folder_name = folder_path.name if str(rel_path) != '.' else 'root'

        # Get description
        description = self.get_folder_description(folder_name, str(rel_path))

        doc_md = f"""# Documentation: {rel_path if str(rel_path) != '.' else 'Root'}

## Purpose

{description}

## Structure

"""

        # Count files and subdirectories
        try:
            items = list(folder_path.iterdir())
            doc_files = [f for f in items if f.is_file() and f.name.endswith('_docs.md')]
            subdirs = [d for d in items if d.is_dir() and not d.name.startswith('.')]

            doc_md += f"- **Documentation files**: {len(doc_files)}\n"
            doc_md += f"- **Subdirectories**: {len(subdirs)}\n\n"

            if subdirs:
                doc_md += "### Subdirectories\n\n"
                for subdir in sorted(subdirs):
                    subdir_desc = self.get_folder_description(subdir.name, str(rel_path / subdir.name))
                    doc_md += f"- **{subdir.name}**: {subdir_desc}\n"
                doc_md += "\n"

        except Exception as e:
            doc_md += f"*Error reading folder contents: {e}*\n\n"

        doc_md += """## Concepts

This section provides narrative context about the code and functionality in this folder.

### Architecture

"""

        # Add context based on folder type
        if 'agents' in str(rel_path):
            doc_md += """
Agents are autonomous components that execute security testing tasks. They use language models
to reason about targets and execute appropriate testing strategies.
"""
        elif 'tools' in str(rel_path):
            doc_md += """
Tools provide discrete capabilities for security testing, including browser automation,
file manipulation, code execution, and information gathering.
"""
        elif 'prompts' in str(rel_path):
            doc_md += """
Prompts are Jinja2 templates that provide context and instructions to language models
for specific security testing scenarios.
"""
        elif 'interface' in str(rel_path):
            doc_md += """
Interface components handle user interaction through command-line and text-based interfaces,
rendering tool outputs and managing user input.
"""
        elif 'llm' in str(rel_path):
            doc_md += """
LLM components manage language model interactions, including request queuing,
memory management, and response processing.
"""
        elif 'runtime' in str(rel_path):
            doc_md += """
Runtime components provide execution environments for tools, including Docker
containerization and tool server management.
"""
        else:
            doc_md += """
This folder contains supporting code and configuration for the Strix framework.
"""

        doc_md += f"""

## Key Files

See the [index](./index.md) for a complete list of files and subdirectories.

---
*Generated: {datetime.now().isoformat()}*
"""

        return doc_md

    def generate_folder_sub(self, folder_path: Path) -> str:
        """Generate sub.md (merged keywords) for a folder."""
        rel_path = folder_path.relative_to(self.docs_path)

        # Collect all keywords from descendant _kw.md files
        all_keywords = defaultdict(list)

        try:
            for kw_file in folder_path.rglob('*_kw.md'):
                try:
                    with open(kw_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Extract keywords (headers level 3)
                    keywords = re.findall(r'^### (\w+)', content, re.MULTILINE)

                    rel_kw_path = kw_file.relative_to(self.docs_path)
                    for kw in keywords:
                        all_keywords[kw].append(str(rel_kw_path))

                except:
                    pass
        except:
            pass

        # Build sub.md content
        sub_md = f"""# Keyword Index: {rel_path if str(rel_path) != '.' else 'Root'}

## Merged Keywords from Descendants

This file aggregates all keywords found in descendant files.

"""

        if all_keywords:
            # Sort keywords alphabetically
            sorted_keywords = sorted(all_keywords.keys())

            # Group by first letter
            current_letter = ''
            for kw in sorted_keywords:
                first_letter = kw[0].upper()
                if first_letter != current_letter:
                    current_letter = first_letter
                    sub_md += f"\n### {current_letter}\n\n"

                sub_md += f"**{kw}**\n"
                for source_file in all_keywords[kw][:5]:  # Limit to first 5 sources
                    sub_md += f"  - [{source_file}](/{source_file})\n"
                if len(all_keywords[kw]) > 5:
                    sub_md += f"  - *... and {len(all_keywords[kw]) - 5} more*\n"
                sub_md += "\n"

            sub_md += f"\n---\n*Total unique keywords: {len(all_keywords)}*\n"
        else:
            sub_md += "*No keywords found in this folder or its descendants.*\n\n"

        sub_md += f"*Generated: {datetime.now().isoformat()}*\n"

        return sub_md

    def process_folder(self, folder_path: Path):
        """Process a single folder."""
        try:
            # Generate index.md
            index_content = self.generate_folder_index(folder_path)
            index_file = folder_path / 'index.md'
            with open(index_file, 'w', encoding='utf-8') as f:
                f.write(index_content)

            # Generate doc.md
            doc_content = self.generate_folder_doc(folder_path)
            doc_file = folder_path / 'doc.md'
            with open(doc_file, 'w', encoding='utf-8') as f:
                f.write(doc_content)

            # Generate sub.md
            sub_content = self.generate_folder_sub(folder_path)
            sub_file = folder_path / 'sub.md'
            with open(sub_file, 'w', encoding='utf-8') as f:
                f.write(sub_content)

            self.folders_processed += 1
            print(f"  Processed: {folder_path.relative_to(self.docs_path)}")

        except Exception as e:
            print(f"  Error processing {folder_path}: {e}")

    def process_all_folders(self):
        """Process all folders in docs."""
        print("Processing folders...")

        # Get all directories
        folders = []
        for root, dirs, files in os.walk(self.docs_path):
            root_path = Path(root)
            if not root_path.name.startswith('.'):
                folders.append(root_path)

        # Sort folders by depth (deepest first for sub.md aggregation)
        folders.sort(key=lambda p: len(p.parts), reverse=True)

        for folder in folders:
            self.process_folder(folder)

        print(f"\nProcessed {self.folders_processed} folders")

def main():
    """Main entry point."""
    docs_path = "/home/user/strix/docs"

    generator = FolderDocGenerator(docs_path)
    generator.process_all_folders()

    print("\n=== SUMMARY ===")
    print(f"Folders processed: {generator.folders_processed}")

if __name__ == "__main__":
    main()
