import pytest
import json
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'BACKEND'))

from BACKEND.app import app

@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

class TestPasswordRoastAPI:
    """Test cases for Password Roast API"""
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get('/api/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'service' in data
        assert 'version' in data
    
    def test_analyze_endpoint_valid_password(self, client):
        """Test analyze endpoint with valid password"""
        response = client.post('/api/analyze', 
                             json={'password': 'test123'})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Check required fields
        assert 'score' in data
        assert 'strength' in data
        assert 'suggestions' in data
        assert 'roast' in data
        assert 'length' in data
        assert 'entropy' in data
        
        # Check data types
        assert isinstance(data['score'], (int, float))
        assert isinstance(data['strength'], str)
        assert isinstance(data['suggestions'], list)
        assert isinstance(data['roast'], str)
    
    def test_analyze_endpoint_empty_password(self, client):
        """Test analyze endpoint with empty password"""
        response = client.post('/api/analyze', 
                             json={'password': ''})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_analyze_endpoint_missing_password(self, client):
        """Test analyze endpoint with missing password"""
        response = client.post('/api/analyze', 
                             json={})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_analyze_endpoint_weak_password(self, client):
        """Test analyze endpoint with weak password"""
        response = client.post('/api/analyze', 
                             json={'password': '123456'})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['strength'] in ['WEAK', 'VERY_WEAK']
        assert data['score'] < 40
        assert len(data['suggestions']) > 0
        assert data['is_common_password'] == True
    
    def test_analyze_endpoint_strong_password(self, client):
        """Test analyze endpoint with strong password"""
        response = client.post('/api/analyze', 
                             json={'password': 'Xq8!kL2$pW9*mN5&'})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['strength'] in ['STRONG', 'VERY_STRONG']
        assert data['score'] > 70
        assert data['length'] >= 12
    
    def test_analyze_endpoint_special_characters(self, client):
        """Test analyze endpoint with special characters"""
        response = client.post('/api/analyze',
                             json={'password': 'P@ssw0rd!2024'})

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['character_classes']['special'] == True
        assert data['score'] > 40
    
    def test_analyze_endpoint_dictionary_words(self, client):
        """Test analyze endpoint with dictionary words"""
        response = client.post('/api/analyze', 
                             json={'password': 'welcomepassword'})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert len(data['dictionary_matches']) > 0
        assert any(match['language'] == 'english' for match in data['dictionary_matches'])
    
    def test_analyze_endpoint_multi_language(self, client):
        """Test analyze endpoint with multi-language words"""
        response = client.post('/api/analyze', 
                             json={'password': 'jambohola'})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Should detect words from multiple languages
        languages = set(match['language'] for match in data['dictionary_matches'])
        assert len(languages) >= 2
    
    def test_analyze_endpoint_leet_speak(self, client):
        """Test analyze endpoint with leetspeak"""
        response = client.post('/api/analyze', 
                             json={'password': 'p@ssw0rd'})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Should detect dictionary words through leetspeak
        assert len(data['dictionary_matches']) > 0
    
    def test_analyze_endpoint_very_long_password(self, client):
        """Test analyze endpoint with very long password"""
        long_password = 'A' * 100 + '1'
        response = client.post('/api/analyze', 
                             json={'password': long_password})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['length'] == 101
        # Should handle long passwords without crashing
    
    def test_analyze_endpoint_invalid_json(self, client):
        """Test analyze endpoint with invalid JSON"""
        response = client.post('/api/analyze', 
                             data='invalid json',
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_static_files_serving(self, client):
        """Test static files are served correctly"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Password Roast AI' in response.data
    
    def test_nonexistent_endpoint(self, client):
        """Test non-existent endpoint returns 404"""
        response = client.get('/api/nonexistent')
        assert response.status_code == 404

if __name__ == '__main__':
    pytest.main([__file__, '-v'])