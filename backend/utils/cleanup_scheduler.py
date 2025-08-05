import schedule
import time
import logging
from threading import Thread
from datetime import datetime
from .database_manager import DatabaseManager

logger = logging.getLogger(__name__)

class CleanupScheduler:
    """
    Automated cleanup scheduler for TTL data management
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.is_running = False
        self.scheduler_thread = None
        
    def start_scheduler(self):
        """Start the cleanup scheduler"""
        if self.is_running:
            logger.warning("Cleanup scheduler is already running")
            return
        
        # Schedule cleanup tasks
        schedule.every(1).hours.do(self._run_cleanup)  # Every hour
        schedule.every().day.at("02:00").do(self._run_deep_cleanup)  # Daily at 2 AM
        schedule.every().week.do(self._run_maintenance)  # Weekly maintenance
        
        self.is_running = True
        self.scheduler_thread = Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("Cleanup scheduler started")
    
    def stop_scheduler(self):
        """Stop the cleanup scheduler"""
        self.is_running = False
        schedule.clear()
        logger.info("Cleanup scheduler stopped")
    
    def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Scheduler error: {str(e)}")
                time.sleep(60)
    
    def _run_cleanup(self):
        """Run regular cleanup"""
        try:
            logger.info("Starting regular cleanup...")
            stats = self.db_manager.cleanup_expired_data()
            logger.info(f"Regular cleanup completed: {stats}")
        except Exception as e:
            logger.error(f"Regular cleanup failed: {str(e)}")
    
    def _run_deep_cleanup(self):
        """Run deep cleanup with additional maintenance"""
        try:
            logger.info("Starting deep cleanup...")
            stats = self.db_manager.cleanup_expired_data()
            
            # Additional deep cleanup tasks
            db_stats = self.db_manager.get_database_stats()
            logger.info(f"Deep cleanup completed: {stats}, DB stats: {db_stats}")
        except Exception as e:
            logger.error(f"Deep cleanup failed: {str(e)}")
    
    def _run_maintenance(self):
        """Run weekly maintenance tasks"""
        try:
            logger.info("Starting weekly maintenance...")
            
            # Run cleanup
            stats = self.db_manager.cleanup_expired_data()
            
            # Log maintenance completion
            logger.info(f"Weekly maintenance completed: {stats}")
            
        except Exception as e:
            logger.error(f"Weekly maintenance failed: {str(e)}")

def create_cleanup_scheduler(db_manager: DatabaseManager):
    """Factory function to create cleanup scheduler"""
    return CleanupScheduler(db_manager)
