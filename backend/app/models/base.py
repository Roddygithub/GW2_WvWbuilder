from sqlalchemy.ext.declarative import declarative_base

# Create a base class for all models
Base = declarative_base()

# This allows us to use Base in other modules without circular imports
