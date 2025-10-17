// Interactive AI Workflow Showcase JavaScript

// Navigation functionality
function showSection(sectionId) {
    // Hide all sections
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(section => {
        section.classList.remove('active');
    });
    
    // Show selected section
    document.getElementById(sectionId).classList.add('active');
    
    // Update navigation buttons
    const navButtons = document.querySelectorAll('.nav-btn');
    navButtons.forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Initialize section-specific features
    if (sectionId === 'workflow') {
        initializeWorkflow();
    } else if (sectionId === 'demo') {
        initializeDemo();
    } else if (sectionId === 'technical') {
        initializeTechnical();
    }
}

// Initialize workflow section
function initializeWorkflow() {
    // Add scroll-triggered animations
    const decisionNodes = document.querySelectorAll('.decision-node');
    
    // Intersection Observer for scroll animations
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, index * 200);
            }
        });
    }, { threshold: 0.5 });
    
    decisionNodes.forEach((node, index) => {
        node.style.opacity = '0';
        node.style.transform = 'translateY(30px)';
        node.style.transition = 'all 0.6s ease';
        observer.observe(node);
    });
    
    // Add click interactions for decision nodes
    decisionNodes.forEach(node => {
        node.addEventListener('click', function() {
            // Remove active class from all nodes
            decisionNodes.forEach(n => n.classList.remove('active'));
            // Add active class to clicked node
            this.classList.add('active');
            
            // Show detailed information
            showNodeDetails(this);
        });
    });
}

// Show detailed information for decision nodes
function showNodeDetails(node) {
    const step = node.getAttribute('data-step');
    
    // Animate the node details
    const details = node.querySelector('.node-details');
    if (details) {
        details.style.transform = 'scale(1.05)';
        setTimeout(() => {
            details.style.transform = 'scale(1)';
        }, 200);
    }
    
    // Add visual feedback
    node.style.boxShadow = '0 8px 30px rgba(0, 122, 255, 0.3)';
    setTimeout(() => {
        node.style.boxShadow = '';
    }, 1000);
}



// Initialize live demo section
function initializeDemo() {
    // Add entity selection interactions
    const entityOptions = document.querySelectorAll('.entity-option');
    
    entityOptions.forEach(option => {
        option.addEventListener('click', function() {
            // Remove active class from all options
            entityOptions.forEach(o => o.classList.remove('active'));
            // Add active class to selected option
            this.classList.add('active');
            
            // Get the selected entity
            const selectedEntity = this.getAttribute('data-entity');
            
            // Start the classification process
            startClassificationProcess(selectedEntity);
        });
    });
    
    // Initialize process steps
    initializeProcessSteps();
}

// Initialize process steps
function initializeProcessSteps() {
    const processSteps = document.querySelectorAll('.process-step');
    
    // Add scroll animations
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateX(0)';
                }, index * 300);
            }
        });
    }, { threshold: 0.3 });
    
    processSteps.forEach((step, index) => {
        step.style.opacity = '0';
        step.style.transform = 'translateX(-30px)';
        step.style.transition = 'all 0.6s ease';
        observer.observe(step);
    });
}

// Start classification process
function startClassificationProcess(entityName) {
    // Update the process steps with the selected entity
    updateProcessSteps(entityName);
    
    // Animate through the process
    animateClassificationProcess();
}

