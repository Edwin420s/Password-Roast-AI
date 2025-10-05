import json
import os
import re
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from flask import request

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def format_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.now().isoformat()

def save_analysis_log(analysis_data: Dict[str, Any], filename: str = "analysis_log.jsonl"):
    """
    Save analysis results for debugging (without passwords)
    
    Args:
        analysis_data: Analysis results
        filename: Log filename
    """
    try:
        # Remove password for security
        safe_data = {k: v for k, v in analysis_data.items() if k != 'password'}
        safe_data['timestamp'] = format_timestamp()
        safe_data['length'] = len(analysis_data.get('password', ''))
        
        # Create logs directory if it doesn't exist
        log_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, filename)
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(safe_data) + '\n')
            
    except Exception as e:
        logger.error(f"Failed to save analysis log: {e}")

def load_wordlist(filepath: str) -> set:
    """
    Load wordlist from file
    
    Args:
        filepath: Path to wordlist file
    
    Returns:
        Set of words
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return set(line.strip().lower() for line in f if line.strip())
    except FileNotFoundError:
        logger.warning(f"Wordlist file not found: {filepath}")
        return set()
    except Exception as e:
        logger.error(f"Error loading wordlist {filepath}: {e}")
        return set()

def get_client_ip() -> str:
    """
    Get client IP address from request
    
    Returns:
        Client IP address
    """
    if request:
        # Check for forwarded IP first
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')
        else:
            return request.remote_addr
    return 'unknown'

def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human readable string
    
    Args:
        seconds: Duration in seconds
    
    Returns:
        Formatted duration string
    """
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}m"
    else:
        return f"{seconds/3600:.1f}h"

def generate_password_suggestions(analysis: Dict[str, Any]) -> List[str]:
    """
    Generate password improvement suggestions
    
    Args:
        analysis: Password analysis results
    
    Returns:
        List of suggestions
    """
    suggestions = []
    password = analysis.get('password', '')
    length = len(password)
    classes = analysis.get('character_classes', {})
    
    # Length suggestions
    if length < 8:
        suggestions.append("Use at least 8 characters")
    elif length < 12:
        suggestions.append("Use 12+ characters for better security")
    elif length < 16:
        suggestions.append("Consider using 16+ characters for high security")
    
    # Character class suggestions
    if not classes.get('upper'):
        suggestions.append("Add uppercase letters (A-Z)")
    if not classes.get('lower'):
        suggestions.append("Add lowercase letters (a-z)")
    if not classes.get('digit'):
        suggestions.append("Add numbers (0-9)")
    if not classes.get('special'):
        suggestions.append("Add special characters (!@#$%^&*)")
    
    # Pattern suggestions
    if analysis.get('dictionary_matches'):
        suggestions.append("Avoid dictionary words from any language")
    
    if analysis.get('patterns_detected'):
        for pattern in analysis['patterns_detected']:
            if pattern['type'] == 'keyboard_pattern':
                suggestions.append("Avoid keyboard patterns (qwerty, 12345)")
            elif pattern['type'] == 'sequential_chars':
                suggestions.append("Avoid sequential characters (abcd, 1234)")
            elif pattern['type'] == 'repeated_chars':
                suggestions.append("Avoid repeated characters (aaa, 111)")
    
    if analysis.get('is_common_password'):
        suggestions.append("Choose a more unique password")
    
    if analysis.get('hibp_check', {}).get('pwned'):
        suggestions.append("This password has been breached - DO NOT USE!")
    
    # General advice
    if not suggestions or analysis.get('score', 0) > 70:
        suggestions.append("Consider using a password manager")
        suggestions.append("Use different passwords for different accounts")
    
    return suggestions[:10]  # Limit to 10 suggestions

def validate_email(email: str) -> bool:
    """
    Basic email validation
    
    Args:
        email: Email address to validate
    
    Returns:
        True if email is valid
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email)) if email else False

class PerformanceTimer:
    """Simple performance timer"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def start(self):
        """Start timer"""
        self.start_time = datetime.now()
        return self
    
    def stop(self):
        """Stop timer"""
        self.end_time = datetime.now()
        return self
    
    def elapsed(self) -> float:
        """Get elapsed time in seconds"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        elif self.start_time:
            return (datetime.now() - self.start_time).total_seconds()
        return 0.0
    
    def __enter__(self):
        return self.start()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()