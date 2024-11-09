import psycopg2

try:
    conn = psycopg2.connect(
        dbname="radius",
        user="radius",
        password="your_password",
        host="192.168.11.105",
        port="5432"
    )
    print("Connection successful!")
    conn.close()
except psycopg2.OperationalError as e:
    print("OperationalError:", e)
except Exception as e:
    print("Error:", e)