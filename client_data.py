import psycopg2

def create_db(conn):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients(
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(30) NOT NULL,
            last_name VARCHAR(30) NOT NULL,
            email VARCHAR(30) NOT NULL
        );
        """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS phones(
            id SERIAL PRIMARY KEY,
            client_id INTEGER,
            phone VARCHAR(20) NOT NULL,
            FOREIGN KEY (client_id) REFERENCES clients (id)
        );
        """)
    conn.commit()
    cur.close()

def add_client(conn, first_name, last_name, email, phones=None):
    cur = conn.cursor()
    cur.execute("INSERT INTO clients(first_name, last_name, email) VALUES (%s, %s, %s) RETURNING id;", (first_name, last_name, email))
    client_id = cur.fetchone()[0]
    cur.close()
    if phones:
        for phone in phones:
            add_phone(conn, client_id, phone)

def add_phone(conn, client_id, phone):
    cur = conn.cursor()
    cur.execute("INSERT INTO phones (client_id, phone) VALUES (%s, %s);", (client_id, phone))
    conn.commit()
    cur.close()

def change_client(conn, client_id, first_name=None, last_name=None, email=None, phones=None):
    cur = conn.cursor()
    if first_name:
        cur.execute("UPDATE clients SET first_name = %s WHERE id = %s;", (first_name, client_id))
    if last_name:
        cur.execute("UPDATE clients SET last_name = %s WHERE id = %s;", (last_name, client_id))
    if email:
        cur.execute("UPDATE clients SET email = %s WHERE id = %s;", (email, client_id))
    if phones:
        cur.execute("DELETE FROM phones WHERE client_id = %s;", (client_id,))
        for phone in phones:
            add_phone(conn, client_id, phone)
    conn.commit()
    cur.close()

def delete_phone(conn, client_id, phone):
    cur = conn.cursor()
    cur.execute("DELETE FROM phones WHERE client_id = %s AND phone = %s;", (client_id, phone))
    conn.commit()
    cur.close()

def delete_client(conn, client_id):
    cur = conn.cursor()
    cur.execute("DELETE FROM phones WHERE client_id = %s;", (client_id,))
    cur.execute("DELETE FROM clients WHERE id = %s;", (client_id,))
    conn.commit()
    cur.close()

def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    cur = conn.cursor()
    if first_name:
        cur.execute("SELECT clients.id, first_name, last_name, email, phone FROM clients LEFT JOIN phones ON clients.id = phones.client_id WHERE first_name = %s;", (first_name,))
    elif last_name:
        cur.execute("SELECT clients.id, first_name, last_name, email, phone FROM clients LEFT JOIN phones ON clients.id = phones.client_id WHERE last_name = %s;", (last_name,))
    elif email:
        cur.execute("SELECT clients.id, first_name, last_name, email, phone FROM clients LEFT JOIN phones ON clients.id = phones.client_id WHERE email = %s;", (email,))
    elif phone:
        cur.execute("SELECT clients.id, first_name, last_name, email, phone FROM clients JOIN phones ON clients.id = phones.client_id WHERE phone = %s;", (phone,))
    rows = cur.fetchall()
    cur.close()
    return rows

with psycopg2.connect(database="client_data", user="postgres", password="3008nikita2006") as conn:
    create_db(conn)
    add_client(conn, 'Михаил', 'Зубенко', 'mafioznik@example.com', ['+7 777 777 77 77', '+7 999 999 99 99'])
    print(find_client(conn, first_name='Михаил'))
    change_client(conn, 1, email='new_mafioznik@example.com')
    print(find_client(conn, first_name='Михаил'))
    delete_phone(conn, 1, '+7 999 999 99 99')
    print(find_client(conn, first_name='Михаил'))
    delete_client(conn, 1)
    print(find_client(conn, first_name='Михаил'))
    conn.commit()
    cur = conn.cursor()
    cur.execute("""
                    DROP TABLE IF EXISTS phones;
                    DROP TABLE IF EXISTS clients;
                    """)
    conn.commit()
conn.close()
