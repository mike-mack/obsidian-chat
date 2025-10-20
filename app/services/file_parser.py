import os
import hashlib
from typing import Tuple, Optional, Dict, Any
from pathlib import Path


class FileParser:
    """
    Class for parsing Obsidian markdown files.
    Handles content extraction, YAML frontmatter parsing, and content hashing.
    """
    
    def parse_file(self, file_path: str) -> Tuple[str, str]:
        """
        Parse an Obsidian markdown file and calculate its content hash.
        
        Args:
            file_path: Path to the markdown file
            
        Returns:
            Tuple[str, str]: A tuple of (content, content_hash)
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Calculate content hash
        content_hash = self._calculate_hash(content)
        
        return content, content_hash
    
    def extract_frontmatter(self, content: str) -> Tuple[Dict[str, Any], str]:
        """
        Extract YAML frontmatter from markdown content.
        
        Args:
            content: The markdown content
            
        Returns:
            Tuple[Dict, str]: A tuple of (frontmatter_dict, content_without_frontmatter)
        """
        import yaml
        
        # Check if the file has frontmatter (starts with ---)
        if not content.startswith('---'):
            return {}, content
            
        # Find the end of the frontmatter
        end_pos = content.find('---', 3)
        if end_pos == -1:
            return {}, content
            
        # Extract and parse frontmatter
        frontmatter_yaml = content[3:end_pos].strip()
        try:
            frontmatter = yaml.safe_load(frontmatter_yaml) or {}
        except yaml.YAMLError:
            # If YAML parsing fails, return empty dict
            frontmatter = {}
            
        # Return frontmatter and content without frontmatter
        content_without_frontmatter = content[end_pos + 3:].strip()
        return frontmatter, content_without_frontmatter
    
    def extract_links(self, content: str) -> list:
        """
        Extract Obsidian links from markdown content.
        
        Args:
            content: The markdown content
            
        Returns:
            list: A list of extracted links
        """
        import re
        
        # Pattern for [[link]] syntax
        wikilink_pattern = r'\[\[(.*?)(?:\|(.*?))?\]\]'
        
        # Find all matches
        matches = re.findall(wikilink_pattern, content)
        
        # Process matches into standardized format
        links = []
        for match in matches:
            target = match[0].strip()
            alias = match[1].strip() if match[1] else None
            links.append({
                'target': target,
                'alias': alias
            })
            
        return links
    
    def _calculate_hash(self, content: str) -> str:
        """
        Calculate a SHA-256 hash of the content.
        
        Args:
            content: The content to hash
            
        Returns:
            str: The hexadecimal hash string
        """
        return hashlib.sha256(content.encode('utf-8')).hexdigest()