// Update process steps with entity data
function updateProcessSteps(entityName) {
    // Step 1: Text Analysis
    const step1 = document.querySelector('.process-step[data-step="1"] .text-breakdown');
    if (step1) {
        step1.innerHTML = '';
        const words = entityName.split(' ');
        words.forEach(word => {
            const wordSpan = document.createElement('span');
            wordSpan.className = 'word';
            wordSpan.textContent = word;
            step1.appendChild(wordSpan);
        });
    }
    
    // Step 2: Language Detection
    const step2 = document.querySelector('.process-step[data-step="2"] .language-results');
    if (step2) {
        // Analyze language patterns
        const languages = analyzeLanguages(entityName);
        step2.innerHTML = '';
        
        languages.forEach(lang => {
            const langResult = document.createElement('div');
            langResult.className = 'lang-result';
            langResult.innerHTML = `
                <span class="lang-name">${lang.name}</span>
                <span class="lang-words">${lang.words.join(', ')}</span>
            `;
            step2.appendChild(langResult);
        });
    }
    
    // Step 3: Pattern Matching
    const step3 = document.querySelector('.process-step[data-step="3"] .pattern-results');
    if (step3) {
        const patterns = detectPatterns(entityName);
        step3.innerHTML = '';
        
        patterns.forEach(pattern => {
            const patternResult = document.createElement('div');
            patternResult.className = 'pattern-result';
            patternResult.innerHTML = `
                <span class="pattern-name">${pattern.type}</span>
                <span class="pattern-match">${pattern.match}</span>
            `;
            step3.appendChild(patternResult);
        });
    }
    
    // Step 4: Scoring
    const step4 = document.querySelector('.process-step[data-step="4"] .scoring-results');
    if (step4) {
        const scores = calculateScores(entityName);
        step4.innerHTML = '';
        
        Object.entries(scores).forEach(([category, score]) => {
            const scoreResult = document.createElement('div');
            scoreResult.className = `score-result ${category}`;
            scoreResult.innerHTML = `
                <span class="score-label">${category.charAt(0).toUpperCase() + category.slice(1)}</span>
                <span class="score-value">${score}</span>
            `;
            step4.appendChild(scoreResult);
        });
    }
    
    // Step 5: Final Result
    const step5 = document.querySelector('.process-step[data-step="5"] .final-result');
    if (step5) {
        const result = getFinalClassification(entityName);
        step5.innerHTML = `
            <div class="result-type ${result.type}">
                <span class="type-name">${result.type.charAt(0).toUpperCase() + result.type.slice(1)}</span>
                <span class="type-confidence">${result.confidence}% Confidence</span>
            </div>
            <div class="result-explanation">
                <span class="explanation-text">${result.reasoning}</span>
            </div>
        `;
    }
}

// Analyze languages in entity name
function analyzeLanguages(entityName) {
    const languages = [];
    
    // Check for Arabic names
    const arabicNames = ['MOHAMMED', 'AHMED', 'KHAN', 'ABDUL', 'ALI', 'HUSSEIN', 'AZIZ', 'RAHMAN', 'ZAHRA'];
    const arabicWords = entityName.split(' ').filter(word => 
        arabicNames.includes(word.toUpperCase())
    );
    
    if (arabicWords.length > 0) {
        languages.push({
            name: 'Arabic',
            words: arabicWords
        });
    }
    
    // Check for Spanish names
    const spanishNames = ['MARIA', 'GARCIA', 'RODRIGUEZ', 'FAMILIA', 'HIJOS', 'EMPRESA'];
    const spanishWords = entityName.split(' ').filter(word => 
        spanishNames.includes(word.toUpperCase())
    );
    
    if (spanishWords.length > 0) {
        languages.push({
            name: 'Spanish',
            words: spanishWords
        });
    }
    
    // Check for African names
    const africanNames = ['DENNIS', 'KAPUTO', 'CHIWELE'];
    const africanWords = entityName.split(' ').filter(word => 
        africanNames.includes(word.toUpperCase())
    );
    
    if (africanWords.length > 0) {
        languages.push({
            name: 'African',
            words: africanWords
        });
    }
    
    // Check for English terms
    const englishTerms = ['MR.', 'MRS.', 'MS.', 'DR.', 'PROF.', 'SHEIKH', 'LTD', 'LIMITED', 'INC', 'CORP', 'COMPANY', '&', 'AND', 'GLOBAL', 'MARINE', 'SHIPPING', 'SERVICES', 'INVESTMENTS', 'TRADING', 'GOVERNMENT', 'MINISTRY', 'DEPARTMENT', 'BANK', 'RESERVE', 'CENTRAL', 'NATIONAL', 'FAMILY', 'HOLDINGS', 'GROUP', 'PARTNERS', 'ENTERPRISES'];
    const englishWords = entityName.split(' ').filter(word => 
        englishTerms.includes(word.toUpperCase())
    );
    
    if (englishWords.length > 0) {
        languages.push({
            name: 'English',
            words: englishWords
        });
    }
    
    // Check for Russian patterns
    const russianPatterns = ['KOMPANIYA', 'KORPORATSIYA', 'KHOLDING'];
    const russianWords = entityName.split(' ').filter(word => 
        russianPatterns.includes(word.toUpperCase())
    );
    
    if (russianWords.length > 0) {
        languages.push({
            name: 'Russian',
            words: russianWords
        });
    }
    
    // Check for Portuguese terms
    const portugueseTerms = ['EMPRESA', 'NACIONAL', 'DE', 'HIDROCARBONETOS'];
    const portugueseWords = entityName.split(' ').filter(word => 
        portugueseTerms.includes(word.toUpperCase())
    );
    
    if (portugueseWords.length > 0) {
        languages.push({
            name: 'Portuguese',
            words: portugueseWords
        });
    }
    
    return languages;
}

