# Quick Start Guide
## AI Decision Engine Project

### 🚀 Get Started in 5 Minutes

#### 1. Check Current Status
```bash
python update_progress.py
```

#### 2. Run the Main System
```bash
python run_system.py
```
This will:
- Evaluate income strategies
- Show top recommended strategies
- Initialize the system

#### 3. Test the API (API_SERVICES Strategy)

**Option A: Quick Start (Windows)**
```bash
scripts\run_all.bat
```
This starts API, waitlist backend, and opens landing page.

**Option B: Manual Start**
```bash
cd api
pip install -r requirements.txt
python main.py
```

**In another terminal, test the API:**
```bash
cd api
python test_api.py
```

**Option C: Run All Tests**
```bash
scripts\test_all.bat
```

**Access API docs:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

#### 4. View Landing Page (SAAS_PRODUCT Strategy)

**Start waitlist backend:**
```bash
cd saas_landing
python waitlist_backend.py
```

**View landing page:**
- Open `saas_landing/index.html` in browser
- Or use: `python -m http.server 3000` then visit http://localhost:3000

#### 5. Generate a Tweet
```bash
python autonomous_tweet_scheduler.py
```

#### 6. View Dashboard
```bash
# Generate dashboard data
python analytics/dashboard_data.py

# Open dashboard (after generating data)
# Open analytics/simple_dashboard.html in browser
```

#### 7. Check System Health
```bash
python monitor_system.py
```

#### 8. Generate Report
```bash
python generate_report.py
```

#### 9. Test API Server
```bash
# Start API and test
scripts\start_and_test_api.bat

# Or test components only
python api\test_local.py
```

#### 10. Deploy Resources
- **One-Click Deploy**: `scripts\one_click_deploy.bat` ⭐ EASIEST!
- **Full Auto**: `scripts\full_auto_deploy.bat`
- **Docker**: `scripts\deploy_docker.bat`
- See `AUTOMATION_GUIDE.md` for all options
- See `DEPLOYMENT_CHECKLIST.md` for full guide

---

### 📁 Project Structure

```
ai-decision-engine-api/
├── START_HERE.md ⭐ (Read first!)
├── PROGRESS_STATUS.json ⭐ (Current state)
├── README.md (Master documentation)
│
├── api/ (API_SERVICES strategy)
│   ├── main.py (FastAPI server)
│   ├── api_specification.yaml
│   ├── test_api.py
│   └── requirements.txt
│
├── saas_landing/ (SAAS_PRODUCT strategy)
│   ├── index.html (Landing page)
│   └── waitlist_backend.py
│
├── Core Systems
│   ├── ai_decision_engine.py
│   ├── income_strategies.py
│   ├── ai_memory_system.py
│   └── autonomy_tracker.py
│
└── Documentation
    ├── strategy_implementation_plan.md
    ├── DEPLOYMENT_GUIDE.md
    └── IMPLEMENTATION_SUMMARY.md
```

---

### 🎯 Current Work Status

**API_SERVICES**: 90% Complete
- ✅ Specification done
- ✅ Implementation done
- ✅ Tests ready
- ⏳ Next: Test locally → Deploy

**SAAS_PRODUCT**: 70% Complete
- ✅ Landing page done
- ✅ Waitlist backend done
- ⏳ Next: Deploy → Market

---

### 🔧 Common Commands

```bash
# Check progress
python update_progress.py

# Run main system
python run_system.py

# Check memory
python check_memory.py

# Generate tweet
python autonomous_tweet_scheduler.py

# Test API
cd api && python test_api.py

# Run API server
cd api && python main.py
```

---

### 📊 System Status

- **Phase**: 1 - Foundation
- **AI Autonomy**: 77.4%
- **Status**: OPERATIONAL ✅
- **Strategies Active**: 2 (API_SERVICES, SAAS_PRODUCT)

---

### 🆘 Need Help?

1. Read `START_HERE.md` for orientation
2. Check `PROGRESS_STATUS.json` for current state
3. See `README.md` for full documentation
4. Check `DEPLOYMENT_GUIDE.md` for deployment help

---

**Last Updated**: October 30, 2025

