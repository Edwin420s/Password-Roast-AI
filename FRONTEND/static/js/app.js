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
        const roastElement = document.getElementById('roastText');
        const singingElement = document.getElementById('singingRoast');
        
        if (roastElement) {
            roastElement.innerHTML = this.escapeHtml(roast);
            roastElement.classList.add('fade-in');
        }
        
        if (singingElement && singingRoast) {
            singingElement.innerHTML = this.escapeHtml(singingRoast);
            singingElement.style.display = 'block';
        }
    }

    displayAnalysisDetails(data) {
        // Update basic metrics
        this.updateMetric('lengthValue', data.length);
        this.updateMetric('entropyValue', data.entropy);
        
        // Update character classes
        this.updateCharacterClasses(data.character_classes);
        
        // Update HIBP status
        this.updateHIBPStatus(data.hibp_check);
    }

    updateCharacterClasses(classes) {
        const elements = {
            'upper': document.getElementById('hasUpper'),
            'lower': document.getElementById('hasLower'),
            'digit': document.getElementById('hasDigit'),
            'special': document.getElementById('hasSpecial')
        };

        for (const [type, element] of Object.entries(elements)) {
            if (element) {
                const hasClass = classes[type];
                element.textContent = hasClass ? '✓' : '✗';
                element.className = `class-badge ${hasClass ? 'present' : 'missing'}`;
            }
        }
    }

    updateHIBPStatus(hibp) {
        const hibpElement = document.getElementById('hibpStatus');
        if (!hibpElement) return;

        if (hibp.pwned) {
            hibpElement.innerHTML = `
                <span class="hibp-badge pwned">⚠️ BREACHED</span>
                <small>Found in ${hibp.count} data breaches</small>
            `;
        } else {
            hibpElement.innerHTML = `
                <span class="hibp-badge safe">✅ SAFE</span>
                <small>Not found in known breaches</small>
            `;
        }
    }

    displayRecommendations(recommendations) {
        const container = document.getElementById('recommendationsList');
        if (!container) return;

        container.innerHTML = '';

        recommendations.forEach(rec => {
            const element = document.createElement('div');
            element.className = `recommendation priority-${rec.priority}`;
            element.innerHTML = `
                <div class="rec-header">
                    <span class="rec-priority">${rec.priority.toUpperCase()}</span>
                    <h4>${rec.title}</h4>
                </div>
                <p class="rec-description">${rec.description}</p>
                <div class="rec-action">${rec.action}</div>
            `;
            container.appendChild(element);
        });
    }

    displayWeaknesses(data) {
        const container = document.getElementById('weaknessDetails');
        if (!container) return;

        container.innerHTML = '';

        // Dictionary matches
        if (data.dictionary_matches && data.dictionary_matches.length > 0) {
            this.addWeaknessSection(container, 
                'Dictionary Words Found', 
                '🚨', 
                data.dictionary_matches.map(match => 
                    `"${match.matched_word}" (${match.language}${match.type === 'fuzzy' ? ' - similar word' : ''})`
                )
            );
        }

        // Patterns
        if (data.patterns_detected && data.patterns_detected.length > 0) {
            this.addWeaknessSection(container,
                'Patterns Detected',
                '⌨️',
                data.patterns_detected.map(pattern => {
                    switch (pattern.type) {
                        case 'keyboard_pattern': return 'Keyboard pattern';
                        case 'sequential_chars': return 'Sequential characters';
                        case 'repeated_chars': return 'Repeated characters';
                        case 'common_base': return `Common base: "${pattern.base_word}"`;
                        default: return pattern.type;
                    }
                })
            );
        }

        // Common password
        if (data.is_common_password) {
            this.addWeaknessSection(container,
                'Common Password',
                '📊',
                ['This is a very commonly used password that attackers try first']
            );
        }
    }

    addWeaknessSection(container, title, emoji, items) {
        const section = document.createElement('div');
        section.className = 'weakness-section';
        section.innerHTML = `
            <h4>${emoji} ${title}</h4>
            <ul>
                ${items.map(item => `<li>${this.escapeHtml(item)}</li>`).join('')}
            </ul>
        `;
        container.appendChild(section);
    }

    showLoading(show) {
        const loading = document.getElementById('loading');
        const roastButton = document.getElementById('roastButton');
        
        if (loading) loading.style.display = show ? 'block' : 'none';
        if (roastButton) {
            roastButton.disabled = show;
            roastButton.innerHTML = show ? 
                '<div class="button-spinner"></div> Analyzing...' : 
                'Roast Me! 🔥';
        }
    }

    showError(message) {
        // You could implement a toast notification system here
        alert(message);
    }

    showSection(sectionId) {
        // Hide all sections first
        const sections = ['resultSection', 'loading', 'errorSection'];
        sections.forEach(id => {
            const element = document.getElementById(id);
            if (element) element.style.display = 'none';
        });

        // Show target section
        const target = document.getElementById(sectionId);
        if (target) target.style.display = 'block';
    }

    togglePasswordVisibility() {
        const input = document.getElementById('passwordInput');
        const toggle = document.getElementById('togglePassword');
        
        if (input.type === 'password') {
            input.type = 'text';
            toggle.textContent = '🙈';
        } else {
            input.type = 'password';
            toggle.textContent = '👁️';
        }
    }

    toggleTheme() {
        const body = document.body;
        const currentTheme = body.getAttribute('data-theme') || 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        
        body.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        
        // Update theme toggle button
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.textContent = newTheme === 'light' ? '🌙' : '☀️';
        }
    }

    loadWordlistsInfo() {
        // Display supported languages
        const langElement = document.getElementById('supportedLanguages');
        if (langElement) {
            langElement.textContent = 'English, Swahili, Spanish, French + Common Patterns';
        }
    }

    animateResults() {
        const elements = document.querySelectorAll('.result-item, .weakness-section, .recommendation');
        elements.forEach((element, index) => {
            element.style.animationDelay = `${index * 0.1}s`;
            element.classList.add('fade-in-up');
        });
    }

    trackAnalysis(data) {
        // Basic analytics - you can integrate with Google Analytics etc.
        console.log('Password analyzed:', {
            strength: data.strength,
            score: data.score,
            length: data.length,
            has_hibp_match: data.hibp_check.pwned
        });
    }

    escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    updateMetric(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
        }
    }

    copyToClipboard(element) {
        const text = element.getAttribute('data-copy') || element.textContent;
        navigator.clipboard.writeText(text).then(() => {
            // Show copy confirmation
            const originalText = element.textContent;
            element.textContent = 'Copied! ✓';
            setTimeout(() => {
                element.textContent = originalText;
            }, 2000);
        });
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.passwordApp = new PasswordRoastApp();
    
    // Load saved theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.body.setAttribute('data-theme', savedTheme);
    
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.textContent = savedTheme === 'light' ? '🌙' : '☀️';
    }
});

// Service Worker for PWA capabilities (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}