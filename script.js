// Simple Research Data Viewer - Country Based

class CountryDataViewer {
    constructor() {
        this.files = [];
        this.countries = {};
        this.currentView = 'browser';
        this.charts = {};
        this.currentCountry = null;
        this.init();
    }

    async init() {
        await this.loadFiles();
        this.organizeByCountry();
        this.setupEventListeners();
        this.renderCountryList();
        this.loadUpdates();
        
        // Handle initial URL state
        this.handleInitialState();
    }

    async loadFiles() {
        try {
            // For GitHub Pages, we'll use the hardcoded file list
            // since we can't run a server to scan the directory
            this.files = this.generateMockFiles();
            return;
        } catch (error) {
            console.warn('Error loading files, using mock data:', error);
            this.files = this.generateMockFiles();
        }
    }

    generateMockFiles() {
        const countries = [
            'AD', 'AF', 'AG', 'AI', 'AM', 'AO', 'AR', 'AW', 'BB', 'BD', 'BF', 'BH', 'BI', 'BJ', 'BN', 'BO', 'BS', 'BT', 'CD', 'CG', 'CI', 'CM', 'CR', 'CU', 'CV', 'DJ', 'DM', 'DO', 'DZ', 'ET', 'FJ', 'GA', 'GE', 'GM', 'GN', 'GQ', 'GT', 'GW', 'GY', 'HN', 'HT', 'IQ', 'IR', 'JM', 'JO', 'KE', 'KG', 'KH', 'KI', 'KM', 'KN', 'KP', 'KV', 'LA', 'LC', 'LK', 'LR', 'LS', 'LY', 'MC', 'MG', 'ML', 'MM', 'MN'
        ];

        const files = [];
        
        for (const country of countries) {
            // Add CSV file
            files.push({
                countryCode: country,
                fileName: `done_processed_${country}_data.csv`,
                fileType: 'csv',
                filePath: `August/done_processed_${country}_data.csv`,
                size: this.getRandomSize(1, 30),
                records: this.getRandomRecords(2, 100)
            });

            // Add stats file
            files.push({
                countryCode: country,
                fileName: `done_processed_${country}_data_stats.txt`,
                fileType: 'stats',
                filePath: `August/done_processed_${country}_data_stats.txt`,
                size: this.getRandomSize(0.5, 2),
                records: null
            });
        }

        return files;
    }

    organizeByCountry() {
        this.countries = {};
        
        this.files.forEach(file => {
            const countryCode = file.countryCode.replace('_', ''); // Remove trailing underscore
            
            if (!this.countries[countryCode]) {
                this.countries[countryCode] = {
                    code: countryCode,
                    name: this.getCountryName(countryCode),
                    csvFile: null,
                    statsFile: null,
                    totalRecords: 0,
                    totalSize: 0
                };
            }
            
            if (file.fileType === 'csv') {
                this.countries[countryCode].csvFile = file;
                this.countries[countryCode].totalRecords = file.records || 0;
            } else if (file.fileType === 'stats') {
                this.countries[countryCode].statsFile = file;
            }
            
            this.countries[countryCode].totalSize += file.size || 0;
        });
    }

    getCountryName(code) {
        const countryNames = {
            'AD': 'Andorra', 'AF': 'Afghanistan', 'AG': 'Antigua & Barbuda', 'AI': 'Anguilla',
            'AM': 'Armenia', 'AO': 'Angola', 'AR': 'Argentina', 'AW': 'Aruba',
            'BB': 'Barbados', 'BD': 'Bangladesh', 'BF': 'Burkina Faso', 'BH': 'Bahrain',
            'BI': 'Burundi', 'BJ': 'Benin', 'BN': 'Brunei', 'BO': 'Bolivia',
            'BS': 'Bahamas', 'BT': 'Bhutan', 'BW': 'Botswana',
            'CD': 'DR Congo', 'CG': 'Congo', 'CI': 'Ivory Coast', 'CM': 'Cameroon',
            'CR': 'Costa Rica', 'CU': 'Cuba', 'CV': 'Cape Verde',
            'DJ': 'Djibouti', 'DM': 'Dominica', 'DO': 'Dominican Republic', 'DZ': 'Algeria',
            'ET': 'Ethiopia',
            'FJ': 'Fiji',
            'GA': 'Gabon', 'GE': 'Georgia', 'GM': 'Gambia', 'GN': 'Guinea',
            'GQ': 'Equatorial Guinea', 'GT': 'Guatemala', 'GW': 'Guinea-Bissau', 'GY': 'Guyana',
            'HN': 'Honduras', 'HT': 'Haiti',
            'IQ': 'Iraq', 'IR': 'Iran',
            'JM': 'Jamaica', 'JO': 'Jordan',
            'KE': 'Kenya', 'KG': 'Kyrgyzstan', 'KH': 'Cambodia', 'KI': 'Kiribati',
            'KM': 'Comoros', 'KN': 'St. Kitts & Nevis', 'KP': 'North Korea', 'KV': 'Kosovo',
            'LA': 'Laos', 'LC': 'St. Lucia', 'LK': 'Sri Lanka', 'LR': 'Liberia',
            'LS': 'Lesotho', 'LY': 'Libya',
            'MC': 'Monaco', 'MG': 'Madagascar', 'ML': 'Mali', 'MM': 'Myanmar', 'MN': 'Mongolia'
        };
        
        return countryNames[code] || code;
    }

