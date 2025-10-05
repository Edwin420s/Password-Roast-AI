import os
import random
from typing import Dict, List
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class AIRoastGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.fallback_roasts = self._load_fallback_roasts()
    
    def _load_fallback_roasts(self) -> Dict[str, List[str]]:
        """Load fallback roasts for when AI is unavailable"""
        return {
            'VERY_WEAK': [
                "🔥 Yikes! This password is weaker than a wet paper towel! Even my grandma's cat could guess this!",
                "💀 Bruh... did you just mash your forehead on the keyboard? This is BAD!",
                "🚨 ALERT! This password screams 'HACK ME PLEASE!' to every bot on the internet!",
                "😂 This password is so weak, it probably uses 'password' as its password!",
                "📉 My disappointment is immeasurable, and my day is ruined. Please try again!"
            ],
            'WEAK': [
                "😬 Oof! This password is trying its best, but it's still snack food for hackers!",
                "🤔 Interesting choice... if 'interesting' means 'easily guessable by a potato!'",
                "🎯 Hackers love passwords like this - they're low-hanging fruit!",
                "💤 This password is putting me to sleep... and probably hackers too (from boredom!)",
                "📝 Pro tip: Maybe don't use words that actually exist in any language?"
            ],
            'FAIR': [
                "🤨 Not terrible, but not great either. It's like bringing a spoon to a knife fight!",
                "🎪 This password is walking the tightrope between 'meh' and 'okay I guess'!",
                "⚖️ On one hand: some good elements. On the other: room for SO much improvement!",
                "🏗️ There's a foundation here... now let's build a skyscraper, not a shed!",
                "📊 Statistically speaking: better than 'password123', worse than 'actually secure'!"
            ],
            'STRONG': [
                "👍 Okay, okay! This password has some swagger! Hackers will need to work for this one!",
                "🛡️ Now we're talking! This password could probably defend a small castle!",
                "💪 Look at you, being all secure and stuff! I'm genuinely impressed!",
                "🎯 Bullseye! This password hits the sweet spot between memorable and secure!",
                "🌟 Shining brighter than a hacker's tears! This is quality password craftsmanship!"
            ],
            'VERY_STRONG': [
                "🎉 HOLY MOLY! This password is Fort Knox-level secure! Are you a cybersecurity wizard?!",
                "🏆 Trophy unlocked: 'Uncrackable Beast'! Hackers everywhere are crying!",
                "🚀 To infinity and beyond! This password could probably secure NASA's systems!",
                "💎 Diamond hands! This password is precious and virtually unbreakable!",
                "👑 All hail the Password King/Queen! This is absolute perfection! 🎊"
            ]
        }
    
    def generate_ai_roast(self, analysis_result: Dict) -> str:
        """Generate AI-powered roast using OpenAI"""
        if not self.client.api_key:
            return self._get_fallback_roast(analysis_result['strength'])
        
        try:
            prompt = self._build_roast_prompt(analysis_result)
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": """You are a sassy, funny, but helpful cybersecurity expert. 
                        Your job is to roast weak passwords in an entertaining way while educating users.
                        Keep roasts under 2 sentences, use emojis, and be creative with analogies.
                        Mix humor with actual security advice."""
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=150,
                temperature=0.9
            )
            
            roast = response.choices[0].message.content.strip()
            return roast if roast else self._get_fallback_roast(analysis_result['strength'])
            
        except Exception as e:
            print(f"AI roast generation failed: {e}")
            return self._get_fallback_roast(analysis_result['strength'])
    
    def _build_roast_prompt(self, analysis: Dict) -> str:
        """Build detailed prompt for AI roasting"""
        weaknesses = self._extract_weaknesses(analysis)
        strengths = self._extract_strengths(analysis)
        
        prompt = f"""
        Password: {analysis['password']}
        Strength: {analysis['strength']}
        Score: {analysis['score']}/100
        
        Weaknesses found:
        {weaknesses}
        
        Strengths:
        {strengths}
        
        Crack time: {analysis['crack_time_estimate']}
        
        Generate a funny, sassy roast (1-2 sentences) that:
        1. Roasts the specific weaknesses
        2. Acknowledges any strengths
        3. Provides quick security advice
        4. Uses emojis and humor
        5. Is memorable and shareable
        
        Make it creative and specific to this password's issues!
        """
        
        return prompt
    
    def _extract_weaknesses(self, analysis: Dict) -> str:
        """Extract weaknesses for the prompt"""
        weaknesses = []
        
        if analysis['length'] < 8:
            weaknesses.append(f"Too short ({analysis['length']} characters)")
        elif analysis['length'] < 12:
            weaknesses.append(f"Could be longer ({analysis['length']} characters)")
        
        if analysis['dictionary_matches']:
            weak_words = [match['matched_word'] for match in analysis['dictionary_matches'][:3]]
            weaknesses.append(f"Dictionary words: {', '.join(weak_words)}")
        
        for pattern in analysis['patterns_detected']:
            if pattern['type'] == 'keyboard_pattern':
                weaknesses.append("Keyboard pattern detected")
            elif pattern['type'] == 'sequential_chars':
                weaknesses.append("Sequential characters")
            elif pattern['type'] == 'repeated_chars':
                weaknesses.append("Repeated characters")
        
        if analysis['is_common_password']:
            weaknesses.append("Very common password")
        
        if analysis['hibp_check']['pwned']:
            weaknesses.append(f"Exposed in {analysis['hibp_check']['count']} breaches")
        
        # Character class weaknesses
        classes = analysis['character_classes']
        if not classes['upper']:
            weaknesses.append("No uppercase letters")
        if not classes['lower']:
            weaknesses.append("No lowercase letters")
        if not classes['digit']:
            weaknesses.append("No numbers")
        if not classes['special']:
            weaknesses.append("No special characters")
        
        return "\n".join(f"- {w}" for w in weaknesses) if weaknesses else "No major weaknesses found!"
    
    def _extract_strengths(self, analysis: Dict) -> str:
        """Extract strengths for the prompt"""
        strengths = []
        
        if analysis['length'] >= 16:
            strengths.append("Excellent length")
        elif analysis['length'] >= 12:
            strengths.append("Good length")
        
        if analysis['entropy'] >= 60:
            strengths.append("High entropy")
        elif analysis['entropy'] >= 40:
            strengths.append("Good entropy")
        
        # Character class strengths
        classes = analysis['character_classes']
        class_count = sum(classes.values())
        if class_count == 4:
            strengths.append("All character types used")
        elif class_count == 3:
            strengths.append("Good character variety")
        
        if not analysis['dictionary_matches']:
            strengths.append("No dictionary words")
        
        if not analysis['patterns_detected']:
            strengths.append("No obvious patterns")
        
        if not analysis['is_common_password']:
            strengths.append("Not a common password")
        
        return "\n".join(f"- {s}" for s in strengths) if strengths else "Basic password structure"
    
    def _get_fallback_roast(self, strength: str) -> str:
        """Get random fallback roast for strength level"""
        roasts = self.fallback_roasts.get(strength, self.fallback_roasts['WEAK'])
        return random.choice(roasts)
    
    def generate_singing_roast(self, analysis_result: Dict) -> str:
        """Generate a roast in song/rap format"""
        try:
            prompt = f"""
            Turn this password analysis into a short, funny song or rap (4-8 lines):
            
            Password: {analysis_result['password']}
            Strength: {analysis_result['strength']}
            Key issues: {', '.join([suggestion for suggestion in analysis_result['suggestions'][:3]])}
            
            Make it rhythmic, add some emojis, and keep it educational but hilarious!
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You create funny, educational songs/raps about password security. Use simple rhythms, emojis, and cybersecurity themes."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=200,
                temperature=0.95
            )
            
            song = response.choices[0].message.content.strip()
            return song if song else "🎵 Couldn't compose a tune, but your password needs work! 🎵"
            
        except Exception:
            return "🎤 *Ahem* Your password's so weak... it made the mic drop! 🎤"