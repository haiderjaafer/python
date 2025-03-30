class DevelopmentConfig:
    DEBUG = True
    DATABASE_URI = (
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=localhost;'
        'DATABASE=ContractsProcedures;'
        'UID=sa;'
        'PWD=123'
    )
    PDF_BASE_PATH = 'D:/order_pdfs'  # Add this line
