import pytest
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'BACKEND'))

from password_analyzer import AdvancedPasswordAnalyzer

class TestPasswordAnalyzer:
    """Test cases for AdvancedPasswordAnalyzer"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.analyzer = AdvancedPasswordAnalyzer()
    
    def test_weak_password_detection(self):
        """Test detection of weak passwords"""
        result = self.analyzer.comprehensive_analysis("password123")
        
        assert result['strength'] in ['WEAK', 'VERY_WEAK']
        assert result['score'] < 40
        assert len(result['dictionary_matches']) > 0
        assert len(result['suggestions']) > 0
    
    def test_strong_password(self):
        """Test recognition of strong passwords"""
        result = self.analyzer.comprehensive_analysis("Xq8!kL2$pW9*mN5&")
        
        assert result['strength'] in ['STRONG', 'VERY_STRONG']
        assert result['score'] > 70
        assert result['length'] >= 12
    
    def test_empty_password(self):
        """Test handling of empty password"""
        result = self.analyzer.comprehensive_analysis("")
        
        assert result['score'] == 0
        assert result['strength'] == 'VERY_WEAK'
        assert result['length'] == 0
    
    def test_none_password(self):
        """Test handling of None password"""
        result = self.analyzer.comprehensive_analysis(None)
        
        assert result['score'] == 0
        assert result['strength'] == 'VERY_WEAK'
    
    def test_dictionary_word_detection(self):
        """Test detection of dictionary words"""
        result = self.analyzer.comprehensive_analysis("welcome2024")
        
        assert len(result['dictionary_matches']) > 0
        assert any(match['language'] == 'english' for match in result['dictionary_matches'])
    
    def test_leet_speak_detection(self):
        """Test detection of leetspeak words"""
        result = self.analyzer.comprehensive_analysis("p@ssw0rd")
        
        assert len(result['dictionary_matches']) > 0
        # Should detect "password" through leetspeak reversal
    
    def test_keyboard_pattern_detection(self):
        """Test detection of keyboard patterns"""
        result = self.analyzer.comprehensive_analysis("qwertyuiop")
        
        assert len(result['patterns_detected']) > 0
        assert any('keyboard_pattern' in pattern['type'] for pattern in result['patterns_detected'])
    
    def test_sequential_chars_detection(self):
        """Test detection of sequential characters"""
        result = self.analyzer.comprehensive_analysis("abcd1234")
        
        assert len(result['patterns_detected']) > 0
        assert any('sequential' in pattern['type'] for pattern in result['patterns_detected'])
    
    def test_common_password_detection(self):
        """Test detection of common passwords"""
        result = self.analyzer.comprehensive_analysis("123456")
        
        assert result['is_common_password'] == True
        assert result['score'] < 30
    
    def test_multi_language_detection(self):
        """Test detection of words in multiple languages"""
        # Test Swahili word
        result_swahili = self.analyzer.comprehensive_analysis("jambo2024")
        swahili_matches = [m for m in result_swahili['dictionary_matches'] if m['language'] == 'swahili']
        assert len(swahili_matches) > 0
        
        # Test Spanish word  
        result_spanish = self.analyzer.comprehensive_analysis("hola123")
        spanish_matches = [m for m in result_spanish['dictionary_matches'] if m['language'] == 'spanish']
        assert len(spanish_matches) > 0
    
    def test_character_class_detection(self):
        """Test detection of character classes"""
        result = self.analyzer.comprehensive_analysis("Password123!")
        
        classes = result['character_classes']
        assert classes['upper'] == True
        assert classes['lower'] == True  
        assert classes['digit'] == True
        assert classes['special'] == True
    
    def test_entropy_calculation(self):
        """Test entropy calculation"""
        # Low entropy password
        result_low = self.analyzer.comprehensive_analysis("aaaa")
        assert result_low['entropy'] < 10
        
        # High entropy password
        result_high = self.analyzer.comprehensive_analysis("Xq8!kL2$pW9*mN5&")
        assert result_high['entropy'] > 40
    
    def test_crack_time_estimation(self):
        """Test crack time estimation"""
        # Weak password
        result_weak = self.analyzer.comprehensive_analysis("123456")
        assert "Instantly" in result_weak['crack_time_estimate'] or "Seconds" in result_weak['crack_time_estimate']
        
        # Strong password
        result_strong = self.analyzer.comprehensive_analysis("Xq8!kL2$pW9*mN5&Vr3#pL0@")
        assert "Years" in result_strong['crack_time_estimate'] or "Centuries" in result_strong['crack_time_estimate']
    
    def test_special_characters(self):
        """Test handling of special characters"""
        result = self.analyzer.comprehensive_analysis("P@ssw0rd!2024")

        assert result['character_classes']['special'] == True
        assert result['score'] > 40
    
    def test_long_password(self):
        """Test handling of very long passwords"""
        long_password = "A" * 100
        result = self.analyzer.comprehensive_analysis(long_password)
        
        assert result['length'] == 100
        # Should penalize for lack of diversity despite length
        assert result['score'] < 80

if __name__ == '__main__':
    pytest.main([__file__, '-v'])