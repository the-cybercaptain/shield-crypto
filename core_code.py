#!/usr/bin/env python3 
""" 
╔════════════════════════════════════════════════════════╗ 
║           SECURE TOOL - Core Encryption Engine        ║ 
║     AES-GCM + ChaCha20-Poly1305 Double Encryption    ║ 
║              PURE BINARY FILE FORMAT                  ║ 
╚════════════════════════════════════════════════════════╝ 
""" 
 
import os 
import base64 
import string 
import random 
import secrets 
import hashlib 
import re 
import struct 
import zlib 
from datetime import datetime 
from pathlib import Path 
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305 
from cryptography.hazmat.backends import default_backend 
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC 
from cryptography.hazmat.primitives import hashes 
 
# ───────────────────────────────────────────── 
#  CONSTANTS 
# ───────────────────────────────────────────── 
 
HISTORY_FILE = "encryption_history.txt" 
MAGIC_HEADER = b"SHLDCRYPTO"  # 10 bytes magic 
VERSION = 3 
 
SPECIAL_MAP = { 
    ' ': '_SPC_', '.': '_DOT_', '@': '_AT_', '!': '_EXCL_', '?': '_QSTN_', 
    ',': '_COMMA_', ':': '_COLON_', ';': '_SEMICOLON_', 
    "'": '_SQUOTE_', '"': '_DQUOTE_', '/': '_SLASH_', '\\': '_BSLASH_', 
    '(': '_LPAREN_', ')': '_RPAREN_', '-': '_DASH_', '_': '_UNDERSCORE_' 
} 
REVERSE_MAP = {v: k for k, v in SPECIAL_MAP.items()} 
 
CAESAR_SHIFT = 3 
 
# ───────────────────────────────────────────── 
#  KEY DERIVATION 
# ───────────────────────────────────────────── 
 
def derive_key_from_password(password: str, salt: bytes = None): 
    if salt is None: 
        salt = secrets.token_bytes(16) 
    kdf = PBKDF2HMAC( 
        algorithm=hashes.SHA256(), 
        length=32, 
        salt=salt, 
        iterations=100_000, 
        backend=default_backend() 
    ) 
    key = kdf.derive(password.encode()) 
    return key, salt 
 
 
def encrypt_keys_with_password(aes_key: bytes, chacha_key: bytes, password: str) -> bytes: 
    enc_key, salt = derive_key_from_password(password) 
    combined = aes_key + chacha_key 
    aesgcm = AESGCM(enc_key) 
    nonce = secrets.token_bytes(12) 
    ciphertext = aesgcm.encrypt(nonce, combined, None) 
    return salt + nonce + ciphertext 
 
 
def decrypt_keys_with_password(encrypted_keys_data: bytes, password: str): 
    try: 
        salt = encrypted_keys_data[:16] 
        nonce = encrypted_keys_data[16:28] 
        ciphertext = encrypted_keys_data[28:] 
        enc_key, _ = derive_key_from_password(password, salt) 
        aesgcm = AESGCM(enc_key) 
        combined = aesgcm.decrypt(nonce, ciphertext, None) 
        return combined[:32], combined[32:64] 
    except Exception: 
        return None, None 
 
# ───────────────────────────────────────────── 
#  AES-GCM 
# ───────────────────────────────────────────── 
 
def generate_aes_key() -> bytes: 
    return secrets.token_bytes(32) 
 
 
def aes_gcm_encrypt(data: bytes, key: bytes) -> bytes: 
    aesgcm = AESGCM(key) 
    nonce = secrets.token_bytes(12) 
    return nonce + aesgcm.encrypt(nonce, data, None) 
 
 
def aes_gcm_decrypt(encrypted_data: bytes, key: bytes) -> bytes: 
    nonce, ciphertext = encrypted_data[:12], encrypted_data[12:] 
    return AESGCM(key).decrypt(nonce, ciphertext, None) 
 
# ───────────────────────────────────────────── 
#  CHACHA20-POLY1305 
# ───────────────────────────────────────────── 
 
def generate_chacha_key() -> bytes: 
    return secrets.token_bytes(32) 
 
 