    getRandomSize(min, max) {
        return (Math.random() * (max - min) + min).toFixed(1);
    }

    getRandomRecords(min, max) {
        return Math.floor(Math.random() * (max - min) + min);
    }

    setupEventListeners() {
        // Search functionality
        document.getElementById('search').addEventListener('input', (e) => {
            this.filterCountries(e.target.value);
        });

        // Browser history handling
        window.addEventListener('popstate', (event) => {
            this.handlePopState(event);
        });
    }

    renderCountryList() {
        const countryList = document.getElementById('countryList');
        countryList.innerHTML = '';

        const countryCodes = Object.keys(this.countries).sort();
        
        if (countryCodes.length === 0) {
            countryList.innerHTML = `
                <div class="empty-state">
                    <h3>No countries found</h3>
                    <p>No data files are available.</p>
                </div>
            `;
            return;
        }

        countryCodes.forEach(countryCode => {
            const country = this.countries[countryCode];
            const countryItem = document.createElement('div');
            countryItem.className = 'country-item';
            countryItem.onclick = () => this.openCountry(country);
            
            countryItem.innerHTML = `
                <div class="country-code">${countryCode}</div>
                <div class="country-name">${country.name}</div>
                <div class="country-meta">${country.totalRecords} records</div>
            `;
            
            countryList.appendChild(countryItem);
        });
    }

    filterCountries(searchTerm) {
        const countryItems = document.querySelectorAll('.country-item');
        const term = searchTerm.toLowerCase();
        
        countryItems.forEach(item => {
            const countryCode = item.querySelector('.country-code').textContent.toLowerCase();
            const countryName = item.querySelector('.country-name').textContent.toLowerCase();
            
            if (countryCode.includes(term) || countryName.includes(term)) {
                item.style.display = '';
            } else {
                item.style.display = 'none';
            }
        });
    }

    async openCountry(country) {
        this.currentView = 'viewer';
        this.currentCountry = country;
        this.showViewer();
        
        // Update browser history
        const url = new URL(window.location);
        url.searchParams.set('country', country.code);
        window.history.pushState({ country: country.code }, `Country: ${country.code}`, url.toString());
        
        document.getElementById('viewerTitle').textContent = `Country: ${country.code}`;
        
        // Show loading states
        document.getElementById('chartContent').innerHTML = '<div class="loading">Loading visualization...</div>';
        document.getElementById('csvContent').innerHTML = '<div class="loading">Loading data...</div>';
        document.getElementById('statsContent').innerHTML = '<div class="loading">Loading statistics...</div>';
        
        try {
            // Load CSV data
            if (country.csvFile) {
                const csvContent = await this.loadFileContent(country.csvFile.filePath);
                this.displayCSVContent(csvContent, document.getElementById('csvContent'));
            } else {
                document.getElementById('csvContent').innerHTML = '<div class="loading">No CSV data available</div>';
            }
            
            // Load and visualize stats
            if (country.statsFile) {
                const statsContent = await this.loadFileContent(country.statsFile.filePath);
                this.displayStatsWithVisualization(statsContent, document.getElementById('chartContent'), document.getElementById('statsContent'), country.code);
            } else {
                document.getElementById('chartContent').innerHTML = '<div class="loading">No visualization available</div>';
                document.getElementById('statsContent').innerHTML = '<div class="loading">No statistics available</div>';
            }
            
        } catch (error) {
            console.error('Error loading country data:', error);
            document.getElementById('csvContent').innerHTML = '<div class="loading">Error loading data</div>';
            document.getElementById('statsContent').innerHTML = '<div class="loading">Error loading statistics</div>';
        }
    }

