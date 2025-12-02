import os
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Obtém a URL do banco de dados das variáveis de ambiente
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL não está configurada no arquivo .env")
else:
    # Log para confirmar o alvo da conexão (sem expor a senha)
    try:
        db_host = DATABASE_URL.split("@")[1].split(":")[0]
        db_name = DATABASE_URL.split("/")[-1]
        logging.info(f"Conectando ao banco de dados: Host='{db_host}', DB='{db_name}'")
    except Exception:
        logging.error("Não foi possível parsear a DATABASE_URL para logging.")


engine = create_engine(DATABASE_URL)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()


# Dependência para obter a sessão do banco de dados em rotas FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
