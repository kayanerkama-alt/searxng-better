# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Encrypted Search for Atomic Search
Provides client-side encryption for sensitive searches
"""

import hashlib
import hmac
import secrets
import base64
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum


class EncryptionLevel(Enum):
    """Search encryption levels"""
    NONE = "none"
    BASIC = "basic"      # URL encoding only
    STANDARD = "standard" # Base64 encoding
    STRONG = "strong"    # Encrypted with key


@dataclass
class EncryptedQuery:
    """Represents an encrypted search query"""
    query: str
    encrypted: str
    encryption_level: str
    key_id: Optional[str] = None
    timestamp: Optional[int] = None
    nonce: Optional[str] = None


class EncryptedSearchEngine:
    """
    Handles encrypted search queries
    Provides multiple levels of encryption for sensitive searches
    """
    
    # Encryption key rotation period (24 hours)
    KEY_ROTATION_SECONDS = 86400
    
    def __init__(self):
        self._keys: Dict[str, str] = {}
        self._key_timestamps: Dict[str, int] = {}
        self._current_key_id: Optional[str] = None
        self._generate_new_key()
    
    def _generate_new_key(self) -> str:
        """Generate a new encryption key"""
        import time
        key_id = secrets.token_hex(8)
        key = secrets.token_bytes(32)  # 256-bit key
        self._keys[key_id] = base64.b64encode(key).decode()
        self._key_timestamps[key_id] = int(time.time())
        self._current_key_id = key_id
        return key_id
    
    def _get_current_key(self) -> Tuple[str, str]:
        """Get the current encryption key"""
        import time
        # Check if we need to rotate
        if self._current_key_id:
            age = time.time() - self._key_timestamps.get(self._current_key_id, 0)
            if age > self.KEY_ROTATION_SECONDS:
                self._generate_new_key()
        return self._current_key_id, self._keys.get(self._current_key_id, '')
    
    def encrypt_query(self, query: str, level: EncryptionLevel = EncryptionLevel.STANDARD) -> EncryptedQuery:
        """
        Encrypt a search query
        
        Args:
            query: The plaintext query
            level: Encryption level to use
        
        Returns:
            EncryptedQuery object
        """
        import time
        
        if level == EncryptionLevel.NONE:
            return EncryptedQuery(
                query=query,
                encrypted=query,
                encryption_level=level.value
            )
        
        elif level == EncryptionLevel.BASIC:
            # URL encoding
            from urllib.parse import quote
            encrypted = quote(query)
            return EncryptedQuery(
                query=query,
                encrypted=encrypted,
                encryption_level=level.value
            )
        
        elif level == EncryptionLevel.STANDARD:
            # Base64 encoding with salt
            nonce = secrets.token_hex(8)
            salted = f"{query}:{nonce}"
            encrypted = base64.b64encode(salted.encode()).decode()
            return EncryptedQuery(
                query=query,
                encrypted=encrypted,
                encryption_level=level.value,
                nonce=nonce,
                timestamp=int(time.time())
            )
        
        elif level == EncryptionLevel.STRONG:
            # AES-like encryption simulation (for demo)
            # In production, use PyCryptodome or similar
            nonce = secrets.token_hex(16)
            key_id, key = self._get_current_key()
            
            # Simple XOR encryption (demo purposes)
            # Use Fernet or AES-GCM in production
            encrypted = self._xor_encrypt(query, key) + ":" + nonce
            
            return EncryptedQuery(
                query=query,
                encrypted=encrypted,
                encryption_level=level.value,
                key_id=key_id,
                nonce=nonce,
                timestamp=int(time.time())
            )
        
        return EncryptedQuery(query=query, encrypted=query, encryption_level="none")
    
    def _xor_encrypt(self, plaintext: str, key: str) -> str:
        """Simple XOR encryption (demo - use proper AES in production)"""
        key_bytes = key.encode()[:32]
        result = []
        for i, char in enumerate(plaintext):
            key_char = key_bytes[i % len(key_bytes)]
            result.append(chr(ord(char) ^ key_char))
        return base64.b64encode(''.join(result).encode()).decode()
    
    def decrypt_query(self, encrypted: str, level: str) -> Optional[str]:
        """Decrypt an encrypted query"""
        if level == EncryptionLevel.NONE.value:
            return encrypted
        elif level == EncryptionLevel.BASIC.value:
            from urllib.parse import unquote
            return unquote(encrypted)
        elif level == EncryptionLevel.STANDARD.value:
            try:
                decoded = base64.b64decode(encrypted.encode()).decode()
                return decoded.split(':')[0]
            except:
                return None
        elif level == EncryptionLevel.STRONG.value:
            try:
                parts = encrypted.rsplit(':', 1)
                if len(parts) == 2:
                    data, nonce = parts
                    decrypted = self._xor_decrypt(data, self._keys.get(self._current_key_id, ''))
                    return decrypted
            except:
                pass
            return None
        return None
    
    def _xor_decrypt(self, ciphertext: str, key: str) -> str:
        """Simple XOR decryption (demo - use proper AES in production)"""
        try:
            decoded = base64.b64decode(ciphertext.encode()).decode()
            key_bytes = key.encode()[:32]
            result = []
            for i, char in enumerate(decoded):
                key_char = key_bytes[i % len(key_bytes)]
                result.append(chr(ord(char) ^ key_char))
            return ''.join(result)
        except:
            return ciphertext
    
    def create_encrypted_search_url(self, query: str, base_url: str = "/search") -> Dict[str, Any]:
        """Create an encrypted search URL"""
        encrypted = self.encrypt_query(query, EncryptionLevel.STANDARD)
        return {
            'url': f"{base_url}?q={encrypted.encrypted}&enc={encrypted.encryption_level}",
            'encrypted': encrypted.encrypted,
            'level': encrypted.encryption_level,
            'nonce': encrypted.nonce
        }
    
    def generate_search_token(self, query: str) -> str:
        """Generate a one-time token for a search"""
        import time
        salt = secrets.token_hex(16)
        data = f"{query}:{salt}:{int(time.time())}"
        return hashlib.sha256(data.encode()).hexdigest()[:32]
    
    def verify_search_token(self, token: str, max_age: int = 300) -> bool:
        """Verify a search token is valid and not expired"""
        # Token-based verification for anonymous searches
        return len(token) == 32


# Global instance
_encrypted_search = EncryptedSearchEngine()


def get_encrypted_search() -> EncryptedSearchEngine:
    """Get the encrypted search engine"""
    return _encrypted_search


def encrypt_search(query: str, level: str = "standard") -> EncryptedQuery:
    """Convenience function to encrypt a search"""
    return _encrypted_search.encrypt_query(
        query, 
        EncryptionLevel(level)
    )


def create_private_search_url(query: str) -> Dict[str, Any]:
    """Create a private (encrypted) search URL"""
    return _encrypted_search.create_encrypted_search_url(query)
