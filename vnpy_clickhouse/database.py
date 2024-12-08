from clickhouse_driver import Client
from contextlib import contextmanager
import datetime

class Database:
    def __init__(self, host='localhost', port=9000, user='default', password='', database='futures'):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.client = None
        self.create_tick_table()
        self.create_bar_table()
    def connect(self):
        self.client = Client(self.host, port=self.port, user=self.user, password=self.password, database=self.database)
        print("Connected to ClickHouse.")

    def close(self):
        if self.client:
            self.client.disconnect()
            print("Connection to ClickHouse closed.")

    @contextmanager
    def connection(self):
        self.connect()
        try:
            yield self.client
        finally:
            self.close()

    def create_bar_table(self):
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS bar_data
            (
                symbol FixedString(16),
                exchange FixedString(16),
                interval FixedString(16),
                datetime DateTime,
                open_price Float64,
                high_price Float64,
                low_price Float64,
                close_price Float64,
                volume Int64,
                open_interest Int64
            )
        ENGINE = MergeTree()
        PARTITION BY toYYYYMM(datetime)
        ORDER BY (symbol, exchange, interval, datetime)
        SETTINGS index_granularity = 8192;
        """
        with self.connection() as client:
            client.execute(create_table_sql)
        print("Table 'bar_data' created successfully.")

    def create_tick_table(self):
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS tick_data
        (
            symbol FixedString(16),
            exchange FixedString(16),
            datetime DateTime,

            name String,
            volume Float64,
            turnover Float64,
            open_interest Float64,
            last_price Float64,
            last_volume Float64,
            limit_up Float64,
            limit_down Float64,

            open_price Float64,
            high_price Float64,
            low_price Float64,
            pre_close Float64,

            bid_price_1 Float64,
            bid_price_2 Float64,
            bid_price_3 Float64,
            bid_price_4 Float64,
            bid_price_5 Float64,

            ask_price_1 Float64,
            ask_price_2 Float64,
            ask_price_3 Float64,
            ask_price_4 Float64,
            ask_price_5 Float64,

            bid_volume_1 Float64,
            bid_volume_2 Float64,
            bid_volume_3 Float64,
            bid_volume_4 Float64,
            bid_volume_5 Float64,

            ask_volume_1 Float64,
            ask_volume_2 Float64,
            ask_volume_3 Float64,
            ask_volume_4 Float64,
            ask_volume_5 Float64,

            localtime DateTime
        )
        ENGINE = MergeTree
        PARTITION BY toYYYYMM(datetime)
        ORDER BY (symbol, exchange, datetime)
        SETTINGS index_granularity = 8192;
        """
        with self.connection() as client:
            client.execute(create_table_sql)
        print("Table 'tick_data' created successfully.")

# # 示例用法
# if __name__ == "__main__":
#     # 创建 Database 实例
#     ch_manager = Database()

#     # 创建 tick_data 表
#     ch_manager.create_tick_table()

#     # 关闭连接
#     ch_manager.close()


# # 示例用法
# if __name__ == "__main__":
#     # 创建 Database 实例
#     ch_manager = Database()

#     # 示例数据
#     tick_data = [
#         ('AAPL', datetime(2024, 12, 8, 11, 35, 00), 150.25, 1000, 150.20, 500, 150.30, 600, 'example1'),
#         ('GOOG', datetime(2024, 12, 8, 11, 36, 00), 2750.50, 500, 2750.40, 300, 2750.60, 400, 'example2'),
#         ('MSFT', datetime(2024, 12, 8, 11, 37, 00), 300.75, 800, 300.70, 400, 300.80, 500, 'example3')
#     ]

#     # 插入数据
#     ch_manager.insert_tick_data(tick_data)

#     # 加载数据
#     symbol = 'AAPL'
#     start_time = datetime(2024, 12, 8, 11, 35, 00)
#     end_time = datetime(2024, 12, 8, 11, 36, 00)

#     # 加载特定时间范围内的数据
#     data_range = ch_manager.load_tick_data(symbol, start_time, end_time)
#     print("Data for specific time range:")
#     for row in data_range:
#         print(row)

#     # 加载所有数据
#     all_data = ch_manager.load_tick_data(symbol)
#     print("All data for the symbol:")
#     for row in all_data:
#         print(row)

#     # 关闭连接
#     ch_manager.close()