// Detect patterns in entity name
function detectPatterns(entityName) {
    const patterns = [];
    
    // Personal titles
    if (entityName.match(/^(MR\.|MRS\.|MS\.|DR\.|PROF\.|SHEIKH)/i)) {
        patterns.push({
            type: 'Personal Title',
            match: entityName.match(/^(MR\.|MRS\.|MS\.|DR\.|PROF\.|SHEIKH)/i)[0]
        });
    }
    
    // Family indicators
    if (entityName.match(/& (SONS|BROTHERS|PARTNERS)/i) || entityName.match(/(FAMILY|FAMILIA)/i)) {
        const familyMatch = entityName.match(/& (SONS|BROTHERS|PARTNERS)/i) || entityName.match(/(FAMILY|FAMILIA)/i);
        patterns.push({
            type: 'Family Indicator',
            match: familyMatch[0]
        });
    }
    
    // Company suffixes
    if (entityName.match(/(LTD|LIMITED|INC|CORP|COMPANY|CORP|PVT|CO)$/i)) {
        patterns.push({
            type: 'Company Suffix',
            match: entityName.match(/(LTD|LIMITED|INC|CORP|COMPANY|CORP|PVT|CO)$/i)[0]
        });
    }
    
    // Business terms
    if (entityName.match(/(INVESTMENTS|TRADING|SERVICES|SHIPPING|MARINE|FOODS|HOLDINGS|GROUP|ENTERPRISES)/i)) {
        patterns.push({
            type: 'Business Terms',
            match: entityName.match(/(INVESTMENTS|TRADING|SERVICES|SHIPPING|MARINE|FOODS|HOLDINGS|GROUP|ENTERPRISES)/i)[0]
        });
    }
    
    // Government terms
    if (entityName.match(/(GOVERNMENT|MINISTRY|DEPARTMENT|BANK|RESERVE|CENTRAL|NATIONAL)/i)) {
        patterns.push({
            type: 'Government Terms',
            match: entityName.match(/(GOVERNMENT|MINISTRY|DEPARTMENT|BANK|RESERVE|CENTRAL|NATIONAL)/i)[0]
        });
    }
    
    // Arabic names
    const arabicNames = ['MOHAMMED', 'AHMED', 'KHAN', 'ABDUL', 'ALI', 'HUSSEIN', 'AZIZ', 'RAHMAN', 'ZAHRA'];
    const arabicWords = entityName.split(' ').filter(word => 
        arabicNames.includes(word.toUpperCase())
    );
    
    if (arabicWords.length > 0) {
        patterns.push({
            type: 'Arabic Names',
            match: arabicWords.join(', ')
        });
    }
    
    // Spanish names
    const spanishNames = ['MARIA', 'GARCIA', 'RODRIGUEZ', 'FAMILIA', 'HIJOS'];
    const spanishWords = entityName.split(' ').filter(word => 
        spanishNames.includes(word.toUpperCase())
    );
    
    if (spanishWords.length > 0) {
        patterns.push({
            type: 'Spanish Names',
            match: spanishWords.join(', ')
        });
    }
    
    // Russian patterns
    const russianPatterns = ['KOMPANIYA', 'KORPORATSIYA', 'KHOLDING'];
    const russianWords = entityName.split(' ').filter(word => 
        russianPatterns.includes(word.toUpperCase())
    );
    
    if (russianWords.length > 0) {
        patterns.push({
            type: 'Russian Patterns',
            match: russianWords.join(', ')
        });
    }
    
    // Portuguese terms
    const portugueseTerms = ['EMPRESA', 'NACIONAL', 'DE', 'HIDROCARBONETOS'];
    const portugueseWords = entityName.split(' ').filter(word => 
        portugueseTerms.includes(word.toUpperCase())
    );
    
    if (portugueseWords.length > 0) {
        patterns.push({
            type: 'Portuguese Terms',
            match: portugueseWords.join(', ')
        });
    }
    
    return patterns;
}