def chacha_encrypt(data: bytes, key: bytes) -> bytes: 
    chacha = ChaCha20Poly1305(key) 
    nonce = secrets.token_bytes(12) 
    return nonce + chacha.encrypt(nonce, data, None) 
 
 
def chacha_decrypt(encrypted_data: bytes, key: bytes) -> bytes: 
    nonce, ciphertext = encrypted_data[:12], encrypted_data[12:] 
    return ChaCha20Poly1305(key).decrypt(nonce, ciphertext, None) 
 
# ───────────────────────────────────────────── 
#  CAESAR + ROTATION HELPERS 
# ───────────────────────────────────────────── 
 
def _shift_char(c: str, shift: int) -> str: 
    if c.isalpha(): 
        base = ord('A') if c.isupper() else ord('a') 
        return chr((ord(c) - base + shift) % 26 + base) 
    if c in SPECIAL_MAP: 
        return SPECIAL_MAP[c] 
    return f'_UNK_{ord(c)}_' 
 
 
def _unshift_char(c: str, shift: int) -> str: 
    if len(c) == 1 and c.isalpha(): 
        base = ord('A') if c.isupper() else ord('a') 
        return chr((ord(c) - base - shift) % 26 + base) 
    return c 
 
 
def _random_str(length: int) -> str: 
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length)) 
 
# ───────────────────────────────────────────── 
#  MESSAGE ENCRYPTION 
# ───────────────────────────────────────────── 
 
def encrypt_message(message: str, password: str, padding: int = 3) -> dict: 
    try: 
        aes_key = generate_aes_key() 
        chacha_key = generate_chacha_key() 
        encrypted_keys = encrypt_keys_with_password(aes_key, chacha_key, password) 
 
        words = message.split(" ") 
        encoded_words = [] 
 
        for word in words: 
            rotated = word[1:] + word[0] if len(word) > 1 else word 
            shifted = ''.join(_shift_char(c, CAESAR_SHIFT) for c in rotated) 
            aes_enc = aes_gcm_encrypt(shifted.encode(), aes_key) 
            chacha_enc = chacha_encrypt(aes_enc, chacha_key) 
            padded = _random_str(padding) + base64.b64encode(chacha_enc).decode() + _random_str(padding) 
            encoded_words.append(padded) 
 
        intermediate = " ".join(encoded_words) 
        text_data = ( 
            base64.b64encode(encrypted_keys).decode() 
            + "||" + intermediate 
            + "||" + str(padding) 
            + "||message" 
        ) 
        compressed = zlib.compress(text_data.encode(), level=9) 
        output = MAGIC_HEADER + struct.pack('!H', VERSION) + compressed 
         
        return {'success': True, 'output_data': bytes(output), 'padding': padding} 
    except Exception as e: 
        return {'success': False, 'error': str(e)} 
 
 
