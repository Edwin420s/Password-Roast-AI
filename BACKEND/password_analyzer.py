import re
import math
import unicodedata
from collections import Counter
from difflib import SequenceMatcher
import os
import hashlib
import requests
from typing import Dict, List, Tuple

class AdvancedPasswordAnalyzer:
    def __init__(self):
        self.wordlists = self.load_wordlists()
        self.common_passwords = self.load_common_passwords()
        self.leet_map = self.get_leet_mappings()
        
    def load_wordlists(self) -> Dict[str, set]:
        """Load multi-language wordlists from files"""
        wordlists = {}
        wordlist_path = os.path.join(os.path.dirname(__file__), 'wordlists')
        
        for filename in os.listdir(wordlist_path):
            if filename.endswith('.txt'):
                lang = filename.replace('.txt', '')
                with open(os.path.join(wordlist_path, filename), 'r', encoding='utf-8') as f:
                    wordlists[lang] = set(line.strip().lower() for line in f if line.strip())
        
        return wordlists
    
    def load_common_passwords(self) -> set:
        """Load common leaked passwords"""
        common_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'common_passwords.txt')
        try:
            with open(common_path, 'r', encoding='utf-8') as f:
                return set(line.strip().lower() for line in f if line.strip())
        except FileNotFoundError:
            return {'123456', 'password', '12345678', 'qwerty', 'abc123'}
    
    def get_leet_mappings(self) -> Dict[str, List[str]]:
        """Extended leetspeak mappings with multiple possibilities"""
        return {
            '4': ['a'],
            '@': ['a'],
            '8': ['b'],
            '3': ['e'],
            '1': ['l', 'i'],
            '0': ['o'],
            '$': ['s'],
            '5': ['s'],
            '7': ['t'],
            '2': ['z'],
            '!': ['i'],
            '+': ['t'],
            '#': ['h'],
            '6': ['g', 'b']
        }
    
    def normalize_text(self, text: str) -> str:
        """Advanced text normalization"""
        # Unicode normalization
        text = unicodedata.normalize('NFKC', text)
        # Remove accents
        text = ''.join(c for c in unicodedata.normalize('NFKD', text) 
                      if unicodedata.category(c) != 'Mn')
        return text.lower()
    
    def generate_leet_variations(self, text: str) -> List[str]:
        """Generate multiple leetspeak deobfuscation variations"""
        variations = [text]
        
        # Simple direct replacement
        direct_replacement = ''.join(self.leet_map.get(ch, [ch])[0] for ch in text)
        variations.append(direct_replacement)
        
        # Advanced: try multiple possibilities for ambiguous characters
        if any(ch in self.leet_map and len(self.leet_map[ch]) > 1 for ch in text):
            # This could be expanded for more complex variations
            pass
            
        return list(set(variations))
    
    def calculate_advanced_entropy(self, password: str) -> float:
        """Calculate password entropy considering character classes and repetition"""
        if len(password) <= 1:
            return 0

        # Character class detection
        classes_present = {
            'lower': any(c.islower() for c in password),
            'upper': any(c.isupper() for c in password),
            'digit': any(c.isdigit() for c in password),
            'special': any(not c.isalnum() for c in password)
        }

        # Effective alphabet size based on classes used
        alphabet_size = 0
        if classes_present['lower']: alphabet_size += 26
        if classes_present['upper']: alphabet_size += 26
        if classes_present['digit']: alphabet_size += 10
        if classes_present['special']: alphabet_size += 32  # Common special chars

        if alphabet_size == 0:
            return 0

        # Base entropy
        entropy = len(password) * math.log2(alphabet_size)

        # Penalty for repetition
        char_counts = Counter(password)
        max_count = max(char_counts.values())
        repetition_ratio = max_count / len(password)
        repetition_penalty = repetition_ratio * 0.7  # Reduce entropy for repetition

        entropy *= (1 - repetition_penalty)

        return min(max(entropy, 0), 100)  # Cap at 100, min 0
    
    def find_dictionary_matches(self, password: str) -> List[Dict]:
        """Advanced dictionary matching with fuzzy search"""
        matches = []
        password_lower = password.lower()
        
        # Test multiple variations
        test_variants = [password_lower]
        test_variants.extend(self.generate_leet_variations(password_lower))
        
        for variant in test_variants:
            # Check for exact matches
            for lang, words in self.wordlists.items():
                for word in words:
                    if word in variant:
                        matches.append({
                            'language': lang,
                            'matched_word': word,
                            'variant': variant,
                            'type': 'exact',
                            'position': variant.find(word)
                        })
            
            # Check for fuzzy matches
            for lang, words in self.wordlists.items():
                for word in words:
                    if len(word) >= 4 and abs(len(word) - len(variant)) <= 3:
                        similarity = SequenceMatcher(None, word, variant).ratio()
                        if similarity >= 0.7:  # Adjust threshold as needed
                            matches.append({
                                'language': lang,
                                'matched_word': word,
                                'variant': variant,
                                'type': 'fuzzy',
                                'similarity': similarity,
                                'position': 0
                            })
        
        return matches
    
    def detect_patterns(self, password: str) -> List[Dict]:
        """Detect various password patterns"""
        patterns = []
        
        # Keyboard patterns
        keyboard_patterns = [
            'qwerty', 'asdfgh', 'zxcvbn', '123456', 'abcdef',
            'yxcvbnm', 'poiuyt', 'lkjhgf', 'mnbvcx'
        ]
        
        password_lower = password.lower()
        for pattern in keyboard_patterns:
            if pattern in password_lower:
                patterns.append({
                    'type': 'keyboard_pattern',
                    'pattern': pattern,
                    'severity': 'high'
                })
        
        # Sequential characters
        if self.has_sequential_chars(password):
            patterns.append({
                'type': 'sequential_chars',
                'severity': 'medium'
            })
        
        # Repeated characters
        if re.search(r'(.)\1{2,}', password):  # 3 or more repeated chars
            patterns.append({
                'type': 'repeated_chars',
                'severity': 'medium'
            })
        
        # Common base words with simple additions
        common_bases = ['password', 'admin', 'welcome', 'qwerty']
        for base in common_bases:
            if base in password_lower and len(password) <= len(base) + 3:
                patterns.append({
                    'type': 'common_base',
                    'base_word': base,
                    'severity': 'high'
                })
        
        return patterns
    
    def has_sequential_chars(self, text: str, min_seq: int = 4) -> bool:
        """Check for sequential characters (both directions)"""
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
    
    def check_hibp(self, password: str) -> Dict:
        """Check password against Have I Been Pwned API (privacy-safe)"""
        # SHA-1 hash of password
        sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        prefix, suffix = sha1_hash[:5], sha1_hash[5:]
        
        try:
            response = requests.get(
                f'https://api.pwnedpasswords.com/range/{prefix}',
                timeout=2
            )
            
            if response.status_code == 200:
                hashes = (line.split(':') for line in response.text.splitlines())
                for hash_suffix, count in hashes:
                    if hash_suffix == suffix:
                        return {'pwned': True, 'count': int(count)}
            
            return {'pwned': False, 'count': 0}
            
        except requests.RequestException:
            return {'pwned': False, 'count': 0, 'error': 'API unavailable'}
    
    def comprehensive_analysis(self, password: str) -> Dict:
        """Perform comprehensive password analysis"""
        if not password:
            return self._empty_analysis()
        
        # Basic metrics
        length = len(password)
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)
        
        # Advanced analysis
        entropy = self.calculate_advanced_entropy(password)
        dictionary_matches = self.find_dictionary_matches(password)
        patterns = self.detect_patterns(password)
        hibp_result = self.check_hibp(password)
        is_common = password.lower() in self.common_passwords
        
        # Calculate comprehensive score
        score = self._calculate_score(
            length, entropy, dictionary_matches, patterns, 
            has_upper, has_lower, has_digit, has_special,
            is_common, hibp_result
        )
        
        # Generate suggestions
        suggestions = self._generate_suggestions(
            length, has_upper, has_lower, has_digit, has_special,
            dictionary_matches, patterns, is_common, hibp_result
        )
        
        # Determine strength level
        strength = self._determine_strength(score)
        
        return {
            'password': password,
            'length': length,
            'character_classes': {
                'upper': has_upper,
                'lower': has_lower,
                'digit': has_digit,
                'special': has_special
            },
            'entropy': round(entropy, 2),
            'dictionary_matches': dictionary_matches,
            'patterns_detected': patterns,
            'hibp_check': hibp_result,
            'is_common_password': is_common,
            'score': round(score),
            'strength': strength,
            'suggestions': suggestions,
            'crack_time_estimate': self._estimate_crack_time(score, length)
        }
    
    def _calculate_score(self, length: int, entropy: float, dictionary_matches: List,
                        patterns: List, has_upper: bool, has_lower: bool,
                        has_digit: bool, has_special: bool, is_common: bool,
                        hibp_result: Dict) -> float:
        """Calculate comprehensive password score (0-100)"""
        base_score = 0

        # Length score (max 40)
        base_score += min(length * 2.5, 40)

        # Character variety score (max 20)
        char_types = sum([has_upper, has_lower, has_digit, has_special])
        base_score += char_types * 5

        # Entropy score (max 25)
        base_score += min(entropy / 4, 25)

        # Penalties
        penalties = 0

        # Dictionary matches penalty
        if dictionary_matches:
            penalties += len(dictionary_matches) * 10

        # Pattern penalties
        for pattern in patterns:
            if pattern['severity'] == 'high':
                penalties += 20
            else:
                penalties += 10

        # Common password penalty
        if is_common:
            penalties += 30

        # HIBP penalty
        if hibp_result.get('pwned', False):
            penalties += 25 + min(hibp_result.get('count', 0) / 1000, 20)

        final_score = max(0, base_score - penalties)
        return min(final_score, 100)
    
    def _generate_suggestions(self, length: int, has_upper: bool, has_lower: bool,
                             has_digit: bool, has_special: bool, dictionary_matches: List,
                             patterns: List, is_common: bool, hibp_result: Dict) -> List[str]:
        """Generate targeted improvement suggestions"""
        suggestions = []
        
        if length < 12:
            suggestions.append("Use at least 12 characters for better security")
        elif length < 8:
            suggestions.append("Use at least 8 characters")
        
        if not has_upper:
            suggestions.append("Include uppercase letters")
        if not has_lower:
            suggestions.append("Include lowercase letters")
        if not has_digit:
            suggestions.append("Include numbers")
        if not has_special:
            suggestions.append("Include special characters (!@#$%^&*)")
        
        if dictionary_matches:
            suggestions.append("Avoid dictionary words from any language")
        
        for pattern in patterns:
            if pattern['type'] == 'keyboard_pattern':
                suggestions.append("Avoid keyboard patterns (qwerty, 12345, etc.)")
            elif pattern['type'] == 'sequential_chars':
                suggestions.append("Avoid sequential characters (abcd, 1234, etc.)")
            elif pattern['type'] == 'repeated_chars':
                suggestions.append("Avoid repeated characters (aaa, 111, etc.)")
        
        if is_common:
            suggestions.append("This is a very common password - choose something more unique")
        
        if hibp_result.get('pwned', False):
            count = hibp_result.get('count', 0)
            suggestions.append(f"This password has been exposed in {count} data breaches - DO NOT USE!")
        
        if not suggestions:  # If password is strong
            suggestions.append("Great password! Consider using a password manager for all your accounts")
        
        return suggestions
    
    def _determine_strength(self, score: float) -> str:
        """Determine password strength category"""
        if score >= 80:
            return "VERY_STRONG"
        elif score >= 60:
            return "STRONG"
        elif score >= 40:
            return "FAIR"
        elif score >= 20:
            return "WEAK"
        else:
            return "VERY_WEAK"
    
    def _estimate_crack_time(self, score: float, length: int) -> str:
        """Estimate time to crack password"""
        if score >= 80:
            return "Centuries"
        elif score >= 60:
            return "Years"
        elif score >= 40:
            return "Months"
        elif score >= 20:
            return "Days"
        else:
            return "Instantly"
    
    def _empty_analysis(self) -> Dict:
        """Return empty analysis structure"""
        return {
            'password': '',
            'length': 0,
            'character_classes': {
                'upper': False,
                'lower': False,
                'digit': False,
                'special': False
            },
            'entropy': 0,
            'dictionary_matches': [],
            'patterns_detected': [],
            'hibp_check': {'pwned': False, 'count': 0},
            'is_common_password': False,
            'score': 0,
            'strength': 'VERY_WEAK',
            'suggestions': ['Please enter a password to analyze'],
            'crack_time_estimate': 'Instantly'
        }