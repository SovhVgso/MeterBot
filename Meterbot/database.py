import sqlite3
from contextlib import contextmanager

class dbapi():
    def __init__(self,db_path:str):
        self.db_path = db_path
        self.connection = None
    
    @contextmanager
    def get_cursor(self):
        """ 获取游标，并在完成后自动关闭 """
        if not self.connection:
            self.connect()
        cursor = self.connection.cursor()
        try:
            yield cursor
        finally:
            cursor.close()

    def connect(self):
        """ 连接到数据库 """
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row  # 让每一行返回为字典而不是元组

    def disconnect(self):
        """ 断开数据库连接 """
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def execute_query(self, query, params=None):
        """ 执行SQL查询并提交事务 """
        with self.get_cursor() as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            return cursor.fetchall()

    def create_table(self, table_name, columns):
        """ 创建新表 
        db.create_table('users', {'id': 'INTEGER PRIMARY KEY', 'name': 'TEXT', 'email': 'TEXT', 'user_id': 'INTEGER'})"""
        column_definitions = ', '.join([f'{name} {type}' for name, type in columns.items()])
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_definitions})"
        self.execute_query(query)

    def insert(self, table_name, data, unique_keys=['id'], additional_conditions=None, is_update=True):
        """ 向表中插入数据，如果已存在则默认更新，第三个参数必须是唯一的
        db.insert('users', user_data, ['id'], "user_id = EXCLUDED.user_id")"""
        # 构建列名和占位符
        columns = ', '.join(data.keys())
        placeholders = ', '.join('?' * len(data))
        
        # 构建更新部分
        update_clause = ', '.join([f"{key} = EXCLUDED.{key}" for key in data])
        
        # 构建完整的SQL查询
        conflict_clause = ', '.join(unique_keys)
        where_clause = f" AND {additional_conditions}" if additional_conditions else ""
        
        if is_update:
            # 如果 is_update 为 True，则使用 ON CONFLICT ... DO UPDATE
            query = f"""
                INSERT INTO {table_name} ({columns})
                VALUES ({placeholders})
                ON CONFLICT({conflict_clause}) 
                DO UPDATE SET {update_clause} WHERE {conflict_clause}{where_clause}
            """
        else:
            # 如果 is_update 为 False，则使用 ON CONFLICT ... DO NOTHING
            query = f"""
                INSERT INTO {table_name} ({columns})
                VALUES ({placeholders})
                ON CONFLICT({conflict_clause}) 
                DO NOTHING
            """
        
        # 执行查询
        self.execute_query(query, tuple(data.values()))

    def select(self, table_name, conditions=None):
        """ 根据条件选择记录 
        specific_users = db.select('users', {'user_id': ('>', 3)})"""
        query = f"SELECT * FROM {table_name}"
        
        if conditions:
            where_clauses = []
            params = []
            
            for key, value in conditions.items():
                if isinstance(value, tuple) and len(value) == 2:
                    # 如果值是一个元组，第一个元素是操作符，第二个元素是实际值
                    operator, val = value
                    where_clauses.append(f"{key} {operator} ?")
                    params.append(val)
                else:
                    # 默认等于操作
                    where_clauses.append(f"{key} = ?")
                    params.append(value)
            
            where_clause = ' AND '.join(where_clauses)
            query += f" WHERE {where_clause}"
            return self.execute_query(query, tuple(params))
        else:
            return self.execute_query(query)
        
    def add_columns(self, table_name, column_definitions):
        """ 给现有表添加列，并可设置默认值 
        # 添加新列（字典格式）
        new_columns_dict = {
            'age': ['INTEGER', 0],
            'created_at': ['TEXT', 'CURRENT_TIMESTAMP']
        }
        db.add_columns('users', new_columns_dict)
        
        # 添加新列（列表格式）
        new_columns_list = ['phone_number', 'address']
        db.add_columns('users', new_columns_list)"""
        """ 给现有表添加列，并可设置默认值 """
        if isinstance(column_definitions, dict):
            # 字典格式: {'列名': ['类型', '默认值']}
            for column, (column_type, default_value) in column_definitions.items():
                default_clause = f" DEFAULT {default_value}" if default_value is not None else ""
                query = f"ALTER TABLE {table_name} ADD COLUMN {column} {column_type}{default_clause}"
                self.execute_query(query)
        elif isinstance(column_definitions, list):
            # 列表格式: ['列1', '列2']
            for column in column_definitions:
                query = f"ALTER TABLE {table_name} ADD COLUMN {column} NONE"
                self.execute_query(query)

    def drop_columns(self, table_name, columns_to_drop):
        """ 删除表中的列
        columns_to_drop = ['phone_number', 'address']
        db.drop_columns('users', columns_to_drop)"""
        if not isinstance(columns_to_drop, list):
            columns_to_drop = [columns_to_drop]
        with self.get_cursor() as cursor:
            cursor.execute(f"PRAGMA table_info({table_name})")
            existing_columns = [row['name'] for row in cursor.fetchall()]
        
        for col in columns_to_drop:
            if col not in existing_columns:
                raise ValueError(f"Column '{col}' does not exist in table '{table_name}'")
        
        for col in columns_to_drop:
            query = f"ALTER TABLE {table_name} DROP COLUMN {col}"
            self.execute_query(query)

    def delete_records(self, table_name, conditions=None):
        """ 根据条件删除记录
         conditions = {'name': ('=', 'Alice')}
         db.delete_records('users', conditions) """
        query = f"DELETE FROM {table_name}"
        if conditions:
            where_clauses = []
            params = []
            for key, value in conditions.items():
                if isinstance(value, tuple) and len(value) == 2:
                    operator, val = value
                    where_clauses.append(f"{key} {operator} ?")
                    params.append(val)
                else:
                    where_clauses.append(f"{key} = ?")
                    params.append(value)
            
            where_clause = ' AND '.join(where_clauses)
            query += f" WHERE {where_clause}"
            self.execute_query(query, tuple(params))
        else:
            self.execute_query(query)

        