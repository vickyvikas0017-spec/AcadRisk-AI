import os
import logging
from contextlib import contextmanager
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session
from config import Config

logger = logging.getLogger(__name__)

Base = declarative_base()

class DatabaseManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.engine = None
        self.session_factory = None
        self.active_dialect = None
        self.is_connected = False
        self.connection_error = None
        self.initialize_engine()
        self._initialized = True

    def initialize_engine(self, custom_url=None):
        target_url = custom_url or Config.DATABASE_URL
        self.connection_error = None

        # Attempt to connect to primary MySQL
        try:
            temp_engine = create_engine(
                target_url,
                pool_pre_ping=True,
                pool_recycle=3600,
                connect_args={"connect_timeout": 3} if "mysql" in target_url else {}
            )
            with temp_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            self.engine = temp_engine
            self.active_dialect = self.engine.dialect.name
            self.is_connected = True
            logger.info(f"Successfully connected to primary database engine: {self.active_dialect}")
        except Exception as e:
            self.connection_error = str(e)
            logger.warning(f"Could not connect to primary database at {target_url}: {e}")
            if Config.ENABLE_FALLBACK and "mysql" in target_url:
                logger.info("Initializing fallback SQLite database for resilient local execution...")
                fallback_url = Config.FALLBACK_SQLITE_URL
                self.engine = create_engine(
                    fallback_url,
                    connect_args={"check_same_thread": False}
                )
                self.active_dialect = "sqlite"
                self.is_connected = True
                logger.info(f"Connected to local fallback engine: {fallback_url}")
            else:
                self.is_connected = False
                raise

        self.session_factory = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=self.engine))

    def get_session(self):
        return self.session_factory()

    @contextmanager
    def transaction(self):
        """Context manager providing atomic transaction commit and rollback."""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Transaction rolled back due to error: {e}")
            raise
        finally:
            session.close()

    def get_table_statistics(self):
        """Returns statistics for all database tables."""
        stats = []
        if not self.engine:
            return stats
        insp = inspect(self.engine)
        table_names = insp.get_table_names()
        session = self.get_session()
        try:
            for table in sorted(table_names):
                try:
                    count = session.execute(text(f"SELECT COUNT(*) FROM `{table}`" if self.active_dialect == 'mysql' else f"SELECT COUNT(*) FROM \"{table}\"")).scalar()
                except Exception:
                    count = 0
                columns = insp.get_columns(table)
                fks = insp.get_foreign_keys(table)
                indexes = insp.get_indexes(table)
                stats.append({
                    'name': table,
                    'row_count': count,
                    'column_count': len(columns),
                    'columns': [c['name'] for c in columns],
                    'foreign_keys': len(fks),
                    'index_count': len(indexes)
                })
        finally:
            session.close()
        return stats

    def explain_query(self, query_sql, params=None):
        """Safely executes EXPLAIN on a SELECT query to analyze query performance."""
        clean_query = query_sql.strip()
        if not clean_query.upper().startswith("SELECT"):
            raise ValueError("Only SELECT queries can be analyzed with EXPLAIN.")
        
        session = self.get_session()
        try:
            explain_cmd = f"EXPLAIN {clean_query}" if self.active_dialect == 'mysql' else f"EXPLAIN QUERY PLAN {clean_query}"
            result = session.execute(text(explain_cmd), params or {})
            rows = [dict(row._mapping) for row in result]
            return rows
        finally:
            session.close()

db_manager = DatabaseManager()

def get_db():
    return db_manager.get_session()

