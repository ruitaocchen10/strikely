from pydantic import BaseModel
from enum import Enum
from typing import Optional

# Enums for controlled vocabularies                                     
                                                        
class StrikeType(str, Enum):                                                          
    JAB = "jab"                                       
    CROSS = "cross"
    HOOK = "hook"
    UPPERCUT = "uppercut"

class Hand(str, Enum):                                                                
    LEFT = "left"
    RIGHT = "right"                                                                   
                                                        
class FlagType(str, Enum):
    GUARD_DROPPED = "guard_dropped"
    CHIN_EXPOSED = "chin_exposed"                                                     
    OVEREXTENDED = "overextended"
    HIP_ROTATION_LIMITED = "hip_rotation_limited"                                     
                                                                                        
class Severity(str, Enum):
    LOW = "low"                                                                       
    MEDIUM = "medium"                                 
    HIGH = "high"

# Core data types
                                                                                        
class Strike(BaseModel):                              
    id: str
    type: StrikeType
    hand: Hand
    timestamp: float          # seconds into video
    start_frame: int                                                                  
    peak_frame: int
    end_frame: int                                                                    
                                                        
class QualityFlag(BaseModel):
    strike_id: str
    flag_type: FlagType                                                               
    severity: Severity
    description: str          # human-readable, e.g. "Guard hand dropped 15cm below chin"                                                                                 
   
# Pipeline output                                                             
                                                        
class SessionAnalysis(BaseModel):
    video_path: str
    fps: float
    frame_count: int
    duration_seconds: float
    detected_strikes: list[Strike]
    quality_flags: list[QualityFlag]                                                  
   
# Agent output                                                            
                                                        
class Issue(BaseModel):
    flag_type: FlagType
    count: int
    description: str                                                                  
    affected_strikes: list[str]   # strike ids
                                                                                        
class CoachReport(BaseModel):                         
    summary: str                                                                      
    strengths: list[str]                              
    issues: list[Issue]
    recommended_drills: list[str]