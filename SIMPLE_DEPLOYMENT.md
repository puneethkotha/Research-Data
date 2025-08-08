# Simple Research Data Viewer - Country Based

## 🚀 Quick Start

### Local Development

1. **Start the server:**
   ```bash
   python3 server.py
   ```

2. **Access the application:**
   - Open your browser and go to: `http://localhost:8000`
   - The application will load all your data files organized by country

3. **Share with professor:**
   - If on the same network, share your local IP address
   - Or use ngrok for external access: `ngrok http 8000`

## 🌐 Simple Hosting Options

### Option 1: Railway (Recommended - Free)

1. **Create account at [railway.app](https://railway.app)**

2. **Deploy from GitHub:**
   - Connect your GitHub repository
   - Railway will detect Python and deploy automatically
   - Your app will be live in minutes

3. **Get your URL:**
   - Railway provides a public URL like: `https://your-app-name.railway.app`
   - Share this URL with your professor

### Option 2: Render (Free)

1. **Create account at [render.com](https://render.com)**

2. **Create new Web Service:**
   - Connect your GitHub repository
   - Build Command: (leave empty)
   - Start Command: `python server.py $PORT`

3. **Deploy:**
   - Render will automatically deploy your application
   - Get your public URL

### Option 3: Heroku (Free tier discontinued)

1. **Create Procfile:**
   ```
   web: python server.py $PORT
   ```

2. **Deploy:**
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

## 📁 What's Included

The country-based version includes:

- **Country Grid** - Clean grid of all countries with record counts
- **Search functionality** - Find countries by country code
- **Data Viewer** - View CSV data in clean tables when you click a country
- **Statistics Visualization** - Automatic charts showing entity type distribution
- **Responsive design** - Works on desktop, tablet, and mobile
- **Real data** - Connects to your actual August/ directory files

## 🎯 Features

### For Your Professor

1. **Browse Countries:**
   - See all countries as a clean grid (KE, US, UK, etc.)
   - Each country shows the number of records
   - Search for specific countries easily

2. **View Country Data:**
   - Click any country to see both data and statistics
   - CSV data displays in clean, formatted tables
   - Statistics show as both text and interactive charts
   - Entity type distribution visualized automatically

3. **Simple Interface:**
   - Clean, minimalistic design
   - No complex navigation
   - Focus on the data and insights

## 🔧 Technical Details

### File Structure
```
your-project/
├── index.html          # Main application
├── styles.css          # Minimalistic styling
├── script.js           # Country-based functionality
├── server.py           # Python server
└── August/             # Your data files
    ├── done_processed_AD_data.csv
    ├── done_processed_AD_data_stats.txt
    └── ... (all your files)
```

### API Endpoints
- `GET /api/files` - List all available files
- `GET /api/file-content?path=filepath` - Get file content
- `GET /` - Main application

### Data Organization
- Files are automatically organized by country code
- Each country shows both CSV data and statistics
- Statistics are parsed and visualized as charts
- Entity type distribution is automatically extracted and displayed

## 📱 Mobile Friendly

The application works perfectly on:
- Desktop browsers
- Mobile phones
- Tablets
- Any device with a web browser

## 🚀 Deployment Steps

### Step 1: Prepare Your Files
Make sure you have:
- All your data files in the `August/` directory
- The web application files (index.html, styles.css, script.js, server.py)

### Step 2: Choose Hosting
**Recommended: Railway**
- Free tier available
- Automatic deployment
- HTTPS included
- Easy to use

### Step 3: Deploy
1. Push your code to GitHub
2. Connect to Railway/Render
3. Deploy automatically
4. Share the URL with your professor

## 💡 Tips

### For Local Testing
```bash
# Start server
python3 server.py

# Test in browser
open http://localhost:8000

# Test API
curl http://localhost:8000/api/files
```

### For External Access
```bash
# Install ngrok
brew install ngrok  # macOS
# or download from ngrok.com

# Create tunnel
ngrok http 8000

# Share the ngrok URL with your professor
```

### For Production
- The application automatically detects real vs mock data
- If API is available, it uses real data
- If not, it falls back to mock data for demonstration
- Charts are automatically generated from stats files

## 🎉 That's It!

Your professor can now:
1. **Visit the URL** you share
2. **Browse countries** in a clean grid layout
3. **Click any country** to see data and statistics
4. **View interactive charts** showing entity type distribution
5. **Search for specific countries** easily
6. **Access from any device** - desktop, phone, or tablet

The interface is intentionally simple and minimalistic, focusing entirely on your research data with automatic visualization of key insights.