    async loadFileContent(filePath) {
        try {
            // For GitHub Pages, use raw GitHub URLs
            const githubRawUrl = `https://raw.githubusercontent.com/puneethkotha/Research-Data/main/${filePath}`;
            console.log(`Loading file from GitHub: ${githubRawUrl}`);
            
            const response = await fetch(githubRawUrl);
            if (response.ok) {
                const content = await response.text();
                console.log(`Successfully loaded file: ${filePath}, content length: ${content.length}`);
                return content;
            } else {
                console.error(`Failed to load file: ${filePath}, status: ${response.status}`);
            }
        } catch (error) {
            console.warn('GitHub Pages not available, using mock data:', error);
        }
        
        // Fallback to mock data
        console.log(`Using mock data for: ${filePath}`);
        return this.generateMockContent(filePath);
    }

    generateMockContent(filePath) {
        const isCSV = filePath.endsWith('.csv');
        const isStats = filePath.endsWith('.txt');
        
        if (isCSV) {
            const countryCode = filePath.match(/_([A-Z]{2})_data\.csv/)?.[1] || 'XX';
            return `parent_name,parent_id,parent_city,language,entity_type
"${countryCode} COMPANY 1",${countryCode}*1000001,${countryCode},en,company
"${countryCode} INDIVIDUAL 1",${countryCode}*1000002,${countryCode},en,individual
"${countryCode} FAMILY FIRM 1",${countryCode}*1000003,${countryCode},en,family_firm
"${countryCode} GOVERNMENT 1",${countryCode}*1000004,${countryCode},en,government
"${countryCode} COMPANY 2",${countryCode}*1000005,${countryCode},en,company`;
        } else if (isStats) {
            const countryCode = filePath.match(/_([A-Z]{2})_data_stats\.txt/)?.[1] || 'XX';
            return `${countryCode}_data.csv Processing Statistics
================================

Total Records: 25

Language Distribution:
- English (en): 20 records (80.0%)
- Local (local): 5 records (20.0%)

Entity Type Distribution:
- Company: 15 records (60.0%)
- Individual: 5 records (20.0%)
- Family Firm: 3 records (12.0%)
- Government: 2 records (8.0%)

Corrections Made:
- None

Notes:
- Standard distribution for ${countryCode}
- Most entities are companies
- Good mix of entity types`;
        }
        
        return 'File content not available';
    }

    displayCSVContent(content, container) {
        const lines = content.split('\n');
        if (lines.length === 0) {
            container.innerHTML = '<div class="loading">No data available</div>';
            return;
        }

        // Parse CSV properly handling quoted fields
        const parseCSVLine = (line) => {
            const result = [];
            let current = '';
            let inQuotes = false;
            
            for (let i = 0; i < line.length; i++) {
                const char = line[i];
                
                if (char === '"') {
                    if (inQuotes && line[i + 1] === '"') {
                        // Escaped quote
                        current += '"';
                        i++; // Skip next quote
                    } else {
                        // Toggle quote state
                        inQuotes = !inQuotes;
                    }
                } else if (char === ',' && !inQuotes) {
                    // End of field
                    result.push(current.trim());
                    current = '';
                } else {
                    current += char;
                }
            }
            
            // Add the last field
            result.push(current.trim());
            return result;
        };

        const headers = parseCSVLine(lines[0]);
        const rows = lines.slice(1).filter(line => line.trim()).map(line => parseCSVLine(line));

        // Debug: Log the first few rows to check parsing
        console.log('CSV Headers:', headers);
        console.log('First 3 rows:', rows.slice(0, 3));

        let tableHTML = '<table class="csv-table"><thead><tr>';
        headers.forEach(header => {
            tableHTML += `<th>${header.replace(/"/g, '')}</th>`;
        });
        tableHTML += '</tr></thead><tbody>';

        rows.forEach(row => {
            tableHTML += '<tr>';
            row.forEach(cell => {
                tableHTML += `<td>${cell.replace(/"/g, '')}</td>`;
            });
            tableHTML += '</tr>';
        });

        tableHTML += '</tbody></table>';
        container.innerHTML = tableHTML;
    }

