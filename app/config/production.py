class ProductionConfig:
    DEBUG = False
    DATABASE_URI = (
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=production_server;'
        'DATABASE=ContractsProcedures;'
        'UID=sa;'
        'PWD=production_password'
    )