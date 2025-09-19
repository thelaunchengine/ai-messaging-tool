#!/usr/bin/env python3

"""
OPTIMIZED SCRAPING SYSTEM
Implements all the performance fixes to prevent 19-minute delays
"""

import asyncio
import time
import logging
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timedelta
import psutil
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ScrapingConfig:
    """Configuration for optimized scraping"""
    MAX_BATCH_SIZE: int = 15  # Reduced from 44 to 15
    MAX_CONCURRENT_WEBSITES: int = 10  # Process 10 websites simultaneously
    TIMEOUT_PER_WEBSITE: int = 300  # 5 minutes max per website
    RESOURCE_CHECK_INTERVAL: int = 30  # Check resources every 30 seconds
    MAX_CPU_USAGE: float = 80.0  # Max 80% CPU usage
    MAX_MEMORY_USAGE: float = 85.0  # Max 85% memory usage
    MAX_DB_CONNECTIONS: int = 20  # Max database connections

class ResourceMonitor:
    """Monitor system resources and enforce limits"""
    
    def __init__(self, config: ScrapingConfig):
        self.config = config
        self.lock = threading.Lock()
        self.current_tasks = 0
        self.start_time = time.time()
        
    def check_resources(self) -> bool:
        """Check if system has enough resources"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent
            
            with self.lock:
                if cpu_percent > self.config.MAX_CPU_USAGE:
                    logger.warning(f"⚠️  CPU usage too high: {cpu_percent}% > {self.config.MAX_CPU_USAGE}%")
                    return False
                    
                if memory_percent > self.config.MAX_MEMORY_USAGE:
                    logger.warning(f"⚠️  Memory usage too high: {memory_percent}% > {self.config.MAX_MEMORY_USAGE}%")
                    return False
                    
                if self.current_tasks >= self.config.MAX_CONCURRENT_WEBSITES:
                    logger.warning(f"⚠️  Too many concurrent tasks: {self.current_tasks} >= {self.config.MAX_CONCURRENT_WEBSITES}")
                    return False
                    
                return True
                
        except Exception as e:
            logger.error(f"Error checking resources: {e}")
            return False
    
    def start_task(self):
        """Mark a task as started"""
        with self.lock:
            self.current_tasks += 1
            logger.info(f"🚀 Task started. Current tasks: {self.current_tasks}")
    
    def end_task(self):
        """Mark a task as completed"""
        with self.lock:
            self.current_tasks = max(0, self.current_tasks - 1)
            logger.info(f"✅ Task completed. Current tasks: {self.current_tasks}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current resource statistics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": memory.available / (1024**3),
                "current_tasks": self.current_tasks,
                "max_concurrent": self.config.MAX_CONCURRENT_WEBSITES,
                "uptime_seconds": time.time() - self.start_time
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}

class OptimizedScraper:
    """Optimized website scraper with parallel processing and resource management"""
    
    def __init__(self, config: ScrapingConfig):
        self.config = config
        self.resource_monitor = ResourceMonitor(config)
        self.executor = ThreadPoolExecutor(max_workers=config.MAX_CONCURRENT_WEBSITES)
        self.active_tasks = {}
        
    def scrape_websites_optimized(self, websites: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Scrape websites with optimized parallel processing
        
        Args:
            websites: List of website dictionaries
            
        Returns:
            Dictionary with results and statistics
        """
        start_time = time.time()
        total_websites = len(websites)
        
        logger.info(f"🚀 Starting optimized scraping for {total_websites} websites")
        logger.info(f"📊 Configuration: Max batch size={self.config.MAX_BATCH_SIZE}, Max concurrent={self.config.MAX_CONCURRENT_WEBSITES}")
        
        # Split into smaller batches
        batches = self._split_into_batches(websites)
        logger.info(f"📦 Split into {len(batches)} batches of max {self.config.MAX_BATCH_SIZE} websites")
        
        results = {
            "total_websites": total_websites,
            "batches_processed": 0,
            "websites_completed": 0,
            "websites_failed": 0,
            "total_time": 0,
            "average_time_per_website": 0,
            "resource_usage": [],
            "errors": []
        }
        
        # Process batches sequentially but websites within batches in parallel
        for batch_num, batch in enumerate(batches, 1):
            logger.info(f"📦 Processing batch {batch_num}/{len(batches)} with {len(batch)} websites")
            
            batch_start = time.time()
            batch_results = self._process_batch_parallel(batch, batch_num)
            
            # Update results
            results["batches_processed"] += 1
            results["websites_completed"] += batch_results["completed"]
            results["websites_failed"] += batch_results["failed"]
            results["errors"].extend(batch_results["errors"])
            
            # Record resource usage
            stats = self.resource_monitor.get_stats()
            stats["batch_number"] = batch_num
            stats["batch_size"] = len(batch)
            stats["batch_time"] = time.time() - batch_start
            results["resource_usage"].append(stats)
            
            logger.info(f"✅ Batch {batch_num} completed in {time.time() - batch_start:.2f}s")
            logger.info(f"📊 Progress: {results['websites_completed']}/{total_websites} completed")
            
            # Check if we need to pause for resource recovery
            if not self.resource_monitor.check_resources():
                logger.warning("⚠️  Pausing for resource recovery...")
                time.sleep(10)  # Wait 10 seconds for resources to recover
        
        # Calculate final statistics
        total_time = time.time() - start_time
        results["total_time"] = total_time
        results["average_time_per_website"] = total_time / total_websites if total_websites > 0 else 0
        
        logger.info(f"🎉 Scraping completed in {total_time:.2f}s")
        logger.info(f"📊 Final stats: {results['websites_completed']} completed, {results['websites_failed']} failed")
        logger.info(f"⚡ Average time per website: {results['average_time_per_website']:.2f}s")
        
        return results
    
    def _split_into_batches(self, websites: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Split websites into smaller batches"""
        batches = []
        for i in range(0, len(websites), self.config.MAX_BATCH_SIZE):
            batch = websites[i:i + self.config.MAX_BATCH_SIZE]
            batches.append(batch)
        return batches
    
    def _process_batch_parallel(self, batch: List[Dict[str, Any]], batch_num: int) -> Dict[str, Any]:
        """Process a batch of websites in parallel"""
        batch_results = {
            "completed": 0,
            "failed": 0,
            "errors": [],
            "start_time": time.time()
        }
        
        # Submit all websites in the batch to the thread pool
        future_to_website = {}
        for website in batch:
            if self.resource_monitor.check_resources():
                future = self.executor.submit(self._scrape_single_website, website, batch_num)
                future_to_website[future] = website
                self.resource_monitor.start_task()
            else:
                logger.warning(f"⚠️  Skipping website {website.get('websiteUrl', 'Unknown')} due to resource constraints")
                batch_results["failed"] += 1
                batch_results["errors"].append(f"Resource constraint: {website.get('websiteUrl', 'Unknown')}")
        
        # Collect results as they complete
        for future in as_completed(future_to_website):
            website = future_to_website[future]
            try:
                result = future.result(timeout=self.config.TIMEOUT_PER_WEBSITE)
                if result["success"]:
                    batch_results["completed"] += 1
                    logger.info(f"✅ Website {website.get('websiteUrl', 'Unknown')} completed in {result['time_taken']:.2f}s")
                else:
                    batch_results["failed"] += 1
                    batch_results["errors"].append(f"{website.get('websiteUrl', 'Unknown')}: {result['error']}")
                    logger.error(f"❌ Website {website.get('websiteUrl', 'Unknown')} failed: {result['error']}")
            except Exception as e:
                batch_results["failed"] += 1
                batch_results["errors"].append(f"{website.get('websiteUrl', 'Unknown')}: {str(e)}")
                logger.error(f"❌ Website {website.get('websiteUrl', 'Unknown')} exception: {e}")
            finally:
                self.resource_monitor.end_task()
        
        batch_results["end_time"] = time.time()
        batch_results["total_time"] = batch_results["end_time"] - batch_results["start_time"]
        
        return batch_results
    
    def _scrape_single_website(self, website: Dict[str, Any], batch_num: int) -> Dict[str, Any]:
        """
        Scrape a single website with timeout and resource monitoring
        
        Args:
            website: Website dictionary
            batch_num: Current batch number
            
        Returns:
            Dictionary with scraping results
        """
        start_time = time.time()
        website_url = website.get('websiteUrl', 'Unknown')
        
        try:
            logger.info(f"🌐 Scraping website {website_url} (Batch {batch_num})")
            
            # Simulate the actual scraping work (replace with real scraping logic)
            # This is where the real scraping would happen
            scraped_data = self._simulate_scraping(website_url)
            
            # Check timeout
            time_taken = time.time() - start_time
            if time_taken > self.config.TIMEOUT_PER_WEBSITE:
                raise TimeoutError(f"Scraping took {time_taken:.2f}s, exceeded timeout of {self.config.TIMEOUT_PER_WEBSITE}s")
            
            return {
                "success": True,
                "website_url": website_url,
                "scraped_data": scraped_data,
                "time_taken": time_taken,
                "batch_number": batch_num
            }
            
        except Exception as e:
            time_taken = time.time() - start_time
            logger.error(f"❌ Error scraping {website_url}: {e}")
            
            return {
                "success": False,
                "website_url": website_url,
                "error": str(e),
                "time_taken": time_taken,
                "batch_number": batch_num
            }
    
    def _simulate_scraping(self, website_url: str) -> Dict[str, Any]:
        """
        Simulate website scraping (replace with real implementation)
        
        Args:
            website_url: URL to scrape
            
        Returns:
            Simulated scraped data
        """
        # Simulate different processing times based on website complexity
        import random
        
        # Simulate actual scraping work
        time.sleep(random.uniform(0.5, 2.0))  # 0.5 to 2 seconds
        
        # Simulate extracted data
        return {
            "company_name": f"Company from {website_url}",
            "industry": "Technology",
            "business_type": "Enterprise",
            "about_us_content": f"About us content from {website_url}",
            "contact_form_url": f"{website_url}/contact",
            "has_contact_form": True,
            "scraped_at": datetime.now().isoformat()
        }
    
    def shutdown(self):
        """Clean shutdown of the scraper"""
        logger.info("🔄 Shutting down optimized scraper...")
        self.executor.shutdown(wait=True)
        logger.info("✅ Optimized scraper shutdown complete")

def main():
    """Test the optimized scraping system"""
    config = ScrapingConfig()
    scraper = OptimizedScraper(config)
    
    try:
        # Create test websites
        test_websites = [
            {"id": f"test_{i}", "websiteUrl": f"https://example{i}.com"} 
            for i in range(1, 26)  # 25 websites to test batching
        ]
        
        logger.info("🧪 Testing optimized scraping system...")
        results = scraper.scrape_websites_optimized(test_websites)
        
        # Print results
        logger.info("📊 Test Results:")
        logger.info(f"Total websites: {results['total_websites']}")
        logger.info(f"Batches processed: {results['batches_processed']}")
        logger.info(f"Websites completed: {results['websites_completed']}")
        logger.info(f"Websites failed: {results['websites_failed']}")
        logger.info(f"Total time: {results['total_time']:.2f}s")
        logger.info(f"Average time per website: {results['average_time_per_website']:.2f}s")
        
        # Print resource usage
        logger.info("📈 Resource Usage:")
        for usage in results['resource_usage']:
            logger.info(f"Batch {usage['batch_number']}: CPU {usage['cpu_percent']}%, "
                       f"Memory {usage['memory_percent']}%, "
                       f"Tasks {usage['current_tasks']}/{usage['max_concurrent']}")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
    finally:
        scraper.shutdown()

if __name__ == "__main__":
    main()
