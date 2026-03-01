import sqlite3
import random
import datetime

def generate_mock_transactions(conn: sqlite3.Connection):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            order_date TEXT,
            amount REAL,
            tax_rate REAL,
            discount REAL,
            payment_method TEXT,
            status TEXT,
            item_count INTEGER,
            shipping_cost REAL,
            currency TEXT,
            customer_email TEXT,
            customer_country TEXT,
            is_prime INTEGER,
            fraud_score REAL,
            device_os TEXT,
            browser TEXT,
            ip_address TEXT,
            processing_time_ms INTEGER,
            last_updated_date TEXT
        )
    """)
    
    cursor.execute("SELECT count(*) FROM transactions")
    if cursor.fetchone()[0] == 0:
        print("Seeding SQLite with 1000 realistic rows for transactions table...")
        
        payment_methods = ['CREDIT', 'DEBIT', 'PAYPAL', 'CRYPTO', 'BANK_TRANSFER']
        statuses = ['COMPLETED', 'PENDING', 'FAILED', 'REFUNDED']
        currencies = ['USD', 'EUR', 'GBP', 'JPY']
        countries = ['US', 'UK', 'CA', 'AU', 'DE', 'FR', 'JP', 'IN']
        os_list = ['Windows', 'macOS', 'Linux', 'iOS', 'Android']
        browsers = ['Chrome', 'Firefox', 'Safari', 'Edge']
        
        insert_query = """
        INSERT INTO transactions (
            customer_id, order_date, amount, tax_rate, discount, payment_method, status,
            item_count, shipping_cost, currency, customer_email, customer_country,
            is_prime, fraud_score, device_os, browser, ip_address, processing_time_ms, last_updated_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=365)
        
        rows = []
        for i in range(1000):
            customer_id = random.randint(1, 500)
            
            # random date between start and end
            random_days = random.random() * 365
            order_date = start_date + datetime.timedelta(days=random_days)
            order_date_str = order_date.strftime("%Y-%m-%d %H:%M:%S")
            
            amount = round(random.uniform(10.0, 5000.0), 2)
            tax_rate = random.choice([0.0, 0.05, 0.10, 0.20])
            discount = round(random.uniform(0.0, amount * 0.3), 2)
            pm = random.choice(payment_methods)
            st = random.choice(statuses)
            item_count = random.randint(1, 20)
            shipping_cost = round(random.uniform(0.0, 50.0), 2)
            curr = random.choice(currencies)
            email = f"customer_{customer_id}@example.com"
            country = random.choice(countries)
            is_prime = random.choice([0, 1])
            fraud_score = round(random.uniform(0.0, 100.0), 2)
            d_os = random.choice(os_list)
            browser = random.choice(browsers)
            ip = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
            proc_time = random.randint(50, 3000)
            last_updated = (order_date + datetime.timedelta(hours=random.randint(1, 48))).strftime("%Y-%m-%d %H:%M:%S")
            
            # Inject some anomalies for Data Quality checks
            if random.random() < 0.02:
                amount = -amount # negative amount anomaly
            if random.random() < 0.01:
                email = None # null email anomaly
            if random.random() < 0.01:
                st = "UNKNOWN_STATUS" # invalid status anomaly
                
            rows.append((
                customer_id, order_date_str, amount, tax_rate, discount, pm, st,
                item_count, shipping_cost, curr, email, country, is_prime, fraud_score,
                d_os, browser, ip, proc_time, last_updated
            ))
            
            # execute many in chunks of 500
            if len(rows) >= 500:
                cursor.executemany(insert_query, rows)
                rows = []
                
        if rows:
            cursor.executemany(insert_query, rows)
            
        conn.commit()
        print("Completed seeding 1000 rows into transactions table.")