    displayStatsWithVisualization(content, chartContainer, statsContainer, countryCode) {
        console.log(`Displaying stats for ${countryCode}:`, content.substring(0, 200) + '...');
        
        // Parse stats content to extract data
        const stats = this.parseStatsContent(content);
        
        // Show chart in chart container
        const chartHTML = `
            <canvas id="statsChart" width="400" height="300"></canvas>
        `;
        chartContainer.innerHTML = chartHTML;
        
        // Show stats text in stats container
        const statsHTML = `
            <div class="stats-content">${content}</div>
        `;
        statsContainer.innerHTML = statsHTML;
        
        // Create chart after DOM is updated
        setTimeout(() => {
            this.createStatsChart(stats, countryCode);
        }, 100);
    }

    parseStatsContent(content) {
        const stats = {
            totalRecords: 0,
            languages: {},
            entityTypes: {}
        };
        
        const lines = content.split('\n');
        let inLanguageSection = false;
        let inEntitySection = false;
        
        console.log('Parsing stats content:', content.substring(0, 200) + '...');
        
        lines.forEach(line => {
            const trimmedLine = line.trim();
            
            // Extract total records (handle both "Total Records:" and "Total Entries:")
            if (trimmedLine.includes('Total Records:') || trimmedLine.includes('Total Entries:')) {
                const match = trimmedLine.match(/Total (Records|Entries):\s*(\d+)/);
                if (match) stats.totalRecords = parseInt(match[2]);
            }
            
            // Check for section headers
            if (trimmedLine === 'Language Distribution:') {
                inLanguageSection = true;
                inEntitySection = false;
                console.log('Found Language Distribution section');
                return;
            }
            
            if (trimmedLine === 'Entity Type Distribution:') {
                inLanguageSection = false;
                inEntitySection = true;
                console.log('Found Entity Type Distribution section');
                return;
            }
            
            // Extract language distribution (handle both formats)
            if (inLanguageSection && trimmedLine.startsWith('-')) {
                // Try the standard format first
                let langMatch = trimmedLine.match(/- ([^(]+) \(([^)]+)\): (\d+) records/);
                if (langMatch) {
                    const languageName = langMatch[1].trim();
                    const languageCode = langMatch[2].trim();
                    const count = parseInt(langMatch[3]);
                    stats.languages[languageName] = count;
                    console.log(`Found language: ${languageName} (${languageCode}): ${count}`);
                } else {
                    // Try alternative format without percentages
                    langMatch = trimmedLine.match(/- ([^(]+) \(([^)]+)\): (\d+) entries/);
                    if (langMatch) {
                        const languageName = langMatch[1].trim();
                        const languageCode = langMatch[2].trim();
                        const count = parseInt(langMatch[3]);
                        stats.languages[languageName] = count;
                        console.log(`Found language: ${languageName} (${languageCode}): ${count}`);
                    }
                }
            }
            
            // Extract entity type distribution (handle both formats)
            if (inEntitySection && trimmedLine.startsWith('-')) {
                // Try the standard format first
                let entityMatch = trimmedLine.match(/- ([^:]+): (\d+) records/);
                if (entityMatch) {
                    const entityType = entityMatch[1].trim();
                    const count = parseInt(entityMatch[2]);
                    stats.entityTypes[entityType] = count;
                    console.log(`Found entity type: ${entityType}: ${count}`);
                } else {
                    // Try alternative format with "entries" and different entity type names
                    entityMatch = trimmedLine.match(/- ([^:]+): (\d+) entries/);
                    if (entityMatch) {
                        let entityType = entityMatch[1].trim();
                        const count = parseInt(entityMatch[2]);
                        
                        // Map alternative entity type names to standard ones
                        if (entityType === 'Companies') entityType = 'Company';
                        if (entityType === 'Individuals') entityType = 'Individual';
                        if (entityType === 'Government Entities') entityType = 'Government';
                        if (entityType === 'Family Firms') entityType = 'Family Firm';
                        
                        stats.entityTypes[entityType] = count;
                        console.log(`Found entity type: ${entityType}: ${count}`);
                    }
                }
            }
        });
        
        console.log('Parsed stats:', stats);
        return stats;
    }

