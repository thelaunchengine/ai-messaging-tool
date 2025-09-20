"""
Optimized database connection pool for AI Messaging Backend
"""
import os
import logging
import threading
from contextlib import contextmanager
from queue import Queue, Empty
import pg8000
from urllib.parse import urlparse
import time

logger = logging.getLogger(__name__)

class DatabaseConnectionPool:
    def __init__(self, database_url, min_connections=5, max_connections=20):
        self.database_url = database_url
        self.min_connections = min_connections
        self.max_connections = max_connections
        self.pool = Queue(maxsize=max_connections)
        self.active_connections = 0
        self.lock = threading.Lock()
        
        # Parse connection parameters
        parsed_url = urlparse(database_url)
        self.connection_params = {
            'host': parsed_url.hostname,
            'port': parsed_url.port or 5432,
            'user': parsed_url.username,
            'password': parsed_url.password,
            'database': parsed_url.path[1:] if parsed_url.path else 'aimsgdb'
        }
        
        # Initialize pool with minimum connections
        self._initialize_pool()
    
    def _create_connection(self):
        """Create a new database connection"""
        try:
            conn = pg8000.connect(**self.connection_params)
            conn.autocommit = True
            return conn
        except Exception as e:
            logger.error(f"Failed to create database connection: {e}")
            return None
    
    def _initialize_pool(self):
        """Initialize the connection pool with minimum connections"""
        for _ in range(self.min_connections):
            conn = self._create_connection()
            if conn:
                self.pool.put(conn)
                self.active_connections += 1
    
    @contextmanager
    def get_connection(self):
        """Get a connection from the pool"""
        conn = None
        try:
            # Try to get existing connection
            try:
                conn = self.pool.get_nowait()
            except Empty:
                # Create new connection if under limit
                with self.lock:
                    if self.active_connections < self.max_connections:
                        conn = self._create_connection()
                        if conn:
                            self.active_connections += 1
                        else:
                            # Fallback to waiting for existing connection
                            conn = self.pool.get(timeout=30)
                    else:
                        conn = self.pool.get(timeout=30)
            
            yield conn
            
        except Exception as e:
            logger.error(f"Error in connection pool: {e}")
            if conn:
                try:
                    conn.close()
                except:
                    pass
                with self.lock:
                    self.active_connections -= 1
            raise
        finally:
            # Return connection to pool
            if conn:
                try:
                    # Test connection before returning
                    conn.execute("SELECT 1")
                    self.pool.put(conn)
                except:
                    # Connection is bad, create new one
                    try:
                        conn.close()
                    except:
                        pass
                    with self.lock:
                        self.active_connections -= 1
                    # Add new connection to pool
                    new_conn = self._create_connection()
                    if new_conn:
                        self.pool.put(new_conn)
                        self.active_connections += 1
    
    def close_all(self):
        """Close all connections in the pool"""
        while not self.pool.empty():
            try:
                conn = self.pool.get_nowait()
                conn.close()
            except:
                pass
        self.active_connections = 0

# Global connection pool instance
_pool = None

def get_connection_pool():
    """Get the global connection pool instance"""
    global _pool
    if _pool is None:
        database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:AiMessaging2024Secure@production-ai-messaging-db.cmpkwkuqu30h.us-east-1.rds.amazonaws.com:5432/ai_messaging')
        _pool = DatabaseConnectionPool(database_url)
    return _pool

@contextmanager
def get_db_connection():
    """Get a database connection from the pool"""
    pool = get_connection_pool()
    with pool.get_connection() as conn:
        yield conn
