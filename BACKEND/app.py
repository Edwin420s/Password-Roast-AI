from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import unicodedata
import re
import math
from collections import Counter
from difflib import SequenceMatcher
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder='../FRONTEND/templates')
CORS(app)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# --- Expanded wordlists for multiple languages ---
WORDLISTS = {
    'english': {
        'password', 'admin', 'welcome', 'hello', 'qwerty', 'secret', 'letmein', 
        'monkey', 'dragon', 'master', 'login', 'welcome123', 'sunshine', 'princess',
        'football', 'baseball', 'mustang', 'superman', 'batman', 'trustno1'
    },
    'swahili': {
        'habari', 'safari', 'mambo', 'jambo', 'rafiki', 'hakuna', 'matata',
        'asante', 'karibu', 'pole', 'chakula', 'maji', 'mtoto', 'shule'
    },
    'spanish': {
        'hola', 'adios', 'gracias', 'porfavor', 'amigo', 'casa', 'agua',
        'familia', 'trabajo', 'escuela', 'buenos', 'noches'
    },
    'french': {
        'bonjour', 'au revoir', 'merci', 's il vous plait', 'ami', 'maison',
        'eau', 'famille', 'travail', 'ecole'
    }
}

# Common leaked passwords
COMMON_PASSWORDS = {
    '123456', 'password', '12345678', 'qwerty', 'abc123', 'password1',
    '12345', '123456789', 'letmein', 'welcome', 'monkey', 'dragon'
}

# Leet speak mappings
LEET_MAP = {
    '4': 'a', '@': 'a', '8': 'b', '3': 'e', '1': 'l', '0': 'o', 
    '$': 's', '5': 's', '7': 't', '2': 'z', '!': 'i', '+': 't'
}

# --------------- Utility Functions ---------------
def normalize(text: str) -> str:
    """Normalize unicode and convert to lowercase"""
    text = unicodedata.normalize('NFKC', text)
    text = text.lower()
    return text

def transliterate_basic(text: str) -> str:
    """Basic accent removal"""
    return ''.join(
        c for c in unicodedata.normalize('NFKD', text) 
        if unicodedata.category(c) != 'Mn'
    )

def reverse_leet(text: str):
    """Convert leetspeak to normal text"""
    return ''.join(LEET_MAP.get(ch, ch) for ch in text)

def calculate_entropy(password: str) -> float:
    """Calculate Shannon entropy of password"""
    if len(password) <= 1:
        return 0
    freq = Counter(password)
    entropy = 0.0
    for count in freq.values():
        p = count / len(password)
        entropy -= p * math.log2(p)
    return entropy * len(password)

def is_keyboard_pattern(text: str) -> bool:
    """Detect keyboard patterns like qwerty, asdf, etc."""
    patterns = [
        'qwerty', 'asdfgh', 'zxcvbn', '123456', 'abcdef',
        'yxcvbn', 'poiuyt', 'lkjhgf', 'mnbvcx'
    ]
    text_lower = text.lower()
    return any(pattern in text_lower for pattern in patterns)

def has_sequential_chars(text: str, min_seq: int = 4) -> bool:
    """Check for sequential characters"""
    if len(text) < min_seq:
        return False
    
    for i in range(len(text) - min_seq + 1):
        segment = text[i:i+min_seq]
        # Check if all differences are 1 (ascending) or -1 (descending)
        diffs = [ord(segment[j+1]) - ord(segment[j]) for j in range(min_seq-1)]
        if all(diff == 1 for diff in diffs) or all(diff == -1 for diff in diffs):
            return True
    return False

def fuzzy_match(word1, word2, threshold=0.8):
    """Check if two words are similar using ratio"""
    return SequenceMatcher(None, word1, word2).ratio() >= threshold

# --------------- Detection Engine ---------------
def find_dictionary_matches(password: str, min_length: int = 3):
    """Find dictionary words in password across all languages"""
    matches = []
    
    # Test different transformations
    test_variants = [
        password,  # original
        reverse_leet(password),  # de-obfuscated
    ]
    
    for variant in test_variants:
        variant_lower = variant.lower()
        n = len(variant_lower)
        
        # Check all substrings
        for start in range(n):
            for end in range(start + min_length, n + 1):
                substring = variant_lower[start:end]
                
                # Exact matches
                for lang, words in WORDLISTS.items():
                    if substring in words:
                        matches.append({
                            'language': lang,
                            'word': substring,
                            'start': start,
                            'end': end,
                            'type': 'exact',
                            'variant': variant
                        })
                
                # Fuzzy matches
                for lang, words in WORDLISTS.items():
                    for dict_word in words:
                        if abs(len(dict_word) - len(substring)) <= 2:
                            if fuzzy_match(dict_word, substring):
                                matches.append({
                                    'language': lang,
                                    'word': substring,
                                    'dict_word': dict_word,
                                    'start': start,
                                    'end': end,
                                    'type': 'fuzzy',
                                    'variant': variant
                                })
                                break
    
    return matches

