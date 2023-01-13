import jaydebeapi

from consts import ConnectionConst

class Database:
    def __init__(self):
        self.conn = jaydebeapi.connect(
            ConnectionConst.JDBC_DRIVER_NAME,
            ConnectionConst.JDBC_URL,
            [ConnectionConst.DATABASE_USER, ConnectionConst.DATABASE_PASS],
            ConnectionConst.PATH_TO_DRIVER,
        )
        self.curs = self.conn.cursor()

    # decorator to avoid repeating code
    def _fetch_all(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            self = args[0]
            self.curs._rs = result
            self.curs._meta = result.getMetaData()
            records = self.curs.fetchall()
            self.curs.close()
            return records
        return wrapper

    @_fetch_all
    def get_tables(self):
        return self.conn.jconn.getMetaData().getTables("", "", "%", ["TABLE"])

    @_fetch_all
    def get_foreign_keys(self, table_name):
        return self.conn.jconn.getMetaData().getImportedKeys("", "", table_name)

    @_fetch_all
    def get_column_data(self, table_name):
        return self.conn.jconn.getMetaData().getColumns("", "", table_name, "%")

    def get_column_data_rs(self, table_name):
        return self.conn.jconn.getMetaData().getColumns("", "", table_name, "%")

    @_fetch_all
    def get_primary_keys(self, table_name):
        return self.conn.jconn.getMetaData().getPrimaryKeys("", "", table_name)

    def __enter__(self):
        return self
    
    def __exit__(self, *args, **kwargs):
        self.curs.close()
        self.conn.close()
