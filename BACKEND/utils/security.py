import re
import hashlib
from typing import Optional

def sanitize_password_input(password: str, max_length: int = 256) -> Optional[str]:
    """
    Sanitize password input with basic validation
    
    Args:
        password: The password to sanitize
        max_length: Maximum allowed password length
    
    Returns:
        Sanitized password or None if invalid
    """
    if not password or not isinstance(password, str):
        return None
    
    # Remove excessive whitespace
    sanitized = password.strip()
    
    # Check length limits
    if len(sanitized) < 1 or len(sanitized) > max_length:
        return None
    
    # Check for suspicious patterns (basic XSS prevention)
    suspicious_patterns = [
        r'<script.*?>.*?</script>',
        r'javascript:',
        r'on\w+=',
        r'<iframe.*?>',
        r'vbscript:',
        r'expression\(.*\)'
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, sanitized, re.IGNORECASE):
            return None
    
    return sanitized

def hash_password_for_hibp(password: str) -> str:
    """
    Hash password for Have I Been Pwned API check
    
    Args:
        password: Password to hash
    
    Returns:
        SHA-1 hash in uppercase
    """
    return hashlib.sha1(password.encode('utf-8')).hexdigest().upper()

def is_suspicious_input(text: str) -> bool:
    """
    Check for potentially malicious input patterns
    
    Args:
        text: Input text to check
    
    Returns:
        True if suspicious patterns found
    """
    if not text:
        return False
    
    suspicious_patterns = [
        r'<script.*?>',
        r'javascript:',
        r'on\w+=',
        r'<iframe.*?>',
        r'vbscript:',
        r'expression\(.*\)',
        r'eval\(.*\)',
        r'alert\(.*\)',
        r'document\.cookie',
        r'window\.location',
        r'document\.write'
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    return False

def calculate_password_entropy(password: str) -> float:
    """
    Calculate Shannon entropy of password
    
    Args:
        password: Password to analyze
    
    Returns:
        Entropy bits
    """
    if len(password) <= 1:
        return 0.0
    
    # Calculate frequency of each character
    freq = {}
    for char in password:
        freq[char] = freq.get(char, 0) + 1
    
    # Calculate entropy
    entropy = 0.0
    length = len(password)
    
    for count in freq.values():
        p = count / length
        entropy -= p * (p and math.log2(p))  # Avoid log(0)
    
    return entropy * length

def contains_common_patterns(password: str) -> list:
    """
    Check for common password patterns
    
    Args:
        password: Password to check
    
    Returns:
        List of detected patterns
    """
    patterns = []
    password_lower = password.lower()
    
    # Keyboard patterns
    keyboard_patterns = [
        'qwerty', 'asdfgh', 'zxcvbn', '123456', 'abcdef',
        'yxcvbnm', 'poiuyt', 'lkjhgf', 'mnbvcx', '1qaz2wsx',
        '1q2w3e4r', '1q2w3e', 'zaq12wsx', '!qaz2wsx'
    ]
    
    for pattern in keyboard_patterns:
        if pattern in password_lower:
            patterns.append(f"keyboard_pattern_{pattern}")
    
    # Sequential characters
    if has_sequential_chars(password, 4):
        patterns.append("sequential_chars")
    
    # Repeated characters
    if re.search(r'(.)\1{2,}', password):  # 3 or more repeated
        patterns.append("repeated_chars")
    
    # Common number patterns
    number_patterns = [
        r'^1234567890$',
        r'^123456789$',
        r'^12345678$',
        r'^1234567$',
        r'^123456$',
        r'^12345$',
        r'^1234$',
        r'^123$',
        r'^111111$',
        r'^000000$',
        r'^121212$',
        r'^112233$'
    ]
    
    for pattern in number_patterns:
        if re.match(pattern, password):
            patterns.append("common_number_pattern")
            break
    
    return patterns

def has_sequential_chars(text: str, min_seq: int = 4) -> bool:
    """
    Check for sequential characters
    
    Args:
        text: Text to check
        min_seq: Minimum sequence length
    
    Returns:
        True if sequential characters found
    """
    if len(text) < min_seq:
        return False
    
    for i in range(len(text) - min_seq + 1):
        segment = text[i:i+min_seq]
        
        # Check ascending
        asc_diffs = [ord(segment[j+1]) - ord(segment[j]) for j in range(min_seq-1)]
        # Check descending  
        desc_diffs = [ord(segment[j]) - ord(segment[j+1]) for j in range(min_seq-1)]
        
        if all(diff == 1 for diff in asc_diffs) or all(diff == 1 for diff in desc_diffs):
            return True
    
    return False