def analyze_password_strength(password: str):
    """Comprehensive password analysis"""
    if not password:
        return None
    
    # Basic analysis
    length = len(password)
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    
    # Advanced analysis
    entropy = calculate_entropy(password)
    dictionary_matches = find_dictionary_matches(password)
    keyboard_pattern = is_keyboard_pattern(password)
    sequential_chars = has_sequential_chars(password)
    is_common = password.lower() in COMMON_PASSWORDS
    
    # Calculate score (0-100)
    base_score = 0
    
    # Length bonus
    base_score += min(length * 4, 40)  # max 40 for length
    
    # Character variety bonus
    char_types = sum([has_upper, has_lower, has_digit, has_special])
    base_score += char_types * 10  # max 40 for variety
    
    # Entropy bonus
    base_score += min(entropy * 2, 20)  # max 20 for entropy
    
    # Penalties
    penalties = 0
    if dictionary_matches:
        penalties += len(dictionary_matches) * 15
    if keyboard_pattern:
        penalties += 25
    if sequential_chars:
        penalties += 20
    if is_common:
        penalties += 30
    
    final_score = max(0, base_score - penalties)
    
    # Determine strength level
    if final_score >= 70:
        strength = "STRONG"
    elif final_score >= 40:
        strength = "FAIR"
    else:
        strength = "WEAK"
    
    # Generate suggestions
    suggestions = []
    if length < 8:
        suggestions.append("Use at least 8 characters")
    if not has_upper:
        suggestions.append("Add uppercase letters")
    if not has_lower:
        suggestions.append("Add lowercase letters")
    if not has_digit:
        suggestions.append("Add numbers")
    if not has_special:
        suggestions.append("Add special characters (!@#$%)")
    if dictionary_matches:
        suggestions.append("Avoid dictionary words")
    if keyboard_pattern:
        suggestions.append("Avoid keyboard patterns")
    
    return {
        'password': password,
        'length': length,
        'has_upper': has_upper,
        'has_lower': has_lower,
        'has_digit': has_digit,
        'has_special': has_special,
        'entropy': round(entropy, 2),
        'dictionary_matches': dictionary_matches,
        'keyboard_pattern': keyboard_pattern,
        'sequential_chars': sequential_chars,
        'is_common_password': is_common,
        'score': round(final_score),
        'strength': strength,
        'suggestions': suggestions
    }

# --------------- AI Roast Generator ---------------
def generate_password_roast(analysis_result):
    """Generate funny roast using OpenAI"""
    if not client.api_key:
        return "API key not configured - using default roast"
    
    try:
        weaknesses = []
        if analysis_result['length'] < 8:
            weaknesses.append("shorter than a toddler's attention span")
        if analysis_result['dictionary_matches']:
            weaknesses.append("uses dictionary words that even my grandma could guess")
        if analysis_result['keyboard_pattern']:
            weaknesses.append("follows keyboard patterns like a mindless robot")
        if analysis_result['is_common_password']:
            weaknesses.append("is more common than bad coffee in office meetings")
        if analysis_result['sequential_chars']:
            weaknesses.append("has sequential characters that scream 'lazy'")
        
        weakness_text = " and ".join(weaknesses) if weaknesses else "barely exists"
        
        prompt = f"""
        Roast this weak password in a funny, educational way. 
        Password: {analysis_result['password']}
        Weaknesses: {weakness_text}
        Strength: {analysis_result['strength']}
        
        Make it humorous but helpful - explain why it's weak and what to improve.
        Keep it under 2 sentences and add emojis.
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a sassy but helpful cybersecurity expert who roasts weak passwords in a funny way."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        return f"🔥 Yikes! Your password is so weak even our AI roast failed! But seriously: {analysis_result['suggestions'][0] if analysis_result['suggestions'] else 'Try something stronger!'} 😄"

# --------------- Routes ---------------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        password = data.get('password', '')
        
        if not password:
            return jsonify({'error': 'No password provided'}), 400
        
        # Analyze password
        analysis = analyze_password_strength(password)
        
        # Generate AI roast
        roast = generate_password_roast(analysis)
        analysis['roast'] = roast
        
        return jsonify(analysis)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)