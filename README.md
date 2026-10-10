# 🚀 AI Decision Engine API

> AI-driven decision-making framework for autonomous systems

[![Status](https://img.shields.io/badge/status-production--ready-brightgreen)](https://github.com)
[![Version](https://img.shields.io/badge/version-1.0.0-blue)](https://github.com)
[![Python](https://img.shields.io/badge/python-3.11+-blue)](https://python.org)

---

## 📋 Overview

The AI Decision Engine API provides a comprehensive RESTful API for AI-driven decision-making, risk assessment, and autonomy tracking. Built with FastAPI, it's designed for developers building autonomous AI systems.

### Key Features

- ✅ **18+ API Endpoints** - Complete decision-making framework
- ✅ **Authentication** - API key-based security with tiered access
- ✅ **Analytics** - Real-time usage tracking and metrics
- ✅ **Documentation** - Interactive API documentation
- ✅ **Dashboard** - Web-based user interface
- ✅ **Production Ready** - Fully tested and deployment-ready

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone <repository-url>
cd ai-decision-engine-api

# Install dependencies
pip install -r api/requirements.txt
```

### Start Server

```bash
cd api
uvicorn main:app --reload
```

### Access Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Get API Key

```bash
python api/manage_api_keys.py generate pro
```

### Test API

```bash
python api/test_api.py
```

---

## 📚 Documentation

- **[API Documentation](api/README.md)** - Complete API reference
- **[Integration Guide](api/INTEGRATION_GUIDE.md)** - How to integrate
- **[Deployment Guide](DEPLOYMENT_GUIDE.md)** - Deploy to production
- **[Operational Runbook](OPERATIONAL_RUNBOOK.md)** - Operations guide
- **[Changelog](CHANGELOG.md)** - Version history
- **[Roadmap](ROADMAP.md)** - Future plans

---

## 🏗️ Project Structure

```
ai-decision-engine-api/
├── api/                    # API backend
│   ├── main.py            # FastAPI application
│   ├── api_key_manager.py # Authentication
│   ├── analytics.py       # Analytics
│   └── ...
├── docs/                  # API documentation
├── saas_landing/         # Landing page
├── scripts/              # Automation scripts
├── examples/             # Integration examples
└── .github/workflows/    # CI/CD
```

---

## 🔑 API Endpoints

### Core Endpoints

- `GET /health` - Health check
- `POST /decisions/evaluate` - Evaluate decisions
- `POST /risk/assess` - Risk assessment
- `GET /autonomy/level` - Get autonomy level
- `POST /autonomy/should-execute` - Auto-execute check
- `POST /memory/insights` - Memory insights

### Analytics Endpoints

- `GET /analytics/stats` - Usage statistics
- `GET /analytics/endpoints` - Top endpoints
- `GET /analytics/performance` - Performance metrics

### Key Management

- `GET /api/keys/list` - List API keys
- `POST /api/keys/generate` - Generate new key
- `POST /api/keys/deactivate` - Deactivate key

See [API Documentation](api/README.md) for complete reference.

---

## 💻 Integration Examples

### Python

```python
import requests

headers = {
    "X-API-Key": "YOUR_API_KEY",
    "Content-Type": "application/json"
}

response = requests.post(
    "https://api.example.com/decisions/evaluate",
    json={"category": "FINANCIAL", "amount": 1000},
    headers=headers
)
```

### JavaScript

```javascript
const response = await fetch('https://api.example.com/decisions/evaluate', {
    method: 'POST',
    headers: {
        'X-API-Key': 'YOUR_API_KEY',
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        category: 'FINANCIAL',
        amount: 1000
    })
});
```

More examples in [examples/](examples/) directory.

---

## 🛠️ Tools & Scripts

### CLI Tools

- `api/manage_api_keys.py` - API key management
- `api/analytics_dashboard.py` - Analytics viewer
- `scripts/prepare_launch.py` - Launch readiness check
- `scripts/deploy_automated.py` - Deployment automation

### Web Interfaces

- User Dashboard: `dashboard/index.html`
- API Docs: `docs/index.html`
- Status Page: `status_page.html`

---

## 🧪 Testing

```bash
# Run all tests
python api/test_api.py
python api/test_comprehensive.py

# Check code quality
python scripts/check_code_quality.py
```

---

## 🚀 Deployment

### Quick Deploy

```bash
python scripts/deploy_automated.py <platform>
```

### Supported Platforms

- Local
- Docker
- Railway
- Heroku
- Render

See [Deployment Guide](DEPLOYMENT_GUIDE.md) for details.

---

## 📊 Project Statistics

- **Total Files**: 208+
- **Python Files**: 57
- **Lines of Code**: 9,310+
- **API Endpoints**: 18+
- **Test Coverage**: Comprehensive

---

## 🔒 Security

- API key authentication
- Rate limiting per key
- Tier-based access control
- Request tracking
- Production-ready security


---

## 📈 Roadmap

See [ROADMAP.md](ROADMAP.md) for future plans and features.

---

## 🤝 Contributing

Contributions welcome! See contributing guidelines (coming soon).

---

## 📄 License

Proprietary - All rights reserved

---

## 📞 Support

- **Documentation**: See `/docs` endpoint
- **Issues**: GitHub Issues
- **Email**: see GitHub issues

---

## 🎉 Status

**Production Ready** ✅

All core features implemented, tested, and ready for deployment.

---

*Built with ❤️ by AI Decision Engine*

*Last Updated: November 2025*

