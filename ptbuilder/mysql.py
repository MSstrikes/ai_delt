import pymysql
import utils as tool


def get_conn():
    return pymysql.connect(host=tool.MYSQL_HOST,
                           port=tool.MYSQL_PORT,
                           user=tool.MYSQL_USER,
                           passwd=tool.MYSQL_PASSWORD,
                           db=tool.MYSQL_DB, charset='utf8')


def get_table(table_name):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM " + table_name)
    out = cur.fetchall()
    cur.close()
    conn.close()
    return out


def insert_coordinate(json_obj):
    conn = get_conn()
    cur = conn.cursor()
    # SQL 插入语句

    try:
        # 执行sql语句
        for row in json_obj:
            sql = "INSERT INTO dw_dim_coordinate(latitude,longitude, radius, distance_unit) VALUES ('" + \
                  row['latitude'] + "', '" + row['longitude'] + "', '" + row['radius'] + "', '" + row[
                      'distance_unit'] + "')"
            cur.execute(sql)
        # 提交到数据库执行
        conn.commit()
    except Exception:
        # Rollback in case there is any error
        conn.rollback()

    cur.close()
    conn.close()
