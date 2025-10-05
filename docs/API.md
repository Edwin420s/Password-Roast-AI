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