def decrypt_message(file_content: bytes, password: str, padding: int = 3) -> dict: 
    """Decrypt message with given padding""" 
    try: 
        if not file_content.startswith(MAGIC_HEADER): 
            return {'success': False, 'error': 'Invalid file format - no magic header found', 'wrong_password': False} 
         
        pos = len(MAGIC_HEADER) 
        if len(file_content) < pos + 2: 
            return {'success': False, 'error': 'Invalid file format', 'wrong_password': False} 
         
        version = struct.unpack('!H', file_content[pos:pos+2])[0] 
        pos += 2 
         
        try: 
            decompressed = zlib.decompress(file_content[pos:]) 
            text_content = decompressed.decode('utf-8') 
        except: 
            return {'success': False, 'error': 'Invalid or corrupted file format', 'wrong_password': False} 
         
        parts = text_content.split("||") 
        if len(parts) < 4: 
            return {'success': False, 'error': 'Invalid file format', 'wrong_password': False} 
         
        encrypted_keys_b64, encrypted_text, stored_padding_str, file_type = parts[0], parts[1], parts[2], parts[3] 
         
        if file_type.strip() != "message": 
            return {'success': False, 'error': 'Not a message file — use File Decrypt', 'wrong_password': False} 
         
        encrypted_keys = base64.b64decode(encrypted_keys_b64) 
        aes_key, chacha_key = decrypt_keys_with_password(encrypted_keys, password) 
         
        if aes_key is None: 
            return {'success': False, 'error': 'Wrong master password', 'wrong_password': True} 
         
        length = padding 
        words = encrypted_text.split(" ") 
        decoded_words = [] 
        shift = 3 
         
        for word in words: 
            core = word[length:-length] if len(word) >= 2 * length else word 
            try: 
                chacha_enc = base64.b64decode(core) 
            except: 
                decoded_words.append("[DECODE ERROR]") 
                continue 
            try: 
                aes_enc = chacha_decrypt(chacha_enc, chacha_key) 
            except: 
                decoded_words.append("[CHACHA20 ERROR]") 
                continue 
            try: 
                decrypted_bytes = aes_gcm_decrypt(aes_enc, aes_key) 
                shifted_text = decrypted_bytes.decode() 
            except: 
                decoded_words.append("[AES-GCM ERROR]") 
                continue 
 
            parts_list = [] 
            i = 0 
            while i < len(shifted_text): 
                if shifted_text[i] == '_': 
                    end = shifted_text.find('_', i + 1) 
                    if end == -1: 
                        parts_list.append(shifted_text[i]) 
                        i += 1 
                        continue 
                    token = shifted_text[i:end + 1] 
                    if token in REVERSE_MAP: 
                        parts_list.append(REVERSE_MAP[token]) 
                        i = end + 1 
                    elif shifted_text[i:].startswith('_UNK_'): 
                        end2 = shifted_text.find('_', i + 5) 
                        if end2 == -1: 
                            parts_list.append(shifted_text[i]) 
                            i += 1 
                            continue 
                        ascii_code = int(shifted_text[i + 5:end2]) 
                        parts_list.append(chr(ascii_code)) 
                        i = end2 + 1 
                    else: 
                        parts_list.append(shifted_text[i]) 
                        i += 1 
                else: 
                    parts_list.append(shifted_text[i]) 
                    i += 1 
 
            unshifted = ''.join(_unshift_char(c, CAESAR_SHIFT) for c in parts_list) 
            original = unshifted[-1] + unshifted[:-1] if len(unshifted) > 1 else unshifted 
            decoded_words.append(original) 
         
        real_message = ' '.join(decoded_words) 
        return {'success': True, 'message': real_message} 
         
    except Exception as e: 
        return {'success': False, 'error': str(e), 'wrong_password': False} 
 
# ───────────────────────────────────────────── 
#  FILE ENCRYPTION / DECRYPTION 
# ───────────────────────────────────────────── 
 
def encrypt_file_data(file_bytes: bytes, password: str, original_ext: str = "") -> dict: 
    try: 
        compressed = zlib.compress(file_bytes, level=9) 
        aes_key = generate_aes_key() 
        chacha_key = generate_chacha_key() 
        encrypted_keys = encrypt_keys_with_password(aes_key, chacha_key, password) 
        aes_encrypted = aes_gcm_encrypt(compressed, aes_key) 
        chacha_encrypted = chacha_encrypt(aes_encrypted, chacha_key) 
        output = bytearray() 
        output.extend(MAGIC_HEADER) 
        output.extend(struct.pack('!H', VERSION)) 
        output.extend(encrypted_keys) 
        output.extend(struct.pack('!I', len(original_ext))) 
        output.extend(original_ext.encode()) 
        output.extend(chacha_encrypted) 
        return {'success': True, 'output_data': bytes(output), 'original_ext': original_ext} 
    except Exception as e: 
        return {'success': False, 'error': str(e)} 
 
 
