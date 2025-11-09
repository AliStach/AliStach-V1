"""SQLite-based audit logging for security events."""

import sqlite3
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from contextlib import contextmanager
from pathlib import Path

logger = logging.getLogger(__name__)


class AuditLogger:
    """SQLite-based audit logger for security events."""
    
    def __init__(self, db_path: str = None):
        """Initialize audit logger with SQLite database."""
        # In serverless environments (Vercel), use /tmp for writable storage
        # or disable database logging if /tmp is not available
        if db_path is None:
            # Check if we're in a serverless environment
            if os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
                # Use /tmp in serverless environments
                db_path = "/tmp/audit.db"
            else:
                db_path = "audit.db"
        
        self.db_path = db_path
        self.enabled = True
        self._db_initialized = False
        # DO NOT initialize database here - wait until first use
        # This prevents filesystem operations during import
    
    def _ensure_db_directory(self):
        """Ensure database directory exists."""
        try:
            db_dir = Path(self.db_path).parent
            if db_dir and not db_dir.exists():
                db_dir.mkdir(parents=True, exist_ok=True)
        except (PermissionError, OSError) as e:
            # In read-only filesystems (some serverless environments), disable database logging
            logger.warning(f"Cannot create audit database directory: {e}. Disabling database audit logging.")
            self.enabled = False
    
    def _ensure_initialized(self):
        """Ensure database is initialized (lazy initialization - only on first use)."""
        if self._db_initialized:
            return
        
        if not self.enabled:
            return
        
        try:
            self._ensure_db_directory()
            if not self.enabled:  # Check again after _ensure_db_directory
                return
            
            self._init_database()
            self._db_initialized = True
        except Exception as e:
            logger.warning(f"Failed to initialize audit database: {e}. Disabling database audit logging.")
            self.enabled = False
            self._db_initialized = False
    
    def _init_database(self):
        """Initialize audit database schema."""
        if not self.enabled:
            logger.warning("Audit database logging is disabled (read-only filesystem)")
            return
        
        try:
            # Try to create parent directory if it doesn't exist
            db_dir = Path(self.db_path).parent
            if db_dir and not db_dir.exists():
                try:
                    db_dir.mkdir(parents=True, exist_ok=True)
                except (PermissionError, OSError):
                    # If we can't create the directory, disable logging
                    logger.warning(f"Cannot create audit database directory: {db_dir}. Disabling database audit logging.")
                    self.enabled = False
                    return
            
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    client_ip TEXT,
                    method TEXT,
                    path TEXT,
                    status_code INTEGER,
                    user_agent TEXT,
                    origin TEXT,
                    referer TEXT,
                    error_message TEXT,
                    duration_ms REAL,
                    request_body TEXT,
                    response_body TEXT,
                    security_event TEXT,
                    metadata TEXT
                )
            """)
            
            # Create indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_logs(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_client_ip ON audit_logs(client_ip)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_event_type ON audit_logs(event_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_status_code ON audit_logs(status_code)")
            
            conn.commit()
            conn.close()
            logger.info(f"Audit database initialized at {self.db_path}")
        except (PermissionError, OSError, sqlite3.Error) as e:
            logger.warning(f"Cannot initialize audit database at {self.db_path}: {e}. Disabling database audit logging.")
            self.enabled = False
        except Exception as e:
            logger.error(f"Failed to initialize audit database: {e}")
            self.enabled = False
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with context manager."""
        if not self.enabled:
            # If logging is disabled, raise an error that will be caught
            raise RuntimeError("Audit logging is disabled")
        
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            try:
                yield conn
                conn.commit()
            except Exception as e:
                conn.rollback()
                logger.error(f"Database error: {e}")
                raise
            finally:
                conn.close()
        except (PermissionError, OSError, sqlite3.Error) as e:
            # If connection fails, disable logging for future calls
            logger.warning(f"Cannot connect to audit database: {e}. Disabling database audit logging.")
            self.enabled = False
            raise RuntimeError("Audit logging is disabled") from e
    
    def log_event(
        self,
        event_type: str,
        client_ip: str,
        method: str = None,
        path: str = None,
        status_code: int = None,
        user_agent: str = None,
        origin: str = None,
        referer: str = None,
        error_message: str = None,
        duration_ms: float = None,
        request_body: Dict = None,
        response_body: Dict = None,
        security_event: str = None,
        metadata: Dict = None
    ):
        """Log a security event to the database."""
        # Lazy initialization - only initialize database on first API call
        self._ensure_initialized()
        
        if not self.enabled:
            # Database logging is disabled, skip silently
            return
        
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT INTO audit_logs (
                        timestamp, event_type, client_ip, method, path,
                        status_code, user_agent, origin, referer,
                        error_message, duration_ms, request_body,
                        response_body, security_event, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    datetime.utcnow().isoformat(),
                    event_type,
                    client_ip,
                    method,
                    path,
                    status_code,
                    user_agent,
                    origin,
                    referer,
                    error_message,
                    duration_ms,
                    json.dumps(request_body) if request_body else None,
                    json.dumps(response_body) if response_body else None,
                    security_event,
                    json.dumps(metadata) if metadata else None
                ))
        except (PermissionError, OSError, sqlite3.Error) as e:
            # If we can't write to the database, disable it for future calls
            logger.warning(f"Cannot write to audit database: {e}. Disabling database audit logging.")
            self.enabled = False
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
    
    def get_recent_events(
        self,
        limit: int = 100,
        event_type: str = None,
        client_ip: str = None,
        status_code: int = None,
        start_date: str = None,
        end_date: str = None
    ) -> List[Dict]:
        """Retrieve recent audit events with optional filters."""
        # Lazy initialization - only initialize database on first use
        self._ensure_initialized()
        
        if not self.enabled:
            return []
        
        try:
            with self._get_connection() as conn:
                query = "SELECT * FROM audit_logs WHERE 1=1"
                params = []
                
                if event_type:
                    query += " AND event_type = ?"
                    params.append(event_type)
                
                if client_ip:
                    query += " AND client_ip = ?"
                    params.append(client_ip)
                
                if status_code:
                    query += " AND status_code = ?"
                    params.append(status_code)
                
                if start_date:
                    query += " AND timestamp >= ?"
                    params.append(start_date)
                
                if end_date:
                    query += " AND timestamp <= ?"
                    params.append(end_date)
                
                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to retrieve audit events: {e}")
            return []
    
    def get_security_statistics(self, days: int = 7) -> Dict:
        """Get security statistics for the last N days."""
        # Lazy initialization - only initialize database on first use
        self._ensure_initialized()
        
        if not self.enabled:
            return {}
        
        try:
            with self._get_connection() as conn:
                start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
                
                # Total events
                total = conn.execute(
                    "SELECT COUNT(*) as count FROM audit_logs WHERE timestamp >= ?",
                    (start_date,)
                ).fetchone()['count']
                
                # Events by type
                event_types = conn.execute("""
                    SELECT event_type, COUNT(*) as count
                    FROM audit_logs
                    WHERE timestamp >= ?
                    GROUP BY event_type
                """, (start_date,)).fetchall()
                
                # Security events
                security_events = conn.execute("""
                    SELECT COUNT(*) as count
                    FROM audit_logs
                    WHERE timestamp >= ? AND security_event IS NOT NULL
                """, (start_date,)).fetchone()['count']
                
                # Blocked requests
                blocked = conn.execute("""
                    SELECT COUNT(*) as count
                    FROM audit_logs
                    WHERE timestamp >= ? AND status_code = 403
                """, (start_date,)).fetchone()['count']
                
                # Rate limited requests
                rate_limited = conn.execute("""
                    SELECT COUNT(*) as count
                    FROM audit_logs
                    WHERE timestamp >= ? AND status_code = 429
                """, (start_date,)).fetchone()['count']
                
                return {
                    'total_events': total,
                    'security_events': security_events,
                    'blocked_requests': blocked,
                    'rate_limited_requests': rate_limited,
                    'events_by_type': {row['event_type']: row['count'] for row in event_types},
                    'period_days': days
                }
        except Exception as e:
            logger.error(f"Failed to get security statistics: {e}")
            return {}
    
    def cleanup_old_logs(self, days: int = 30):
        """Remove audit logs older than N days."""
        # Lazy initialization - only initialize database on first use
        self._ensure_initialized()
        
        if not self.enabled:
            return 0
        
        try:
            cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            with self._get_connection() as conn:
                conn.execute(
                    "DELETE FROM audit_logs WHERE timestamp < ?",
                    (cutoff_date,)
                )
                deleted = conn.total_changes
            logger.info(f"Cleaned up {deleted} old audit logs")
            return deleted
        except Exception as e:
            logger.error(f"Failed to cleanup old logs: {e}")
            return 0


# Global audit logger instance (lazy initialization to prevent import-time failures)
_audit_logger_instance = None

def get_audit_logger():
    """Get or create the global audit logger instance."""
    global _audit_logger_instance
    if _audit_logger_instance is None:
        try:
            _audit_logger_instance = AuditLogger()
        except Exception as e:
            logger.warning(f"Failed to initialize audit logger: {e}. Audit logging will be disabled.")
            # Create a dummy logger that does nothing
            class DummyAuditLogger:
                def log_event(self, *args, **kwargs):
                    pass
                def get_recent_events(self, *args, **kwargs):
                    return []
                def get_security_statistics(self, *args, **kwargs):
                    return {}
                def cleanup_old_logs(self, *args, **kwargs):
                    return 0
            _audit_logger_instance = DummyAuditLogger()
    return _audit_logger_instance

# For backward compatibility, create a property-like access
class AuditLoggerProxy:
    def __getattr__(self, name):
        return getattr(get_audit_logger(), name)

audit_logger = AuditLoggerProxy()