    createStatsChart(stats, countryCode) {
        const ctx = document.getElementById('statsChart');
        if (!ctx) {
            console.error('Chart canvas element not found');
            return;
        }
        
        // Destroy existing chart
        if (this.charts[countryCode]) {
            this.charts[countryCode].destroy();
        }
        
        const entityData = Object.entries(stats.entityTypes);
        console.log(`Creating chart for ${countryCode}:`, stats, entityData);
        
        // Only create chart if we have entity data
        if (entityData.length === 0) {
            console.warn(`No entity data found for ${countryCode}`);
            ctx.parentElement.style.display = 'none';
            return;
        }
        
        ctx.parentElement.style.display = 'block';
        
        try {
            // Create entity type chart
            this.charts[countryCode] = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: entityData.map(([label]) => label),
                    datasets: [{
                        data: entityData.map(([, value]) => value),
                        backgroundColor: ['#0066cc', '#34c759', '#ff9500', '#ff3b30', '#af52de'],
                        borderWidth: 2,
                        borderColor: '#ffffff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 20,
                                usePointStyle: true
                            }
                        },
                        title: {
                            display: true,
                            text: `${countryCode} - Entity Type Distribution`,
                            font: {
                                size: 14
                            }
                        }
                    }
                }
            });
            console.log(`Chart created successfully for ${countryCode}`);
        } catch (error) {
            console.error(`Error creating chart for ${countryCode}:`, error);
            ctx.parentElement.innerHTML = `<div class="error">Error creating chart: ${error.message}</div>`;
        }
    }

    showViewer() {
        document.querySelector('.country-browser').style.display = 'none';
        document.getElementById('countryViewer').style.display = 'block';
    }

    showBrowser() {
        this.currentView = 'browser';
        this.currentCountry = null;
        document.querySelector('.country-browser').style.display = 'block';
        document.getElementById('countryViewer').style.display = 'none';
        
        // Update browser history
        const url = new URL(window.location);
        url.searchParams.delete('country');
        window.history.pushState({ view: 'browser' }, 'Research Data', url.toString());
    }



    handleInitialState() {
        const urlParams = new URLSearchParams(window.location.search);
        const countryCode = urlParams.get('country');
        
        if (countryCode && this.countries[countryCode]) {
            this.openCountry(this.countries[countryCode]);
        }
    }

    handlePopState(event) {
        const urlParams = new URLSearchParams(window.location.search);
        const countryCode = urlParams.get('country');
        
        if (countryCode && this.countries[countryCode]) {
            // User navigated to a country view
            this.openCountry(this.countries[countryCode]);
        } else {
            // User navigated back to browser view
            this.showBrowser();
        }
    }

    loadUpdates() {
        const updates = [
            {
                icon: 'FIX',
                text: 'Fixed CSV parsing for quoted fields with commas - resolves issue with company names containing commas being split across multiple columns',
                isNew: true
            },
            {
                icon: 'CHART',
                text: 'Fixed visualization charts for all countries - resolved stats file format compatibility issues',
                isNew: true
            },
            {
                icon: 'ADD',
                text: 'Added missing stats file for LK (Sri Lanka) - now shows proper visualization',
                isNew: true
            },
            {
                icon: 'ENHANCE',
                text: 'Enhanced country data browser with improved search and filtering capabilities',
                isNew: false
            },
            {
                icon: 'DATA',
                text: 'Added comprehensive entity type distribution charts for all countries',
                isNew: false
            }
        ];

        const notificationContent = document.getElementById('notificationContent');
        if (!notificationContent) return;

        // Count new updates for badge
        const newUpdatesCount = updates.filter(update => update.isNew).length;
        const badge = document.getElementById('notificationBadge');
        if (badge) {
            badge.textContent = newUpdatesCount;
            if (newUpdatesCount === 0) {
                badge.style.display = 'none';
            }
        }

        let updatesHTML = '';
        updates.forEach(update => {
            const newClass = update.isNew ? 'new' : '';
            updatesHTML += `
                <div class="update-item ${newClass}">
                    <div class="update-icon">${update.icon}</div>
                    <div class="update-text">${update.text}</div>
                </div>
            `;
        });

        console.log('Loading updates without dates:', updatesHTML);
        notificationContent.innerHTML = updatesHTML;
    }
}

// Global function for back button
function closeViewer() {
    app.currentView = 'browser';
    app.showBrowser();
}

// Global function to toggle updates dropdown
function toggleUpdates() {
    const dropdown = document.getElementById('updatesDropdown');
    if (dropdown) {
        dropdown.classList.toggle('show');
    }
}

// Global function to close updates dropdown
function closeUpdates() {
    const dropdown = document.getElementById('updatesDropdown');
    if (dropdown) {
        dropdown.classList.remove('show');
    }
}

// Close dropdown when clicking outside
document.addEventListener('click', function(event) {
    const bell = document.getElementById('updatesBell');
    const dropdown = document.getElementById('updatesDropdown');
    
    if (bell && dropdown && !bell.contains(event.target)) {
        dropdown.classList.remove('show');
    }
});

// Initialize the application
const app = new CountryDataViewer();
