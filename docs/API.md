# Password Roast AI - API Documentation

## Overview
Password Roast AI is a Flask-based API that analyzes password strength and generates humorous, educational roasts for weak passwords.

## Base URL
http://localhost:5000


## Endpoints

### Health Check
- **URL**: `/api/health`
- **Method**: `GET`
- **Description**: Check API health status
- **Response**:
```json
{
  "status": "healthy",
  "service": "Password Roast AI",
  "version": "2.0.0"
}
```

###Password Analysis
```
URL: /api/analyze
```
Method: POST

##Description: Analyze password strength and generate roast

Request Body:

```
{
  "password": "your_password_here"
}
```

```
{
  "password": "password123",
  "length": 11,
  "character_classes": {
    "upper": false,
    "lower": true,
    "digit": true,
    "special": false
  },
  "entropy": 25.6,
  "dictionary_matches": [
    {
      "language": "english",
      "matched_word": "password",
      "variant": "password123",
      "type": "exact",
      "position": 0
    }
  ],
  "patterns_detected": [
    {
      "type": "common_base",
      "base_word": "password",
      "severity": "high"
    }
  ],
  "hibp_check": {
    "pwned": true,
    "count": 4528673
  },
  "is_common_password": true,
  "score": 18,
  "strength": "VERY_WEAK",
  "suggestions": [
    "Use at least 8 characters",
    "Add uppercase letters",
    "Avoid dictionary words from any language"
  ],
  "crack_time_estimate": "Instantly",
  "roast": "🔥 Yikes! This password is weaker than a wet paper towel!",
  "singing_roast": "🎵 Your password's so weak, it makes hackers weep! 🎵",
  "recommendations": [
    {
      "priority": "critical",
      "title": "DATA BREACH ALERT",
      "description": "This password appeared in 4528673 known data breaches",
      "action": "DO NOT USE this password anywhere. Change it immediately on all accounts."
    }
  ]
}
```

