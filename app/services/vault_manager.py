import os
from pathlib import Path
from typing import List, Optional, Dict
from app.db.models import Vault, Document
from app.db.session import get_db_context
from app.services.file_parser import FileParser


class VaultManager:
    """
    Class responsible for managing Obsidian vaults.
    Handles vault registration, scanning, and content updates.
    """
    
    def __init__(self):
        self.parser = FileParser()
        
    def register_vault(self, name: str, path: str) -> Vault:
        """
        Register a new Obsidian vault.
        
        Args:
            name: The name to identify the vault
            path: The file system path to the vault root
            
        Returns:
            Vault: The newly created vault object
        """
        # Validate path exists
        vault_path = Path(path)
        if not vault_path.exists() or not vault_path.is_dir():
            raise ValueError(f"Path '{path}' does not exist or is not a directory")
            
        with get_db_context() as db:
            # Check if vault with this path already exists
            existing_vault = db.query(Vault).filter(Vault.path == str(vault_path.resolve())).first()
            if existing_vault:
                raise ValueError(f"A vault with path '{path}' is already registered")
                
            # Create new vault
            vault = Vault(name=name, path=str(vault_path.resolve()))
            db.add(vault)
            db.flush()
            
            return vault
    
    def get_vault(self, vault_id: str) -> Optional[Vault]:
        """
        Get a vault by its ID.
        
        Args:
            vault_id: The ID of the vault to retrieve
            
        Returns:
            Vault or None: The vault object if found, None otherwise
        """
        with get_db_context() as db:
            return db.query(Vault).filter(Vault.id == vault_id).first()
    
    def get_all_vaults(self) -> List[Vault]:
        """
        Get all registered vaults.
        
        Returns:
            List[Vault]: A list of all registered vault objects
        """
        with get_db_context() as db:
            return db.query(Vault).all()
    
    def scan_vault(self, vault_id: str) -> Dict:
        """
        Scan vault for markdown files and update the database.
        
        Args:
            vault_id: The ID of the vault to scan
            
        Returns:
            Dict: Statistics about the scan results
        """
        # First, get vault path outside of db context
        vault = self.get_vault(vault_id)
        if not vault:
            raise ValueError(f"Vault with ID '{vault_id}' not found")
            
        vault_path = Path(vault.path)
        if not vault_path.exists():
            raise ValueError(f"Vault path '{vault.path}' does not exist")
        
        stats = {
            "total_files": 0,
            "new_files": 0,
            "updated_files": 0,
            "unchanged_files": 0,
            "errors": 0
        }
        
        # Walk through the vault directory
        markdown_files = list(vault_path.glob("**/*.md"))
        stats["total_files"] = len(markdown_files)
        
        with get_db_context() as db:
            # Re-query vault within this session to update it
            vault_in_session = db.query(Vault).filter(Vault.id == vault_id).first()
            
            # Get existing documents for this vault
            existing_docs = db.query(Document).filter(Document.vault_id == vault_id).all()
            existing_paths = {doc.path: doc for doc in existing_docs}
            
            for file_path in markdown_files:
                relative_path = str(file_path.relative_to(vault_path))
                absolute_path = str(file_path)
                
                try:
                    # Parse the file to get content and hash
                    content, content_hash = self.parser.parse_file(absolute_path)
                    
                    if relative_path in existing_paths:
                        # File exists in DB, check if content changed
                        doc = existing_paths[relative_path]
                        if doc.content_hash != content_hash:
                            # Update the document
                            doc.content_hash = content_hash
                            stats["updated_files"] += 1
                        else:
                            stats["unchanged_files"] += 1
                    else:
                        # New file, add to database
                        new_doc = Document(
                            vault_id=vault_id,
                            path=relative_path,
                            filename=file_path.name,
                            content_hash=content_hash
                        )
                        db.add(new_doc)
                        stats["new_files"] += 1
                except Exception as e:
                    stats["errors"] += 1
                    print(f"Error processing file {file_path}: {str(e)}")
                    
            # Update vault status
            if vault_in_session:
                vault_in_session.is_indexed = True
            
        return stats
    
    def delete_vault(self, vault_id: str) -> bool:
        """
        Delete a vault and all its associated data.
        
        Args:
            vault_id: The ID of the vault to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        with get_db_context() as db:
            vault = db.query(Vault).filter(Vault.id == vault_id).first()
            if not vault:
                return False
                
            db.delete(vault)
            return True