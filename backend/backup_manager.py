"""
Backup & Disaster Recovery Manager for ServerCraft
Handles automated backups, encryption, compression, and restoration
"""

import os
import tarfile
import shutil
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import subprocess
import logging

logger = logging.getLogger(__name__)

class BackupManager:
    """Manage backups for ServerCraft"""
    
    def __init__(self, backup_dir: str = "/app/backups", encryption_key: Optional[str] = None):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True, parents=True)
        self.encryption_key = encryption_key
        
    def generate_encryption_key(self, password: str, salt: Optional[bytes] = None) -> bytes:
        """
        Generate encryption key from password using PBKDF2
        
        Args:
            password: User password for encryption
            salt: Salt for key derivation (generated if not provided)
            
        Returns:
            Encryption key bytes
        """
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt
    
    def create_mongodb_backup(self, db_name: str, output_path: Path) -> bool:
        """
        Create MongoDB backup using mongodump
        
        Args:
            db_name: Database name
            output_path: Output directory
            
        Returns:
            True if successful
        """
        try:
            output_path.mkdir(exist_ok=True, parents=True)
            
            # Run mongodump
            result = subprocess.run(
                [
                    "mongodump",
                    "--db", db_name,
                    "--out", str(output_path),
                    "--quiet"
                ],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                logger.info(f"MongoDB backup created: {output_path}")
                return True
            else:
                logger.error(f"MongoDB backup failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("MongoDB backup timeout")
            return False
        except Exception as e:
            logger.error(f"MongoDB backup error: {e}")
            return False
    
    def create_files_backup(self, source_dirs: List[str], output_path: Path) -> bool:
        """
        Create backup of files from specified directories
        
        Args:
            source_dirs: List of directories to backup
            output_path: Output directory
            
        Returns:
            True if successful
        """
        try:
            output_path.mkdir(exist_ok=True, parents=True)
            
            for source_dir in source_dirs:
                if not os.path.exists(source_dir):
                    logger.warning(f"Source directory not found: {source_dir}")
                    continue
                
                # Copy directory to backup location
                dest_dir = output_path / Path(source_dir).name
                if dest_dir.exists():
                    shutil.rmtree(dest_dir)
                shutil.copytree(source_dir, dest_dir, symlinks=False, ignore_dangling_symlinks=True)
                logger.info(f"Files backed up: {source_dir} -> {dest_dir}")
            
            return True
            
        except Exception as e:
            logger.error(f"Files backup error: {e}")
            return False
    
    def compress_backup(self, source_path: Path, output_file: Path) -> bool:
        """
        Compress backup directory to tar.gz
        
        Args:
            source_path: Directory to compress
            output_file: Output tar.gz file
            
        Returns:
            True if successful
        """
        try:
            with tarfile.open(output_file, "w:gz") as tar:
                tar.add(source_path, arcname=source_path.name)
            
            logger.info(f"Backup compressed: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Compression error: {e}")
            return False
    
    def encrypt_backup(self, input_file: Path, output_file: Path, password: str) -> tuple[bool, Optional[bytes]]:
        """
        Encrypt backup file using Fernet (AES-256)
        
        Args:
            input_file: Input file to encrypt
            output_file: Output encrypted file
            password: Encryption password
            
        Returns:
            (success, salt) tuple
        """
        try:
            # Generate encryption key
            key, salt = self.generate_encryption_key(password)
            fernet = Fernet(key)
            
            # Read and encrypt file
            with open(input_file, 'rb') as f:
                data = f.read()
            
            encrypted_data = fernet.encrypt(data)
            
            # Write encrypted file
            with open(output_file, 'wb') as f:
                f.write(encrypted_data)
            
            logger.info(f"Backup encrypted: {output_file}")
            return True, salt
            
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            return False, None
    
    def decrypt_backup(self, input_file: Path, output_file: Path, password: str, salt: bytes) -> bool:
        """
        Decrypt backup file
        
        Args:
            input_file: Encrypted input file
            output_file: Decrypted output file
            password: Decryption password
            salt: Salt used for key derivation
            
        Returns:
            True if successful
        """
        try:
            # Regenerate encryption key
            key, _ = self.generate_encryption_key(password, salt)
            fernet = Fernet(key)
            
            # Read and decrypt file
            with open(input_file, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = fernet.decrypt(encrypted_data)
            
            # Write decrypted file
            with open(output_file, 'wb') as f:
                f.write(decrypted_data)
            
            logger.info(f"Backup decrypted: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            return False
    
    def decompress_backup(self, input_file: Path, output_dir: Path) -> bool:
        """
        Decompress tar.gz backup
        
        Args:
            input_file: Tar.gz file to decompress
            output_dir: Output directory
            
        Returns:
            True if successful
        """
        try:
            output_dir.mkdir(exist_ok=True, parents=True)
            
            with tarfile.open(input_file, "r:gz") as tar:
                tar.extractall(output_dir)
            
            logger.info(f"Backup decompressed: {output_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Decompression error: {e}")
            return False
    
    def calculate_checksum(self, file_path: Path) -> str:
        """
        Calculate SHA256 checksum of file
        
        Args:
            file_path: File to checksum
            
        Returns:
            Hex checksum string
        """
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def verify_backup(self, backup_file: Path, expected_checksum: str) -> bool:
        """
        Verify backup file integrity
        
        Args:
            backup_file: Backup file to verify
            expected_checksum: Expected SHA256 checksum
            
        Returns:
            True if checksum matches
        """
        try:
            actual_checksum = self.calculate_checksum(backup_file)
            is_valid = actual_checksum == expected_checksum
            
            if is_valid:
                logger.info(f"Backup verification passed: {backup_file}")
            else:
                logger.error(f"Backup verification failed: {backup_file}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Verification error: {e}")
            return False
    
    def create_full_backup(
        self,
        backup_id: str,
        db_name: str,
        file_dirs: List[str],
        password: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create complete backup (database + files + encrypt + compress)
        
        Args:
            backup_id: Unique backup identifier
            db_name: MongoDB database name
            file_dirs: Directories to backup
            password: Encryption password
            metadata: Additional metadata
            
        Returns:
            Backup metadata dict
        """
        try:
            timestamp = datetime.now(timezone.utc)
            date_dir = self.backup_dir / timestamp.strftime("%Y-%m-%d")
            date_dir.mkdir(exist_ok=True, parents=True)
            
            temp_dir = date_dir / f"temp_{backup_id}"
            temp_dir.mkdir(exist_ok=True)
            
            # Create database backup
            db_backup_success = self.create_mongodb_backup(db_name, temp_dir / "database")
            
            # Create files backup
            files_backup_success = self.create_files_backup(file_dirs, temp_dir / "files")
            
            if not db_backup_success and not files_backup_success:
                shutil.rmtree(temp_dir)
                raise Exception("Both database and files backup failed")
            
            # Compress
            compressed_file = date_dir / f"{backup_id}.tar.gz"
            if not self.compress_backup(temp_dir, compressed_file):
                raise Exception("Compression failed")
            
            # Calculate checksum before encryption
            checksum = self.calculate_checksum(compressed_file)
            
            # Encrypt
            encrypted_file = date_dir / f"{backup_id}.tar.gz.enc"
            encrypt_success, salt = self.encrypt_backup(compressed_file, encrypted_file, password)
            
            if not encrypt_success:
                raise Exception("Encryption failed")
            
            # Clean up temp files
            shutil.rmtree(temp_dir)
            compressed_file.unlink()
            
            # Get file size
            file_size = encrypted_file.stat().st_size
            
            # Create metadata
            backup_metadata = {
                "id": backup_id,
                "timestamp": timestamp.isoformat(),
                "file_path": str(encrypted_file),
                "file_size": file_size,
                "checksum": checksum,
                "salt": base64.b64encode(salt).decode(),
                "database_included": db_backup_success,
                "files_included": files_backup_success,
                "file_dirs": file_dirs,
                **metadata
            }
            
            logger.info(f"Full backup created: {backup_id}")
            return backup_metadata
            
        except Exception as e:
            logger.error(f"Full backup error: {e}")
            # Clean up on error
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            raise
    
    def restore_backup(
        self,
        backup_file: Path,
        password: str,
        salt_b64: str,
        db_name: str,
        restore_database: bool = True,
        restore_files: bool = True
    ) -> bool:
        """
        Restore backup
        
        Args:
            backup_file: Encrypted backup file
            password: Decryption password
            salt_b64: Base64 encoded salt
            db_name: Database name for restoration
            restore_database: Whether to restore database
            restore_files: Whether to restore files
            
        Returns:
            True if successful
        """
        try:
            salt = base64.b64decode(salt_b64)
            temp_dir = self.backup_dir / f"restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            temp_dir.mkdir(exist_ok=True)
            
            # Decrypt
            decrypted_file = temp_dir / "backup.tar.gz"
            if not self.decrypt_backup(backup_file, decrypted_file, password, salt):
                raise Exception("Decryption failed")
            
            # Decompress
            extract_dir = temp_dir / "extracted"
            if not self.decompress_backup(decrypted_file, extract_dir):
                raise Exception("Decompression failed")
            
            # Find the actual backup directory (should be only one)
            backup_dirs = list(extract_dir.iterdir())
            if not backup_dirs:
                raise Exception("No backup directory found")
            
            backup_content = backup_dirs[0]
            
            # Restore database
            if restore_database and (backup_content / "database").exists():
                db_dir = backup_content / "database" / db_name
                if db_dir.exists():
                    result = subprocess.run(
                        [
                            "mongorestore",
                            "--db", db_name,
                            "--drop",
                            str(db_dir),
                            "--quiet"
                        ],
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                    
                    if result.returncode != 0:
                        logger.error(f"Database restore failed: {result.stderr}")
                    else:
                        logger.info("Database restored successfully")
            
            # Restore files
            if restore_files and (backup_content / "files").exists():
                files_dir = backup_content / "files"
                for item in files_dir.iterdir():
                    if item.is_dir():
                        dest = Path("/") / item.name
                        if dest.exists():
                            shutil.rmtree(dest)
                        shutil.copytree(item, dest)
                        logger.info(f"Files restored: {item.name}")
            
            # Clean up
            shutil.rmtree(temp_dir)
            
            logger.info("Backup restoration completed")
            return True
            
        except Exception as e:
            logger.error(f"Restore error: {e}")
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            return False
    
    def rotate_backups(self, keep_count: int = 10) -> List[str]:
        """
        Rotate backups, keeping only the latest N backups
        
        Args:
            keep_count: Number of backups to keep
            
        Returns:
            List of deleted backup IDs
        """
        try:
            # Get all encrypted backup files
            backup_files = sorted(
                self.backup_dir.rglob("*.tar.gz.enc"),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            deleted = []
            for backup_file in backup_files[keep_count:]:
                backup_id = backup_file.stem.replace(".tar.gz", "")
                backup_file.unlink()
                deleted.append(backup_id)
                logger.info(f"Rotated old backup: {backup_id}")
            
            return deleted
            
        except Exception as e:
            logger.error(f"Backup rotation error: {e}")
            return []
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        List all available backups
        
        Returns:
            List of backup metadata
        """
        try:
            backup_files = sorted(
                self.backup_dir.rglob("*.tar.gz.enc"),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            backups = []
            for backup_file in backup_files:
                stat = backup_file.stat()
                backup_id = backup_file.stem.replace(".tar.gz", "")
                
                backups.append({
                    "id": backup_id,
                    "file_path": str(backup_file),
                    "file_size": stat.st_size,
                    "created_at": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
                    "modified_at": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat()
                })
            
            return backups
            
        except Exception as e:
            logger.error(f"List backups error: {e}")
            return []
    
    def delete_backup(self, backup_id: str) -> bool:
        """
        Delete a specific backup
        
        Args:
            backup_id: Backup ID to delete
            
        Returns:
            True if successful
        """
        try:
            backup_files = list(self.backup_dir.rglob(f"{backup_id}.tar.gz.enc"))
            
            if not backup_files:
                logger.warning(f"Backup not found: {backup_id}")
                return False
            
            for backup_file in backup_files:
                backup_file.unlink()
                logger.info(f"Backup deleted: {backup_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Delete backup error: {e}")
            return False
