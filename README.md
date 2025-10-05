# Password Roast AI

A fun and educational web application that analyzes password strength and roasts weak passwords using AI. Built with Flask backend and simple HTML frontend.

---

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [API Usage](#api-usage)
- [Password Analysis Details](#password-analysis-details)
- [Deployment](#deployment)
- [Configuration](#configuration)
- [Security Considerations](#security-considerations)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)
- [Support](#support)
- [Troubleshooting](#troubleshooting)
- [Future Enhancements](#future-enhancements)

## Features

- **Comprehensive Password Analysis**: Checks for length, character variety, entropy, dictionary words, keyboard patterns, sequential characters, and common passwords
- **Multi-language Dictionary Detection**: Supports English, Swahili, Spanish, and French word detection
- **AI-Powered Roasts**: Uses OpenAI GPT-3.5-turbo to generate humorous but helpful password critiques
- **Real-time Feedback**: Instant analysis and scoring (0-100 scale)
- **Educational Suggestions**: Provides actionable advice for improving password strength
- **CORS Enabled**: Supports cross-origin requests for API integration

## Technologies Used

- **Backend**: Python Flask
- **AI Integration**: OpenAI API
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Password Analysis**: Custom algorithms for entropy calculation, pattern detection, and fuzzy matching
- **Deployment**: Ready for Heroku/Gunicorn deployment

## Project Structure

```
Password-Roast-AI/
├── BACKEND/
│   ├── app.py                 # Main Flask application and API endpoints
│   ├── password_analyzer.py   # Password analysis logic
│   ├── ai_roast_generator.py  # AI roast generation using OpenAI
│   ├── utils/                 # Helper and security utility modules
│   └── wordlists/             # Multi-language wordlists for dictionary detection
├── FRONTEND/
│   ├── templates/
│   │   ├── landing.html       # Landing page
│   │   ├── demo.html          # Demo page with password input and results
│   │   └── dashboard.html     # Dashboard page
│   ├── static/
│   │   └── js/
│   │       └── app.js         # Frontend JavaScript logic
│   └── static/images/         # Images used in frontend
├── data/
│   └── common_passwords.txt   # Common leaked passwords list
├── docs/
│   └── API.md                 # API documentation
├── tests/
│   ├── test_analyzer.py       # Unit tests for password analyzer
│   └── test_api.py            # API endpoint tests
├── Dockerfile                 # Docker image build instructions
├── docker-compose.yml         # Docker Compose configuration
├── deploy.sh                  # Deployment script using Docker
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── .env                       # Environment variables (not committed)
```

## Installation

### Prerequisites

- Python 3.8 or higher
- OpenAI API key (get one from [OpenAI Platform](https://platform.openai.com/))

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Edwin420s/Password-Roast-AI.git
   cd Password-Roast-AI
   ```

2. **Create virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the root directory:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Usage

### Running the Application

1. **Start the Flask server**:
   ```bash
   python BACKEND/app.py
   ```

2. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

3. **Enter a password** in the input field and click "Roast My Password!"

### API Usage

The application provides a REST API for programmatic access:

#### Analyze Password
**Endpoint**: `POST /api/analyze`

**Request Body**:
```json
{
  "password": "yourpasswordhere"
}
```

**Response**:
```json
{
  "password": "yourpasswordhere",
  "length": 14,
  "character_classes": {
    "upper": true,
    "lower": true,
    "digit": true,
    "special": true
  },
  "entropy": 78.45,
  "dictionary_matches": [],
  "patterns_detected": [],
  "is_common_password": false,
  "hibp_check": {
    "pwned": false,
    "count": 0
  },
  "score": 85,
  "strength": "STRONG",
  "suggestions": [],
  "roast": "🔥 Wow, this password is stronger than my coffee! Keep up the good work! 💪",
  "singing_roast": "🎵 Your password's so strong, it sings like a rockstar! 🎵",
  "recommendations": []
}
```

**Example using curl**:
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"password": "password123"}'
```

#### Health Check
**Endpoint**: `GET /api/health`

**Response**:
```json
{
  "status": "healthy",
  "service": "Password Roast AI",
  "version": "2.0.0"
}
```

## Password Analysis Details

### Strength Scoring
- **0-39**: WEAK
- **40-69**: FAIR
- **70-100**: STRONG

### Analysis Components

1. **Basic Checks**:
   - Length (minimum 8 characters recommended)
   - Character variety (uppercase, lowercase, digits, special characters)

2. **Advanced Analysis**:
   - Shannon entropy calculation
   - Dictionary word detection (exact and fuzzy matching)
   - Keyboard pattern detection (qwerty, asdf, etc.)
   - Sequential character detection (1234, abcd, etc.)
   - Common password checking

3. **Multi-language Support**:
   - English
   - Swahili
   - Spanish
   - French

### AI Roast Generation

The AI roast feature uses GPT-3.5-turbo to create humorous critiques that are:
- Educational: Explain why the password is weak
- Actionable: Suggest specific improvements
- Entertaining: Use emojis and fun language

## Deployment

### Local Development
```bash
python BACKEND/app.py
```

### Production (Heroku Example)

1. **Install Gunicorn**:
   ```bash
   pip install gunicorn
   ```

2. **Create Procfile**:
   ```
   web: gunicorn BACKEND.app:app
   ```

3. **Deploy to Heroku**:
   ```bash
   heroku create your-app-name
   heroku config:set OPENAI_API_KEY=your_key_here
   git push heroku main
   ```

### Docker Deployment

Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "BACKEND/app.py"]
```

Build and run:
```bash
docker build -t password-roast-ai .
docker run -p 5000:5000 password-roast-ai
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required for AI roasts)

### Flask Configuration

The app runs with the following default settings:
- Host: 0.0.0.0
- Port: 5000
- Debug: True (development only)

## Security Considerations

- **API Key Protection**: Never commit API keys to version control
- **HTTPS**: Use HTTPS in production
- **Rate Limiting**: Consider implementing rate limiting for API endpoints
- **Input Validation**: Passwords are analyzed but not stored
- **CORS**: Configured for cross-origin requests (adjust as needed)

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Commit your changes: `git commit -am 'Add new feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation for API changes
- Ensure backward compatibility

## Testing

Run the application and test with various password types:
- Weak passwords (short, common words)
- Strong passwords (long, complex)
- Edge cases (empty, special characters, unicode)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for providing the GPT API
- Flask community for the excellent web framework
- Security researchers for password analysis techniques

## Support

If you encounter issues or have questions:
1. Check the troubleshooting section below
2. Open an issue on GitHub
3. Contact the maintainers

## Troubleshooting

### Common Issues

1. **OpenAI API Key Error**:
   - Ensure your `.env` file contains a valid `OPENAI_API_KEY`
   - Check your OpenAI account has sufficient credits

2. **Template Not Found**:
   - Ensure the FRONTEND/templates/ directory exists
   - Check file paths in app.py

3. **Port Already in Use**:
   - Change the port in `app.run(port=5001)`

4. **Import Errors**:
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version compatibility

### Debug Mode

Run with debug logging:
```bash
export FLASK_DEBUG=1
python BACKEND/app.py
```

## Future Enhancements

- [ ] User authentication and password history
- [ ] Batch password analysis
- [ ] Password generator with strength guarantees
- [ ] Mobile app version
- [ ] Integration with password managers
- [ ] Advanced AI models for better roasts
- [ ] Multi-language support for roasts

---

**Disclaimer**: This tool is for educational purposes. Always use strong, unique passwords and consider using a password manager. Never share real passwords with this application.
