from contextlib import contextmanager
from typing import Generator
import app.logger as logger
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
import dotenv
import os

dotenv.load_dotenv()

# Configure logging
logger = logger.setup_logging(environment="env")

# Create declarative base for models
Base = declarative_base()

class DatabaseHandler:
    """
    A basic database handler for PostgreSQL using SQLAlchemy.
    Provides connection management, session handling, and basic operations.
    """
    
    def __init__(self):
        self.database_url = f"postgresql://{os.getenv("DATABASE_USER")}:{os.getenv("DATABASE_PASSWORD")}@{os.getenv("DATABASE_HOST")}:{os.getenv("DATABASE_PORT")}/{os.getenv("DATABASE_NAME")}"
        self.engine = None
        self.SessionLocal = None
        self._initialize_engine()
    
    def _initialize_engine(self) -> None:
        """Initialize the database engine and session factory."""
        try:
            # Create engine with connection pooling
            self.engine = create_engine(
                self.database_url,
                pool_pre_ping=True,  # Validate connections before use
                pool_recycle=300,    # Recycle connections every 5 minutes
                echo=False,          # Set to True for SQL query logging
            )
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            logger.info("[DatabaseHandler] - Database engine initialized successfully")
            logger.info(f"[DatabaseHandler] - Database connection: {self.database_url}")
            
        except SQLAlchemyError as e:
            logger.error(f"[DatabaseHandler] - Failed to initialize database engine: {e}")
            raise
    
    def create_tables(self) -> None:
        """Create all tables defined in the Base metadata."""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("[DatabaseHandler] - Database tables created successfully")
        except SQLAlchemyError as e:
            logger.error(f"[DatabaseHandler] - Failed to create tables: {e}")
            raise
    
    def drop_tables(self) -> None:
        """Drop all tables defined in the Base metadata."""
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.info("[DatabaseHandler] - Database tables dropped successfully")
        except SQLAlchemyError as e:
            logger.error(f"[DatabaseHandler] - Failed to drop tables: {e}")
            raise
    
    def get_session(self) -> Session:
        """
        Get a new database session.
        Remember to close the session when done.
        """
        return self.SessionLocal()
    
    @contextmanager
    def get_session_context(self) -> Generator[Session, None, None]:
        """
        Context manager for database sessions.
        Automatically handles session cleanup and rollback on errors.
        
        Usage:
            with db_handler.get_session_context() as session:
                # Your database operations here
                session.add(some_object)
                session.commit()
        """
        session = self.get_session()
        try:
            yield session
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def test_connection(self) -> bool:
        """
        Test the database connection.
        Returns True if connection is successful, False otherwise.
        """
        try:
            with self.get_session_context() as session:
                # Execute a simple query to test connection
                result = session.execute(text("SELECT 1"))
                result.fetchone()
                logger.info("Database connection test successful")
                return True
        except SQLAlchemyError as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def execute_raw_query(self, query: str, params: dict = None) -> list:
        """
        Execute a raw SQL query and return results.
        
        Args:
            query: SQL query string
            params: Optional parameters for the query
            
        Returns:
            List of query results
        """
        try:
            with self.get_session_context() as session:
                result = session.execute(text(query), params or {})
                return result.fetchall()
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to execute query: {e}")
            raise
    
    def close_engine(self) -> None:
        """Close the database engine and all connections."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database engine closed")

# Global database handler instance
db_handler = DatabaseHandler()

# Dependency for FastAPI
def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency to get database session.
    
    Usage in FastAPI endpoint:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            # Your database operations here
            return db.query(SomeModel).all()
    """
    with db_handler.get_session_context() as session:
        yield session
