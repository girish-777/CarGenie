"""
Background task scheduler for alert agent
"""
import logging
import asyncio
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.api.v1.alerts import run_alert_agent

logger = logging.getLogger(__name__)


async def run_alert_agent_task():
    """Run the alert agent as a background task"""
    logger.info("[Scheduler] Running alert agent task...")
    
    try:
        db = SessionLocal()
        try:
            result = run_alert_agent(db)
            logger.info(f"[Scheduler] Alert agent completed: {result}")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"[Scheduler] Error running alert agent: {e}")


def start_scheduler():
    """Start the background scheduler (runs every hour)"""
    logger.info("[Scheduler] Starting alert agent scheduler...")
    
    async def periodic_task():
        while True:
            try:
                await run_alert_agent_task()
            except Exception as e:
                logger.error(f"[Scheduler] Error in periodic task: {e}")
            
            # Wait 1 hour (3600 seconds) before next run
            await asyncio.sleep(3600)
    
    # Run in background
    asyncio.create_task(periodic_task())
    logger.info("[Scheduler] Scheduler started (runs every hour)")


# For manual testing or cron job execution
if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    
    db = SessionLocal()
    try:
        result = run_alert_agent(db)
        print(f"Alert agent run completed: {result}")
    finally:
        db.close()

