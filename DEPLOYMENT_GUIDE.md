# Deployment Guide
## AI Decision Engine - Deployment Instructions

### API_SERVICES - AI Decision Engine API

#### Local Development

1. **Install Dependencies**
   ```bash
   cd api
   pip install -r requirements.txt
   ```

2. **Run API Server**
   ```bash
   # Windows
   run_api.bat
   
   # Or directly
   python main.py
   
   # Or with uvicorn
   uvicorn main:app --reload --port 8000
   ```

3. **Test API**
   ```bash
   python test_api.py
   ```

4. **Access API Docs**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

#### Production Deployment

**Option 1: Vercel/Netlify Functions**
- Deploy as serverless functions
- Configure API routes
- Set environment variables

**Option 2: AWS/GCP Cloud**
- Deploy to EC2/Compute Engine
- Use API Gateway for routing
- Set up auto-scaling

**Option 3: Docker Container**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Steps:**
1. Set up production database for API keys
2. Configure environment variables
3. Set up SSL/TLS certificates
4. Configure rate limiting
5. Set up monitoring and logging
6. Deploy to production server

---

### SAAS_PRODUCT - Landing Page

#### Local Development

1. **Run Waitlist Backend**
   ```bash
   cd saas_landing
   python waitlist_backend.py
   ```
   Backend runs on: http://localhost:8001

2. **View Landing Page**
   - Open `index.html` in browser
   - Or use a local server:
   ```bash
   # Python
   python -m http.server 3000
   
   # Node.js
   npx serve
   ```

#### Production Deployment

**Option 1: Netlify (Recommended)**
1. Connect GitHub repository
2. Deploy `saas_landing/` folder
3. Set up custom domain
4. Configure environment variables

**Option 2: Vercel**
1. Install Vercel CLI: `npm i -g vercel`
2. Run `vercel` in `saas_landing/` folder
3. Follow prompts

**Option 3: Static Hosting**
- Upload to AWS S3 + CloudFront
- Upload to GitHub Pages
- Upload to any static host

**Backend Deployment:**
1. Deploy `waitlist_backend.py` as API service
2. Update landing page API URL to production
3. Set up database for waitlist (replace JSON file)
4. Configure CORS for production domain

---

### Environment Variables

#### API Service
```env
API_ENV=production
DATABASE_URL=postgresql://...
JWT_SECRET=your_secret_key
API_RATE_LIMIT=1000
```

#### Waitlist Service
```env
WAITLIST_DB_URL=postgresql://...
EMAIL_SERVICE_API_KEY=your_key
```

---

### Post-Deployment Checklist

- [ ] Test all endpoints
- [ ] Verify authentication works
- [ ] Check rate limiting
- [ ] Monitor error logs
- [ ] Set up alerts
- [ ] Configure backup system
- [ ] Update documentation
- [ ] Create API keys for testing
- [ ] Set up analytics
- [ ] Configure SSL certificates

---

### Next Steps After Deployment

1. **API_SERVICES:**
   - List on RapidAPI marketplace
   - Post on ProductHunt
   - Developer outreach
   - Create tutorial content

2. **SAAS_PRODUCT:**
   - Launch landing page
   - Start marketing campaign
   - Post on IndieHackers
   - Social media promotion
   - Begin MVP development

---

*Last Updated: October 30, 2025*