def decrypt_file_data(encrypted_data: bytes, password: str) -> dict: 
    try: 
        if not encrypted_data.startswith(MAGIC_HEADER): 
            return {'success': False, 'error': 'Invalid file format - no magic header found', 'wrong_password': False} 
         
        version_pos = len(MAGIC_HEADER) 
        if len(encrypted_data) < version_pos + 2: 
            return {'success': False, 'error': 'Invalid file format', 'wrong_password': False} 
         
        version = struct.unpack('!H', encrypted_data[version_pos:version_pos+2])[0] 
        encrypted_keys_pos = version_pos + 2 
        encrypted_keys = encrypted_data[encrypted_keys_pos:encrypted_keys_pos + 108] 
         
        ext_len_pos = encrypted_keys_pos + 108 
        if len(encrypted_data) < ext_len_pos + 4: 
            return {'success': False, 'error': 'Invalid file format', 'wrong_password': False} 
         
        ext_len = struct.unpack('!I', encrypted_data[ext_len_pos:ext_len_pos+4])[0] 
        ext_pos = ext_len_pos + 4 
        original_ext = encrypted_data[ext_pos:ext_pos + ext_len].decode() 
         
        encrypted_content_pos = ext_pos + ext_len 
        encrypted_content = encrypted_data[encrypted_content_pos:] 
         
        if len(encrypted_content) < 12: 
            return {'success': False, 'error': 'Invalid file format', 'wrong_password': False} 
         
        aes_key, chacha_key = decrypt_keys_with_password(encrypted_keys, password) 
         
        if aes_key is None: 
            return {'success': False, 'error': 'Wrong master password', 'wrong_password': True} 
         
        try: 
            aes_enc = chacha_decrypt(encrypted_content, chacha_key) 
            decompressed = aes_gcm_decrypt(aes_enc, aes_key) 
            original_data = zlib.decompress(decompressed) 
            return {'success': True, 'data': original_data, 'original_ext': original_ext} 
        except Exception as e: 
            return {'success': False, 'error': f'Decryption failed: {str(e)}', 'wrong_password': False} 
             
    except Exception as e: 
        return {'success': False, 'error': str(e), 'wrong_password': False} 
 
# ───────────────────────────────────────────── 
#  HISTORY & HELPERS 
# ───────────────────────────────────────────── 
 
def save_to_history(identifier: str, msg_type: str = "MESSAGE", padding=None, original_ext=None): 
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
    line_parts = [f"[+] {timestamp}", f"{msg_type}: {identifier}"] 
    if padding: 
        line_parts.append(f"PADDING: {padding}") 
    if original_ext: 
        line_parts.append(f"ORIGINAL_EXT: {original_ext}") 
    line = " | ".join(line_parts) + "\n\n" 
    with open(HISTORY_FILE, "a") as f: 
        f.write(line) 
 
 
def load_history() -> str: 
    if not os.path.exists(HISTORY_FILE): 
        return "" 
    with open(HISTORY_FILE, "r") as f: 
        return f.read() 
 
 
def clear_history() -> bool: 
    if os.path.exists(HISTORY_FILE): 
        os.remove(HISTORY_FILE) 
        return True 
    return False 
 
 
def validate_password(password: str) -> tuple[bool, str]: 
    if not password: 
        return False, "Password cannot be empty" 
    if len(password) < 6: 
        return False, "Password must be at least 6 characters" 
    return True, "" 
 
 
def validate_message(message: str) -> tuple[bool, str]: 
    if not message.strip(): 
        return False, "Message cannot be empty" 
    return True, "" 
 
 
def validate_padding(value: str, default: int = 3) -> tuple[bool, int, str]: 
    if not value.strip(): 
        return True, default, "" 
    try: 
        num = int(value.strip()) 
        if num < 1: 
            return False, default, "Minimum 1" 
        if num > 1000: 
            return False, default, "Maximum 1000" 
        return True, num, "" 
    except ValueError: 
        return False, default, "Must be a number" 
 
 
def read_enc_file(path: str) -> tuple[bytes | None, str]: 
    try: 
        with open(path, "rb") as f: 
            return f.read(), "" 
    except Exception as e: 
        return None, str(e) 
 
 
def write_file(path: str, content: str) -> tuple[bool, str]: 
    try: 
        with open(path, "w") as f: 
            f.write(content) 
        return True, "" 
    except Exception as e: 
        return False, str(e) 
 
 
def write_binary_file(path: str, data: bytes) -> tuple[bool, str]: 
    try: 
        with open(path, "wb") as f: 
            f.write(data) 
        return True, "" 
    except Exception as e: 
        return False, str(e) 
 
 
def get_file_size(path: str) -> int: 
    try: 
        return os.path.getsize(path) 
    except Exception: 
        return -1