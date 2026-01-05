import sqlite3
import os

# Database path
db_path = os.path.join('instance', 'pregnancy_care.db')

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("🗑️ Clearing database content data...")
print("=" * 60)

# Tables to clear (all content data, keeping only users)
tables_to_clear = [
    'babies',
    'vaccinations',
    'growth_records',
    'nutrition_records',
    'sleep_records',
    'appointments',
    'nutrition_content',
    'vaccination_schedules',
    'faqs',
    'government_schemes',
    'unique_id_history',
    'exercises',
    'meditation_content',
    'wellness_tips',
    'medical_reports',
    'weight_entries'
]

# Clear each table
for table in tables_to_clear:
    try:
        cursor.execute(f"DELETE FROM {table}")
        deleted_count = cursor.rowcount
        print(f"✅ Cleared {table}: {deleted_count} records deleted")
    except sqlite3.Error as e:
        print(f"❌ Error clearing {table}: {e}")

# Commit changes
conn.commit()

# Show remaining data
print("\n" + "=" * 60)
print("📊 Remaining data in database:")
print("=" * 60)

cursor.execute("SELECT COUNT(*) FROM users")
user_count = cursor.fetchone()[0]
print(f"Users: {user_count} accounts")

cursor.execute("SELECT email, role FROM users")
users = cursor.fetchall()
for email, role in users:
    print(f"  - {email} ({role})")

conn.close()
print("\n✅ Database cleanup completed!")
print("✅ Only user accounts remain in the database")
print("=" * 60)
