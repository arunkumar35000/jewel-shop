"""
Helper script to migrate from SQLite to Server-Side MySQL Database.
Usage:
  python migrate_to_mysql.py
"""
import os
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Read .env file
env_file = BASE_DIR / '.env'
env_vars = {}
if env_file.exists():
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env_vars[k.strip()] = v.strip()

db_user = env_vars.get('DB_USER', 'root')
db_password = env_vars.get('DB_PASSWORD', '')
db_host = env_vars.get('DB_HOST', '127.0.0.1')
db_port = env_vars.get('DB_PORT', '3306')
db_name = env_vars.get('DB_NAME', 'jewellery_shop_db')

print("=" * 60)
print("👑 AURA JEWELLERY - SERVER-SIDE MYSQL MIGRATION UTILITY")
print("=" * 60)
print(f"Target Server : {db_host}:{db_port}")
print(f"User          : {db_user}")
print(f"Database Name : {db_name}")
print(f"Password Set? : {'YES (Length: ' + str(len(db_password)) + ')' if db_password else 'NO (BLANK)'}")
print("-" * 60)

try:
    import pymysql
    pymysql.install_as_MySQLdb()
    conn = pymysql.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        port=int(db_port),
        connect_timeout=3
    )
    print("✅ Connection to MySQL Server: SUCCESSFUL!")
    with conn.cursor() as cur:
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        print(f"✅ Database `{db_name}` is ready on MySQL!")
    conn.close()
except Exception as e:
    print(f"❌ MySQL Connection Error: {e}")
    print("\n👉 Please update 'DB_PASSWORD' in your .env file with your correct MySQL root password.")
    sys.exit(1)

print("\nStep 1: Exporting current data from SQLite to JSON...")
dump_cmd = [sys.executable, "manage.py", "dumpdata", "--natural-foreign", "--natural-primary", "-e", "contenttypes", "-e", "auth.Permission", "--indent", "2", "-o", "sqlite_data_dump.json"]
subprocess.run(dump_cmd, check=True)
print("✅ Exported sqlite_data_dump.json")

print("\nStep 2: Applying Django Migrations to MySQL...")
os.environ['DB_ENGINE'] = 'mysql'
migrate_cmd = [sys.executable, "manage.py", "migrate"]
subprocess.run(migrate_cmd, check=True)
print("✅ Tables created in MySQL!")

print("\nStep 3: Loading data into MySQL...")
load_cmd = [sys.executable, "manage.py", "loaddata", "sqlite_data_dump.json"]
subprocess.run(load_cmd, check=True)
print("✅ All data loaded into Server-Side MySQL successfully!")

print("\n" + "=" * 60)
print("🎉 CONGRATULATIONS! SERVER-SIDE MYSQL DATABASE IS NOW ACTIVE!")
print("=" * 60)

