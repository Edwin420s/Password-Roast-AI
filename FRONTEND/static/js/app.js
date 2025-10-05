class PasswordRoastApp {
    constructor() {
        this.currentPassword = '';
        this.currentAnalysis = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadWordlistsInfo();
    }

    bindEvents() {
        // Password input events
        const passwordInput = document.getElementById('passwordInput');
        const roastButton = document.getElementById('roastButton');
        const togglePassword = document.getElementById('togglePassword');

        passwordInput.addEventListener('input', (e) => {
            this.handlePasswordInput(e.target.value);
        });

        passwordInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.analyzePassword();
            }
        });

        roastButton.addEventListener('click', () => {
            this.analyzePassword();
        });

        if (togglePassword) {
            togglePassword.addEventListener('click', () => {
                this.togglePasswordVisibility();
            });
        }

        // Theme toggle
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                this.toggleTheme();
            });
        }

        // Copy functionality
        const copyButtons = document.querySelectorAll('.copy-btn');
        copyButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.copyToClipboard(e.target);
            });
        });
    }

    handlePasswordInput(password) {
        this.currentPassword = password;
        
        // Real-time basic validation
        const strengthIndicator = document.getElementById('realTimeStrength');
        if (strengthIndicator && password.length > 0) {
            const basicStrength = this.getBasicStrength(password);
            strengthIndicator.textContent = basicStrength;
            strengthIndicator.className = `strength-badge ${basicStrength.toLowerCase().replace('_', '-')}`;
        }
    }

    getBasicStrength(password) {
        if (password.length === 0) return 'EMPTY';
        if (password.length < 6) return 'VERY_WEAK';
        if (password.length < 8) return 'WEAK';
        if (password.length < 12) return 'FAIR';
        return 'CHECKING';
    }

    async analyzePassword() {
        if (!this.currentPassword) {
            this.showError('Please enter a password to roast! 🔥');
            return;
        }

        this.showLoading(true);

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    password: this.currentPassword,
                    analyze_patterns: true,
                    check_hibp: true
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Analysis failed');
            }

            this.currentAnalysis = data;
            this.displayResults(data);
            
            // Track analysis for analytics
            this.trackAnalysis(data);

        } catch (error) {
            console.error('Analysis error:', error);
            this.showError(`Analysis failed: ${error.message}`);
        } finally {
            this.showLoading(false);
        }
    }

    displayResults(data) {
        this.showSection('resultSection');
        
        // Update strength meter and score
        this.updateStrengthMeter(data.strength, data.score);
        
        // Display roast
        this.displayRoast(data.roast, data.singing_roast);
        
        // Display detailed analysis
        this.displayAnalysisDetails(data);
        
        // Display recommendations
        this.displayRecommendations(data.recommendations);
        
        // Display weaknesses
        this.displayWeaknesses(data);
        
        // Animate results
        this.animateResults();
    }

    updateStrengthMeter(strength, score) {
        const strengthFill = document.getElementById('strengthFill');
        const strengthValue = document.getElementById('strengthValue');
        const scoreValue = document.getElementById('scoreValue');
        const crackTime = document.getElementById('crackTime');

        if (strengthFill) {
            strengthFill.className = `strength-fill ${strength.toLowerCase().replace('_', '-')}`;
            strengthFill.style.width = `${score}%`;
        }

        if (strengthValue) {
            strengthValue.textContent = strength.replace('_', ' ');
            strengthValue.className = `strength-text ${strength.toLowerCase().replace('_', '-')}`;
        }

        if (scoreValue) {
            scoreValue.textContent = `${score}/100`;
        }

        if (crackTime && this.currentAnalysis) {
            crackTime.textContent = this.currentAnalysis.crack_time_estimate;
        }
    }

    displayRoast(roast, singingRoast) {
        const roastElement = document.getElementById('ro