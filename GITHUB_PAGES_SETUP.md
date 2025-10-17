# GitHub Pages Setup Guide

## How to Deploy to GitHub Pages

### Step 1: Enable GitHub Pages
1. Go to your repository: `https://github.com/puneethkotha/Research-Data`
2. Click on **Settings** tab
3. Scroll down to **Pages** section
4. Under **Source**, select **GitHub Actions**
5. Save the settings

### Step 2: Push Your Code
The GitHub Actions workflow will automatically deploy your site when you push to the main branch.

### Step 3: Access Your Site
Your site will be available at:
`https://puneethkotha.github.io/Research-Data/`

## What Changed for GitHub Pages

### ✅ **Static File Loading**
- Modified JavaScript to load CSV files directly from GitHub raw URLs
- No server required - works with static hosting
- Files are loaded from: `https://raw.githubusercontent.com/puneethkotha/Research-Data/main/August/`

### ✅ **Automatic Deployment**
- GitHub Actions workflow included
- Deploys automatically on every push to main branch
- No manual deployment needed

### ✅ **Free Hosting**
- Completely free with GitHub Pages
- No Railway costs
- Reliable GitHub infrastructure

## Benefits of GitHub Pages vs Railway

| Feature | GitHub Pages | Railway |
|---------|-------------|---------|
| **Cost** | Free | Free tier available |
| **Setup** | Simple | Requires configuration |
| **Static Sites** | Perfect | Overkill for static |
| **Custom Domain** | Supported | Supported |
| **SSL** | Automatic | Automatic |
| **Deployment** | Auto on push | Auto on push |

## Custom Domain (Optional)
If you want a custom domain like `research-data.yourdomain.com`:
1. Add a `CNAME` file to your repository root
2. Add your domain to GitHub Pages settings
3. Configure DNS with your domain provider

## Troubleshooting
- If the site doesn't load, check the Actions tab for deployment errors
- CSV files should load from raw GitHub URLs
- All animations and interactions work the same as Railway
