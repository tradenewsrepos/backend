import psycopg2

with open("../../config.txt") as f:
    user, password, host, port = [w.strip() for w in f.readlines()]

get_list_of_tables = """SELECT relname 
                        FROM pg_class 
                        WHERE relkind IN ('r', 'm') and relname !~ '^(pg_|sql_)'
                        ORDER BY relname;"""

with psycopg2.connect(
    database="newsfeed_db",
    host=host,
    port=port,
    user=user,
    password=password,
) as conn:
    with conn.cursor() as cursor:
        cursor.execute(get_list_of_tables)
        list_of_tables = [table_name[0] for table_name in cursor.fetchall()]
print(list_of_tables)

DUMP_TABLE = """
            SELECT *
            FROM trade_news_events          
            LIMIT 50;
            """
with psycopg2.connect(
    database="newsfeed_db",
    host=host,
    port=port,
    user=user,
    password=password,
) as conn:
    with conn.cursor() as cursor:
        cursor.execute(dump_sql)
