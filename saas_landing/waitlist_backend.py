"""
Enhanced waitlist backend with better error handling and features
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
import json
import os
import logging
from typing import Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Autonomy Tracker - Waitlist API",
    description="Waitlist collection API for SaaS landing page",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

WAITLIST_FILE = os.getenv("WAITLIST_FILE", "waitlist.json")
MAX_ENTRIES = int(os.getenv("MAX_WAITLIST_ENTRIES", "10000"))

class WaitlistEntry(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    company: Optional[str] = None
    source: Optional[str] = "landing_page"
    
    @validator('name')
    def validate_name(cls, v):
        if v and len(v) > 100:
            raise ValueError("Name must be less than 100 characters")
        return v
    
    @validator('company')
    def validate_company(cls, v):
        if v and len(v) > 100:
            raise ValueError("Company must be less than 100 characters")
        return v

class WaitlistResponse(BaseModel):
    success: bool
    message: str
    position: Optional[int] = None
    total: Optional[int] = None

def load_waitlist():
    """Load existing waitlist"""
    try:
        if os.path.exists(WAITLIST_FILE):
            with open(WAITLIST_FILE, "r") as f:
                data = json.load(f)
                return data
        return {"entries": [], "total": 0, "created_at": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Error loading waitlist: {e}")
        return {"entries": [], "total": 0, "created_at": datetime.now().isoformat()}

def save_waitlist(data):
    """Save waitlist to file"""
    try:
        data["updated_at"] = datetime.now().isoformat()
        with open(WAITLIST_FILE, "w") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Waitlist saved: {data['total']} entries")
    except Exception as e:
        logger.error(f"Error saving waitlist: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save waitlist"
        )

def is_email_duplicate(email: str, entries: list) -> bool:
    """Check if email already exists"""
    return any(entry.get("email", "").lower() == email.lower() for entry in entries)

@app.get("/")
async def root():
    """Root endpoint"""
    waitlist_data = load_waitlist()
    return {
        "service": "AI Autonomy Tracker Waitlist API",
        "status": "running",
        "version": "1.0.0",
        "waitlist_count": waitlist_data.get("total", 0)
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/waitlist", response_model=WaitlistResponse, status_code=status.HTTP_201_CREATED)
async def add_to_waitlist(entry: WaitlistEntry):
    """
    Add email to waitlist
    
    - **email**: Email address (required)
    - **name**: Name (optional)
    - **company**: Company name (optional)
    - **source**: Source of signup (optional, default: landing_page)
    """
    try:
        waitlist_data = load_waitlist()
        entries = waitlist_data.get("entries", [])
        
        # Check for duplicates
        if is_email_duplicate(entry.email, entries):
            logger.warning(f"Duplicate email attempt: {entry.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check max entries
        if len(entries) >= MAX_ENTRIES:
            logger.warning("Waitlist at maximum capacity")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Waitlist is full"
            )
        
        # Add entry
        new_entry = {
            "email": entry.email,
            "name": entry.name,
            "company": entry.company,
            "source": entry.source,
            "added_at": datetime.now().isoformat()
        }
        
        entries.append(new_entry)
        waitlist_data["entries"] = entries
        waitlist_data["total"] = len(entries)
        
        save_waitlist(waitlist_data)
        
        logger.info(f"New waitlist entry: {entry.email} (Position: {len(entries)})")
        
        return WaitlistResponse(
            success=True,
            message="Successfully added to waitlist",
            position=len(entries),
            total=len(entries)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding to waitlist: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add to waitlist"
        )

@app.get("/waitlist/stats")
async def get_waitlist_stats():
    """Get waitlist statistics (admin endpoint)"""
    try:
        waitlist_data = load_waitlist()
        entries = waitlist_data.get("entries", [])
        
        # Calculate stats
        sources = {}
        for entry in entries:
            source = entry.get("source", "unknown")
            sources[source] = sources.get(source, 0) + 1
        
        return {
            "total": len(entries),
            "sources": sources,
            "created_at": waitlist_data.get("created_at"),
            "updated_at": waitlist_data.get("updated_at")
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get statistics"
        )

@app.get("/waitlist/count")
async def get_waitlist_count():
    """Get waitlist count (public endpoint)"""
    try:
        waitlist_data = load_waitlist()
        return {
            "count": waitlist_data.get("total", 0),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting count: {e}")
        return {"count": 0, "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
