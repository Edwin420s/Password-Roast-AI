from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from password_analyzer import AdvancedPasswordAnalyzer
from ai_roast_generator import AIRoastGenerator
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(__file__), '..', 'FRONTEND', 'templates'),
            static_folder=os.path.join(os.path.dirname(__file__), '..', 'FRONTEND', 'static'))

CORS(app)

# Initialize components
analyzer = AdvancedPasswordAnalyzer()
roast_generator = AIRoastGenerator()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_password():
    try:
        data = request.get_json()
        password = data.get('password', '').strip()
        
        if not password:
            return jsonify({
                'error': 'No password provided',
                'score': 0,
                'strength': 'VERY_WEAK',
                'suggestions': ['Please enter a password to analyze']
            }), 400
        
        # Perform comprehensive analysis
        analysis = analyzer.comprehensive_analysis(password)
        
        # Generate AI roast
        analysis['roast'] = roast_generator.generate_ai_roast(analysis)
        
        # Add singing roast for fun
        analysis['singing_roast'] = roast_generator.generate_singing_roast(analysis)
        
        # Add security recommendations
        analysis['recommendations'] = generate_security_recommendations(analysis)
        
        return jsonify(analysis)
        
    except Exception as e:
        return jsonify({
            'error': f'Analysis failed: {str(e)}',
            'score': 0,
            'strength': 'VERY_WEAK',
            'suggestions': ['Please try a different password']
        }), 500

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Password Roast AI',
        'version': '2.0.0'
    })

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

def generate_security_recommendations(analysis: dict) -> list:
    """Generate security recommendations based on analysis"""
    recommendations = []
    
    if analysis['score'] < 60:
        recommendations.append({
            'priority': 'high',
            'title': 'Change This Password Immediately',
            'description': 'This password is not secure enough for important accounts',
            'action': 'Generate a new, stronger password'
        })
    
    if analysis['hibp_check']['pwned']:
        recommendations.append({
            'priority': 'critical',
            'title': 'DATA BREACH ALERT',
            'description': f"This password appeared in {analysis['hibp_check']['count']} known data breaches",
            'action': 'DO NOT USE this password anywhere. Change it immediately on all accounts.'
        })
    
    if analysis['is_common_password']:
        recommendations.append({
            'priority': 'high',
            'title': 'Extremely Common Password',
            'description': 'This is one of the most commonly used passwords worldwide',
            'action': 'Choose a more unique password that hackers won\'t guess easily'
        })
    
    if len(analysis['dictionary_matches']) > 0:
        recommendations.append({
            'priority': 'medium',
            'title': 'Dictionary Words Detected',
            'description': 'Password contains words that are easy for attackers to guess',
            'action': 'Use random words or replace letters with special characters'
        })
    
    # Always recommend password manager for strong passwords
    if analysis['score'] >= 60:
        recommendations.append({
            'priority': 'low',
            'title': 'Consider Using a Password Manager',
            'description': 'Strong passwords are hard to remember - let a manager do the work',
            'action': 'Try Bitwarden, 1Password, or LastPass'
        })
    
    return recommendations

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True
    )