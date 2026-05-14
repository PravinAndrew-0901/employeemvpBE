import sys
import os

from db.database import engine, Base
from db.models import *
import db.seed as seed
import create_admin

print("Dropping all tables to sync schema...")
Base.metadata.drop_all(bind=engine)
print("Tables dropped.")

print("Recreating tables and seeding...")
seed.seed_db()
create_admin.create()
print("Database reset successfully! You can now use all new fields.")
