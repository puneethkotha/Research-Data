# Data Classification Research - Parent Entity Analysis
<img width="420" height="360" alt="project-thumbnail" src="https://github.com/user-attachments/assets/0482247c-10eb-4615-afca-7e2eb1a37b90" />

## Project Overview

This research project focuses on identifying individuals vs. companies vs. family firms in vertical ownership patterns across global markets. The dataset contains approximately 1.4 million unique parent entities from over 120 countries, classified into four categories:

- **Individual**: Personal names (e.g., "John Smith")
- **Company**: Corporate entities (e.g., "Midwest Cargo Inc.")
- **Family Firm**: Family-owned businesses (e.g., "John Smith & Sons Inc.")
- **Government**: Government branches and agencies (e.g., "Metropolis Water Agency")

## Research Objective

The goal is to study different vertical ownership patterns of firms across the world, where a firm "A" indirectly controls a firm "C" through an intermediary company "B" (A → B → C). The main research question is whether widely controlled firms behave differently from family firms or government-owned firms.

## Web Application Features

### 🏠 Dashboard
- **Overview Statistics**: Countries analyzed, total files, entity count, and languages
- **Interactive Charts**: Entity type distribution and top countries by entity count
- **Project Information**: Research background and objectives

### 📁 File Browser
- **Complete File List**: All processed CSV and stats files from 120+ countries
- **Search & Filter**: Find files by country code or file type
- **File Viewer**: View CSV data in formatted tables and stats in readable format
- **Download**: Download individual files for further analysis

### 📊 Data Visualizations
- **Interactive Charts**: Generate custom visualizations for any country
- **Multiple Chart Types**: Entity type, language, and city distribution
- **Real-time Generation**: Select country and chart type to create visualizations

### 📝 Research Notes & Feedback
- **Note Management**: Add, categorize, and manage research notes
- **Categories**: General, Methodology, Data Quality, Corrections, Improvements
- **Persistent Storage**: Notes saved locally for continued collaboration
- **Filtering**: Filter notes by category for organized review

## File Structure

```
August/
├── done_processed_AD_data.csv          # Andorra processed data
├── done_processed_AD_data_stats.txt    # Andorra statistics
├── done_processed_AF_data.csv          # Afghanistan processed data
├── done_processed_AF_data_stats.txt    # Afghanistan statistics
└── ... (120+ countries)
```

### CSV File Format
Each CSV file contains the following columns:
- `parent_name`: Name of the parent entity
- `parent_id`: Unique identifier
- `parent_city`: City location
- `language`: Detected language code
- `entity_type`: Classification (individual, company, family_firm, government)

### Stats File Format
Each stats file contains:
- Total record count
- Language distribution
- Entity type distribution
- Corrections made during processing
- Research notes and observations

## How to Use the Web Application

### For Professors/Researchers

1. **View Dashboard**: Start with the overview to understand the scope and scale of the research
2. **Browse Files**: Use the file browser to explore specific countries or regions of interest
3. **Analyze Data**: View CSV files in formatted tables and read detailed statistics
4. **Create Visualizations**: Generate custom charts for specific countries or data aspects
5. **Add Notes**: Leave feedback, corrections, or suggestions using the notes system

### Navigation Tips

- **Search Files**: Use the search bar to find specific countries (e.g., "US", "UK", "DE")
- **Filter by Type**: Choose to view only CSV files or stats files
- **View Details**: Click "View" on any file to see its contents in a modal window
- **Generate Charts**: Select a country and chart type to create custom visualizations
- **Manage Notes**: Add categorized notes and filter them for organized review

## Technical Implementation

### Frontend Technologies
- **HTML5**: Semantic structure and accessibility
- **CSS3**: Modern styling with gradients, animations, and responsive design
- **JavaScript (ES6+)**: Interactive functionality and data processing
- **Bootstrap 5**: Responsive UI framework
- **Chart.js**: Interactive data visualizations
- **PapaParse**: CSV parsing and display

### Key Features
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Local Storage**: Notes persist between sessions
- **Real-time Search**: Instant file filtering and search
- **Interactive Charts**: Dynamic data visualizations
- **Modal File Viewer**: Clean file viewing experience

## Research Methodology

### Data Processing Pipeline
1. **Raw Data Collection**: 1.4M+ parent entities from 120+ countries
2. **Language Detection**: Automatic language identification for multi-language support
3. **Entity Classification**: ML-based classification into four categories
4. **Quality Control**: Manual review and correction of classifications
5. **Statistical Analysis**: Generation of comprehensive statistics per country

### Classification Criteria
- **Individual**: Personal names, typically first and last names
- **Company**: Corporate entities with business suffixes (Inc., Ltd., Corp., etc.)
- **Family Firm**: Family-owned businesses with family indicators (& Sons, & Co., etc.)
- **Government**: Government agencies, public institutions, state-owned entities

## Future Enhancements

### Planned Features
- **Real-time Data Updates**: Live data synchronization
- **Advanced Analytics**: Statistical significance testing
- **Export Functionality**: PDF reports and data exports
- **Collaborative Features**: Multi-user note sharing
- **API Integration**: Direct database connectivity

### Research Extensions
- **Temporal Analysis**: Ownership pattern changes over time
- **Geographic Clustering**: Regional ownership pattern analysis
- **Industry Classification**: Sector-specific ownership patterns
- **Cross-border Analysis**: International ownership structures

## Contact & Support

For questions about the research methodology, data processing, or web application functionality, please contact the research team.

---

**Note**: This web application is designed for academic research purposes and provides a comprehensive interface for exploring and analyzing the processed parent entity classification data.
=======
# Research-Data
Parent entity classification analysis
>>>>>>> bbbdbfa48999d1cfb257fc8d2015f26ec38ac749
