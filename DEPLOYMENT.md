# Deployment Guide - Research Data Web Application

This guide provides multiple options for hosting your research data visualization web application so your professor can access it easily.

## 🚀 Quick Start (Local Development)

### Option 1: Python HTTP Server (Recommended for Local)

1. **Start the server:**
   ```bash
   python server.py
   ```

2. **Access the application:**
   - Open your browser and go to: `http://localhost:8000`
   - The server will automatically serve all files and provide API endpoints

3. **Share with professor:**
   - If on the same network, share your local IP address
   - Or use a service like ngrok for external access

### Option 2: Simple HTTP Server

```bash
# Python 3
python -m http.server 8000

# Python 2
python -m SimpleHTTPServer 8000
```

## 🌐 Cloud Hosting Options

### Option 1: GitHub Pages (Free)

1. **Create a GitHub repository:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/research-data-app.git
   git push -u origin main
   ```

2. **Enable GitHub Pages:**
   - Go to repository Settings → Pages
   - Select "Deploy from a branch"
   - Choose "main" branch and "/ (root)" folder
   - Save

3. **Access your site:**
   - Your site will be available at: `https://yourusername.github.io/research-data-app`

**Note:** GitHub Pages only serves static files, so the API endpoints won't work. You'll need to modify the JavaScript to use mock data or implement a different backend.

### Option 2: Netlify (Free)

1. **Deploy via Netlify:**
   - Go to [netlify.com](https://netlify.com)
   - Drag and drop your project folder
   - Or connect your GitHub repository

2. **Configure build settings:**
   - Build command: (leave empty for static site)
   - Publish directory: `.` (root)

3. **Custom domain (optional):**
   - Add your own domain in the domain settings

### Option 3: Vercel (Free)

1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Deploy:**
   ```bash
   vercel
   ```

3. **Follow the prompts:**
   - Project name: `research-data-app`
   - Framework: Other
   - Output directory: `.`

### Option 4: Heroku (Free tier discontinued)

1. **Create Procfile:**
   ```
   web: python server.py $PORT
   ```

2. **Deploy:**
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

## 🔧 Advanced Hosting with Backend

### Option 1: Railway (Recommended)

1. **Create account at [railway.app](https://railway.app)**

2. **Deploy from GitHub:**
   - Connect your GitHub repository
   - Railway will detect Python and deploy automatically

3. **Environment variables:**
   - Set `PORT` if needed (Railway sets this automatically)

4. **Access your app:**
   - Railway provides a public URL automatically

### Option 2: Render

1. **Create account at [render.com](https://render.com)**

2. **Create new Web Service:**
   - Connect your GitHub repository
   - Build Command: `pip install -r requirements.txt` (if you have one)
   - Start Command: `python server.py $PORT`

3. **Deploy:**
   - Render will automatically deploy your application

### Option 3: DigitalOcean App Platform

1. **Create account at [digitalocean.com](https://digitalocean.com)**

2. **Create App:**
   - Connect your GitHub repository
   - Choose Python as runtime
   - Set build command and run command

3. **Deploy:**
   - DigitalOcean will handle the deployment

## 📁 File Structure for Deployment

Ensure your project has this structure:

```
research-data-app/
├── index.html              # Main application
├── styles.css              # Styling
├── script.js               # JavaScript functionality
├── server.py               # Python server (for backend hosting)
├── README.md               # Documentation
├── DEPLOYMENT.md           # This file
└── August/                 # Your data files
    ├── done_processed_AD_data.csv
    ├── done_processed_AD_data_stats.txt
    └── ... (all your data files)
```

## 🔒 Security Considerations

### For Production Deployment

1. **HTTPS:**
   - Most cloud platforms provide HTTPS automatically
   - For local deployment, consider using ngrok with HTTPS

2. **File Access:**
   - The current server allows access to all files in the August directory
   - Consider implementing authentication for sensitive data

3. **CORS:**
   - The server includes CORS headers for cross-origin requests
   - Adjust as needed for your deployment environment

## 📱 Mobile and Tablet Access

The web application is fully responsive and works on:
- Desktop browsers (Chrome, Firefox, Safari, Edge)
- Mobile browsers (iOS Safari, Chrome Mobile)
- Tablet browsers (iPad, Android tablets)

## 🔧 Customization for Different Hosting

### For Static Hosting (GitHub Pages, Netlify, Vercel)

If you're using static hosting without a backend, modify `script.js`:

```javascript
// Comment out or remove API calls
// const response = await fetch('/api/files');
// Use mock data instead
```

### For Backend Hosting (Railway, Render, Heroku)

The current setup works out of the box with the Python server.

## 📊 Performance Optimization

1. **File Compression:**
   - Enable gzip compression on your server
   - Compress large CSV files if needed

2. **Caching:**
   - Set appropriate cache headers for static files
   - Consider implementing client-side caching for file data

3. **CDN:**
   - Use a CDN for faster global access
   - Most cloud platforms provide CDN automatically

## 🆘 Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   python server.py 8001  # Use different port
   ```

2. **File not found errors:**
   - Ensure all files are in the correct directories
   - Check file permissions

3. **CORS errors:**
   - The server includes CORS headers
   - If issues persist, check browser console for specific errors

4. **Large file loading:**
   - Consider implementing pagination for large CSV files
   - Add loading indicators for better UX

### Getting Help

- Check the browser console for JavaScript errors
- Review server logs for backend issues
- Ensure all dependencies are properly loaded

## 📞 Support

For deployment issues:
1. Check the platform's documentation
2. Review error logs
3. Test locally first
4. Consider using a simpler static hosting option initially

---

**Recommended Deployment Path:**
1. **Start with local server** for testing
2. **Use Railway or Render** for full functionality
3. **Use GitHub Pages** for simple static hosting
4. **Consider Vercel** for advanced features
