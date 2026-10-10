# Contributing Guide
## AI Decision Engine Project

**Note**: This project is AI-driven. Most contributions will be from the AI system itself, but this guide helps understand the project structure.

---

## Project Philosophy

- **AI Autonomy**: AI makes most decisions autonomously
- **Human Oversight**: Human provides safety checkpoints only
- **Transparency**: All decisions and progress are logged
- **Continuous Learning**: System learns from outcomes

---

## Code Structure

### Core Systems
- `ai_decision_engine.py` - Decision-making framework
- `income_strategies.py` - Income generation strategies
- `ai_memory_system.py` - Memory and learning system
- `autonomy_tracker.py` - Autonomy progression tracking

### Strategies
Each strategy follows the `IncomeStrategy` base class pattern:
- `execute()` - Main execution logic
- `evaluate_opportunity()` - Opportunity assessment
- Track performance automatically

### API Service
- `api/main.py` - FastAPI server
- `api/api_specification.yaml` - OpenAPI spec
- `api/test_api.py` - Test suite

---

## Adding New Strategies

1. **Use Template**: Copy `templates/new_strategy_template.py`
2. **Implement Methods**: Fill in `execute()` and `evaluate_opportunity()`
3. **Add to IncomeManager**: Update `income_strategies.py`
4. **Test**: Run `python run_system.py`
5. **Update Progress**: Use `update_progress.py`

---

## Development Workflow

1. Read `START_HERE.md` first
2. Check `PROGRESS_STATUS.json` for current state
3. Make changes
4. Run tests: `scripts\test_all.bat`
5. Update progress: `python update_progress.py`
6. Commit changes

---

## Testing

```bash
# Run all tests
scripts\test_all.bat

# Test specific component
python monitor_system.py
python generate_report.py
```

---

## Code Style

- Follow Python PEP 8
- Use type hints
- Document all functions
- Keep functions focused
- Add comments for complex logic

---

## Progress Tracking

**Always update progress after:**
- Completing a major feature
- Fixing a bug
- Deploying to production
- Achieving a milestone

**Update method:**
```python
from update_progress import ProgressTracker
tracker = ProgressTracker()
tracker.add_accomplishment("CATEGORY", ["Item 1", "Item 2"])
tracker.save_progress()
```

---

## Documentation

When adding new features:
1. Update relevant `.md` files
2. Add to `README.md`
3. Update `PROGRESS_STATUS.json`
4. Create/update relevant README files

---

## Questions?

- Check `START_HERE.md` for orientation
- See `README.md` for full docs
- Review `QUICK_START.md` for commands

---

*This project is AI-driven. Most "contributions" come from the AI system itself as it makes autonomous decisions.*

