#!/usr/bin/env python3
"""
Instagram Agent Scheduler
Schedules automatic posting at configured times using APScheduler
"""

import os
import logging
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class InstagramScheduler:
    """Manages scheduled posting to Instagram at configured times."""
    
    def __init__(self):
        """Initialize the scheduler with configuration from .env"""
        self.morning_time = os.getenv('POST_TIME_MORNING', '09:00')
        self.evening_time = os.getenv('POST_TIME_EVENING', '18:00')
        
        # Parse times (HH:MM format)
        try:
            self.morning_hour, self.morning_minute = map(int, self.morning_time.split(':'))
            self.evening_hour, self.evening_minute = map(int, self.evening_time.split(':'))
        except ValueError:
            raise ValueError(
                f"Invalid time format in .env. Expected HH:MM format.\n"
                f"POST_TIME_MORNING={self.morning_time}\n"
                f"POST_TIME_EVENING={self.evening_time}"
            )
        
        # Create background scheduler
        self.scheduler = BackgroundScheduler()
        logger.info(f"[Scheduler] Initialized with times: {self.morning_time}, {self.evening_time}")
    
    def job_wrapper(self, job_name: str):
        """Wrapper function to run the agent and handle errors.
        
        Args:
            job_name: Name of the job (Morning Post or Evening Post)
        """
        try:
            logger.info(f"\n{'='*70}")
            logger.info(f"[{job_name}] Starting scheduled post...")
            logger.info(f"{'='*70}")
            
            # Import run_agent here to avoid circular imports
            from main import run_agent
            
            success = run_agent()
            
            if success:
                logger.info(f"[{job_name}] ✓ Post completed successfully")
            else:
                logger.warning(f"[{job_name}] ⚠ Post failed or incomplete")
        
        except Exception as e:
            logger.error(f"[{job_name}] ✗ Error during scheduled post: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def schedule_jobs(self):
        """Schedule both morning and evening posting jobs."""
        # Morning post (9:00 AM by default)
        self.scheduler.add_job(
            self.job_wrapper,
            CronTrigger(hour=self.morning_hour, minute=self.morning_minute),
            args=["Morning Post"],
            id='morning_post',
            name='Morning Instagram Post',
            misfire_grace_time=600  # Allow 10 minutes grace for missed jobs
        )
        logger.info(f"[Scheduler] Scheduled morning post at {self.morning_time} daily")
        
        # Evening post (6:00 PM by default)
        self.scheduler.add_job(
            self.job_wrapper,
            CronTrigger(hour=self.evening_hour, minute=self.evening_minute),
            args=["Evening Post"],
            id='evening_post',
            name='Evening Instagram Post',
            misfire_grace_time=600
        )
        logger.info(f"[Scheduler] Scheduled evening post at {self.evening_time} daily")
    
    def get_next_run_time(self) -> dict:
        """Get the next scheduled run times.
        
        Returns:
            Dictionary with next morning and evening run times
        """
        now = datetime.now()
        
        # Calculate next morning time
        morning = now.replace(hour=self.morning_hour, minute=self.morning_minute, second=0)
        if morning <= now:
            morning = morning + timedelta(days=1)
        
        # Calculate next evening time
        evening = now.replace(hour=self.evening_hour, minute=self.evening_minute, second=0)
        if evening <= now:
            evening = evening + timedelta(days=1)
        
        return {
            'morning': morning,
            'evening': evening,
            'next': min(morning, evening)  # Whichever comes first
        }
    
    def run(self):
        """Start the scheduler and keep it running."""
        try:
            # Schedule jobs
            self.schedule_jobs()
            
            # Start scheduler
            self.scheduler.start()
            logger.info("[Scheduler] ✓ Background scheduler started")
            
            # Display next scheduled times
            next_times = self.get_next_run_time()
            logger.info(f"\n[Scheduler] Next scheduled posts:")
            logger.info(f"  Morning: {next_times['morning'].strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"  Evening: {next_times['evening'].strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"  Next run: {next_times['next'].strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            logger.info("[Scheduler] ✓ Ready. Press Ctrl+C to stop.")
            
            # Keep scheduler running
            while True:
                time.sleep(60)  # Check every 60 seconds
        
        except KeyboardInterrupt:
            logger.info("\n[Scheduler] ⚠ Scheduler interrupted by user")
            self.shutdown()
        except Exception as e:
            logger.error(f"[Scheduler] ✗ Fatal error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.shutdown()
    
    def shutdown(self):
        """Gracefully shutdown the scheduler."""
        try:
            if self.scheduler.running:
                logger.info("[Scheduler] Shutting down gracefully...")
                self.scheduler.shutdown()
                logger.info("[Scheduler] ✓ Scheduler stopped")
        except Exception as e:
            logger.error(f"[Scheduler] Error during shutdown: {e}")


def main():
    """Main entry point for the scheduler."""
    print("\n" + "=" * 70)
    print("Instagram Agent - Scheduler")
    print("=" * 70 + "\n")
    
    try:
        # Validate environment
        required_vars = [
            'GEMINI_API_KEY',
            'INSTAGRAM_ACCOUNT_ID',
            'INSTAGRAM_ACCESS_TOKEN',
            'POST_TIME_MORNING',
            'POST_TIME_EVENING'
        ]
        
        missing = []
        for var in required_vars:
            value = os.getenv(var)
            if not value or (var.startswith('GEMINI') and value.endswith('_here')):
                if not var.startswith('POST_TIME'):  # POST_TIME vars can have defaults
                    missing.append(var)
        
        if missing:
            logger.error(f"Missing environment variables: {', '.join(missing)}")
            logger.error("Please update your .env file with valid credentials")
            return False
        
        logger.info("✓ Environment validated")
        
        # Create and run scheduler
        scheduler = InstagramScheduler()
        scheduler.run()
        
        return True
    
    except ValueError as e:
        logger.error(f"Configuration Error: {e}")
        return False
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == '__main__':
    import sys
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Startup error: {e}")
        sys.exit(1)
