FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .
COPY ../ai_decision_engine.py ../ai_decision_engine.py
COPY ../ai_memory_system.py ../ai_memory_system.py
COPY ../autonomy_tracker.py ../autonomy_tracker.py

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