// Calculate scores for different categories
function calculateScores(entityName) {
    const scores = {
        individual: 0,
        family_firm: 0,
        company: 0,
        government: 0
    };
    
    // Individual scoring
    if (entityName.match(/^(MR\.|MRS\.|MS\.|DR\.|PROF\.|SHEIKH)/i)) {
        scores.individual += 45;
    }
    
    if (entityName.match(/[A-Z]{2,}\s[A-Z]{2,}$/)) {
        scores.individual += 15;
    }
    
    // Family firm scoring
    if (entityName.match(/& (SONS|BROTHERS|PARTNERS)/i)) {
        scores.family_firm += 60;
    }
    
    if (entityName.match(/(FAMILY|FAMILIA)/i)) {
        scores.family_firm += 40;
    }
    
    if (entityName.match(/(HIJOS|PARTNERS)/i)) {
        scores.family_firm += 35;
    }
    
    // Company scoring
    if (entityName.match(/(LTD|LIMITED|INC|CORP|COMPANY|CORP|PVT|CO)$/i)) {
        scores.company += 30;
    }
    
    if (entityName.match(/(INVESTMENTS|TRADING|SERVICES|SHIPPING|MARINE|FOODS|HOLDINGS|GROUP|ENTERPRISES)/i)) {
        scores.company += 20;
    }
    
    if (entityName.match(/(GLOBAL|INTERNATIONAL|NATIONAL)/i)) {
        scores.company += 15;
    }
    
    // Government scoring
    if (entityName.match(/(GOVERNMENT|MINISTRY|DEPARTMENT)/i)) {
        scores.government += 50;
    }
    
    if (entityName.match(/(BANK|RESERVE|CENTRAL|NATIONAL)/i)) {
        scores.government += 45;
    }
    
    if (entityName.match(/(EMPRESA NACIONAL)/i)) {
        scores.government += 40;
    }
    
    return scores;
}

// Get final classification
function getFinalClassification(entityName) {
    const scores = calculateScores(entityName);
    const maxScore = Math.max(...Object.values(scores));
    const category = Object.keys(scores).find(key => scores[key] === maxScore);
    
    // Calculate confidence based on score difference
    const totalScore = Object.values(scores).reduce((a, b) => a + b, 0);
    const confidence = totalScore > 0 ? Math.round((maxScore / totalScore) * 100) : 0;
    
    // Generate reasoning
    const reasoning = generateReasoning(category, scores);
    
    return {
        type: category,
        confidence: confidence,
        reasoning: reasoning
    };
}

// Generate reasoning for classification
function generateReasoning(category, scores) {
    const reasons = [];
    
    if (category === 'individual') {
        if (scores.individual > 0) reasons.push('personal titles and simple structure');
    } else if (category === 'family_firm') {
        if (scores.family_firm > 0) reasons.push('family business indicators');
        if (scores.individual > 0) reasons.push('personal elements');
    } else if (category === 'company') {
        if (scores.company > 0) reasons.push('business terminology and legal structure');
    } else if (category === 'government') {
        if (scores.government > 0) reasons.push('institutional and governmental terms');
    }
    
    return `Classified as ${category} due to ${reasons.join(' and ')}`;
}

// Animate classification process
function animateClassificationProcess() {
    const processSteps = document.querySelectorAll('.process-step');
    
    processSteps.forEach((step, index) => {
        setTimeout(() => {
            step.style.borderColor = '#007aff';
            step.style.background = '#e3f2fd';
            
            // Add processing animation
            const stepHeader = step.querySelector('.step-header');
            if (stepHeader) {
                stepHeader.style.color = '#007aff';
            }
            
            // Reset after animation
            setTimeout(() => {
                step.style.borderColor = '';
                step.style.background = '';
                if (stepHeader) {
                    stepHeader.style.color = '';
                }
            }, 2000);
        }, index * 1000);
    });
}

// Initialize technical details section
function initializeTechnical() {
    // Add hover effects to architecture layers
    const archLayers = document.querySelectorAll('.arch-layer');
    
    archLayers.forEach(layer => {
        layer.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px) scale(1.02)';
        });
        
        layer.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
    
    // Add scroll animations
    const techCards = document.querySelectorAll('.tech-card');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, index * 200);
            }
        });
    }, { threshold: 0.3 });
    
    techCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'all 0.6s ease';
        observer.observe(card);
    });
}



// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize first section
    showSection('workflow');
    
    // Add smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add scroll-triggered animations for all sections
    const sections = document.querySelectorAll('.content-section');
    const sectionObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });
    
    sections.forEach(section => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        section.style.transition = 'all 0.6s ease';
        sectionObserver.observe(section);
    });
});

// Export functions for external use
window.AIWorkflow = {
    showSection,
    startClassificationProcess
};
