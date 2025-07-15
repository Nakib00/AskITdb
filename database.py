import sqlite3

connection = sqlite3.connect('student.db')

cursor = connection.cursor()

create_table_query = '''
CREATE TABLE IF NOT EXISTS students (
    NAME VARCHAR(25),
    COURSE VARCHAR(25),
    SECTION VARCHAR(25),
    MARKS INTEGER
);
'''

cursor.execute(create_table_query)

sql_query = '''
INSERT INTO students (NAME, COURSE, SECTION, MARKS) VALUES (?, ?, ?, ?);
'''
values=[
    ('Alice', 'Math', 'A', 85),
    ('Bob', 'Science', 'B', 90),
    ('Charlie', 'History', 'A', 78),
    ('David', 'Math', 'C', 88),
    ('Eve', 'Science', 'B', 92)
]

cursor.executemany(sql_query, values)
connection.commit()

cursor.executemany(sql_query, values)
connection.commit()

# Display the records
data=cursor.execute("""Select * from students""")

for row in data:
    print(row)

if connection:
    connection.close()
