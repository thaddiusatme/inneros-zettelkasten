#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Template Migration Library

This library contains the core logic for migrating Obsidian templates.
It includes classes for parsing, generating, and migrating templates.
"""

import os
import re
import shutil
from datetime import datetime

import yaml

class NoQuotesDumper(yaml.Dumper):
    """
    Custom YAML dumper to handle Templater syntax without adding quotes.
    """
    def represent_scalar(self, tag, value, style=None):
        if isinstance(value, str) and ('<%' in value or '{{' in value):
            return super().represent_scalar(tag, value, style='|')
        return super().represent_scalar(tag, value, style=style)

class TemplateMigrator:
    """Handles the end-to-end template migration process."""

    def __init__(self, template_dir, backup_dir, dry_run=False):
        self.template_dir = template_dir
        self.backup_dir = backup_dir
        self.dry_run = dry_run
        self.processed_count = 0
        self.migrated_count = 0
        self.skipped_count = 0
        self.errors = []

        if not self.dry_run and not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

    def run(self):
        """Iterates through templates and migrates them."""
        self._rename_files_with_typos()

        for filename in sorted(os.listdir(self.template_dir)):
            if not filename.endswith('.md'):
                continue
            
            filepath = os.path.join(self.template_dir, filename)
            self.processed_count += 1
            print(f"\nProcessing: {filename}")

            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                parser = TemplateParser(content)

                if parser.is_compliant:
                    print("- Status: Already compliant. Skipping.")
                    self.skipped_count += 1
                    continue

                generator = TemplateGenerator(parser)
                new_content = generator.generate_content()

                if self.dry_run:
                    print("- Status: Migration needed (Dry Run).")
                    print("--- BEGIN MIGRATED CONTENT ---")
                    print(new_content.strip())
                    print("--- END MIGRATED CONTENT ---")
                    self.migrated_count += 1
                else:
                    self._backup_file(filepath, filename)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"- Status: Migrated successfully.")
                    self.migrated_count += 1

            except Exception as e:
                error_message = f"Failed to process {filename}: {e}"
                print(f"- Status: Error. {error_message}")
                self.errors.append(error_message)

    def _rename_files_with_typos(self):
        """Renames templates with known typos for consistency."""
        typo_map = {
            "permament.md": "permanent.md",
            "permanent Note Mornign Check In Template.md": "permanent-note-morning-check-in.md"
        }
        for old_name, new_name in typo_map.items():
            old_path = os.path.join(self.template_dir, old_name)
            new_path = os.path.join(self.template_dir, new_name)
            if os.path.exists(old_path):
                print(f"Renaming '{old_name}' to '{new_name}'...")
                if not self.dry_run:
                    os.rename(old_path, new_path)

    def _backup_file(self, filepath, filename):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_filename = f"{os.path.splitext(filename)[0]}_{timestamp}.bak"
        backup_filepath = os.path.join(self.backup_dir, backup_filename)
        shutil.copy2(filepath, backup_filepath)
        print(f"- Action: Backed up original to {backup_filepath}")

class TemplateParser:
    """Parses a template file to separate its components."""

    def __init__(self, content):
        self.original_content = content
        self.templater_script = ""
        self.frontmatter = {}
        self.legacy_metadata = {}
        self.body = ""
        self._parse()

    def _parse(self):
        content = self.original_content

        # 1. Extract and remove Templater script block
        script_match = re.search(r"(<%\*.*?%>\n)", content, re.DOTALL)
        if script_match:
            self.templater_script = script_match.group(1).strip()
            content = content.replace(script_match.group(1), "", 1)

        # 2. Extract and remove all YAML frontmatter blocks
        yaml_blocks = re.findall(r"^---\n(.*?)\n---\n?", content, re.DOTALL | re.MULTILINE)
        for block in yaml_blocks:
            try:
                parsed_yaml = yaml.safe_load(block) or {}
                self.frontmatter.update(parsed_yaml)
                content = content.replace(f"---\n{block}---", "", 1)
            except yaml.YAMLError:
                pass # Ignore malformed YAML, treat as body

        # 3. Extract legacy key-value metadata
        # Format: **Key**: Value or Key: Value
        legacy_patterns = [
            re.compile(r"^\*\*(.*?)\*\*:\s*(.*)$", re.MULTILINE),
            re.compile(r"^([A-Za-z]+):\s+(.*)$", re.MULTILINE)
        ]
        for pattern in legacy_patterns:
            for match in pattern.finditer(content):
                key = match.group(1).lower().strip()
                value = match.group(2).strip()
                self.legacy_metadata[key] = value
            content = pattern.sub('', content)

        # 4. The rest is body
        self.body = content.strip()

    @property
    def is_compliant(self):
        # Compliant if it has a single, valid YAML block and no legacy metadata
        if not self.legacy_metadata and len(re.findall(r"^---", self.original_content)) == 2:
            try:
                frontmatter = yaml.safe_load(self.original_content.split("---")[1])
                required_keys = ['type', 'created', 'status']
                return all(key in frontmatter for key in required_keys)
            except (yaml.YAMLError, IndexError):
                return False
        return False

class TemplateGenerator:
    """Generates standardized content for a template."""

    def __init__(self, parser):
        self.parser = parser

    def generate_content(self):
        """Reassembles the full template content in a standardized format."""
        yaml_frontmatter = self._generate_yaml()
        
        parts = []
        if self.parser.templater_script:
            parts.append(self.parser.templater_script)
        
        parts.append(yaml_frontmatter)
        
        if self.parser.body:
            parts.append(self.parser.body)
            
        return "\n\n".join(parts) + "\n"

    def _generate_yaml(self):
        data = self.parser.frontmatter.copy()

        legacy_data = self._map_legacy_to_standard()
        for key, value in legacy_data.items():
            if key not in data:
                data[key] = value

        if 'type' not in data:
            data['type'] = 'permanent'
        if 'created' not in data:
            data['created'] = '<% tp.date.now("YYYY-MM-DD HH:mm") %>'
        if 'status' not in data:
            data['status'] = 'draft'
        if 'tags' not in data:
            data['tags'] = []
        if 'visibility' not in data:
            data['visibility'] = 'private'

        if isinstance(data.get('tags'), str):
            data['tags'] = [tag.strip().replace('#', '') for tag in data['tags'].split()]

        ordered_data = {
            'type': data.get('type'),
            'created': data.get('created'),
            'status': data.get('status'),
        }
        # Add other fields, preserving their order as much as possible
        for key, value in data.items():
            if key not in ordered_data:
                ordered_data[key] = value
        
        ordered_data['tags'] = data.get('tags', [])
        ordered_data['visibility'] = data.get('visibility', 'private')

        yaml_string = yaml.dump(ordered_data, Dumper=NoQuotesDumper, default_flow_style=False, sort_keys=False, allow_unicode=True)
        return f"---\n{yaml_string.strip()}\n---"
    
    def _map_legacy_to_standard(self):
        mapped = {}
        if 'type' in self.parser.legacy_metadata:
            note_type_raw = self.parser.legacy_metadata['type']
            if 'Fleeting' in note_type_raw:
                mapped['type'] = 'fleeting'
            elif 'Permanent' in note_type_raw:
                mapped['type'] = 'permanent'
        
        if 'created' in self.parser.legacy_metadata:
            mapped['created'] = self.parser.legacy_metadata['created']
            
        if 'tags' in self.parser.legacy_metadata:
            mapped['tags'] = self.parser.legacy_metadata['tags']

        return mapped
