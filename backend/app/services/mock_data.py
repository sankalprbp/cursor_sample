"""
Mock Data Service
Provides mock data for demo endpoints and testing
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import random


class MockDataService:
    """Service for generating consistent mock data for demos"""
    
    def __init__(self):
        self._mock_calls = self._generate_mock_calls()
    
    def _generate_mock_calls(self) -> List[Dict[str, Any]]:
        """Generate realistic mock call data"""
        base_time = datetime.now() - timedelta(hours=2)
        
        calls = [
            {
                "id": "call_001",
                "caller_number": "+1 (555) 123-4567",
                "status": "completed",
                "direction": "inbound",
                "started_at": (base_time - timedelta(minutes=90)).isoformat() + "Z",
                "ended_at": (base_time - timedelta(minutes=87)).isoformat() + "Z",
                "duration_seconds": 180,
                "summary": "Customer inquiry about business hours and services. AI provided comprehensive information about operating hours and available services.",
                "transcript_count": 8,
                "satisfaction_score": 4.5
            },
            {
                "id": "call_002",
                "caller_number": "+1 (555) 987-6543",
                "status": "completed",
                "direction": "inbound",
                "started_at": (base_time - timedelta(minutes=60)).isoformat() + "Z",
                "ended_at": (base_time - timedelta(minutes=56)).isoformat() + "Z",
                "duration_seconds": 210,
                "summary": "Technical support request. AI agent successfully guided customer through troubleshooting steps and resolved the issue.",
                "transcript_count": 12,
                "satisfaction_score": 4.8
            },
            {
                "id": "call_003",
                "caller_number": "+1 (555) 456-7890",
                "status": "completed",
                "direction": "inbound",
                "started_at": (base_time - timedelta(minutes=30)).isoformat() + "Z",
                "ended_at": (base_time - timedelta(minutes=28)).isoformat() + "Z",
                "duration_seconds": 120,
                "summary": "Product information request. Customer asked about pricing and features. AI provided detailed product overview.",
                "transcript_count": 6,
                "satisfaction_score": 4.2
            },
            {
                "id": "call_004",
                "caller_number": "+1 (555) 321-0987",
                "status": "active",
                "direction": "inbound",
                "started_at": (base_time - timedelta(minutes=5)).isoformat() + "Z",
                "ended_at": None,
                "duration_seconds": None,
                "summary": None,
                "transcript_count": 3,
                "satisfaction_score": None
            }
        ]
        
        return calls
    
    def get_mock_calls(
        self, 
        limit: int = 50, 
        offset: int = 0, 
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get paginated mock calls with optional status filter"""
        
        calls = self._mock_calls
        
        # Apply status filter if provided
        if status:
            calls = [call for call in calls if call["status"] == status]
        
        # Apply pagination
        total = len(calls)
        paginated_calls = calls[offset:offset + limit]
        
        return {
            "calls": paginated_calls,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total
        }
    
    def get_mock_call_by_id(self, call_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific mock call by ID"""
        for call in self._mock_calls:
            if call["id"] == call_id:
                return call
        return None
    
    def get_mock_transcripts(self, call_id: str) -> List[Dict[str, Any]]:
        """Get mock transcripts for a call"""
        call = self.get_mock_call_by_id(call_id)
        if not call:
            return []
        
        # Generate mock transcripts based on call summary
        transcripts = [
            {
                "id": f"transcript_{call_id}_001",
                "speaker": "caller",
                "text": "Hello, I'm calling to ask about your business hours.",
                "timestamp": call["started_at"],
                "confidence": 0.95
            },
            {
                "id": f"transcript_{call_id}_002",
                "speaker": "ai_agent",
                "text": "Hello! I'd be happy to help you with information about our business hours. We're open Monday through Friday from 9 AM to 6 PM, and Saturday from 10 AM to 4 PM. We're closed on Sundays.",
                "timestamp": call["started_at"],
                "confidence": 1.0
            }
        ]
        
        return transcripts[:call.get("transcript_count", 2)]
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get mock system statistics"""
        return {
            "total_calls_today": 15,
            "active_calls": 2,
            "average_call_duration": 165,
            "success_rate": 0.96,
            "customer_satisfaction": 4.4,
            "response_time_avg": 2.3,
            "uptime_percentage": 99.8
        }


# Global instance
mock_data_service = MockDataService()