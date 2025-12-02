import logging
from sqlalchemy.orm import Session
from typing import Optional


from app.models.client_db import ClientDB

from app.models.client_model import Client as ClientSchema


def get_client(db: Session, user_id: str) -> Optional[ClientDB]:
    """
    Consulta e retorna um cliente do banco de dados pelo user_id.
    """
    return db.query(ClientDB).filter(ClientDB.user_id == user_id).first()


def create_or_update_client(db: Session, client_data: ClientSchema) -> ClientDB:
    """
    Cria um novo cliente se ele não existir, ou atualiza um cliente existente.
    """

    db_client = get_client(db, client_data.user_id)

    if db_client:
        update_data = client_data.__dict__

        for key, value in update_data.items():
            if value is not None:
                setattr(db_client, key, value)

        logging.info(f"Atualizando dados no DB para o usuário: {db_client.user_id}")

    else:
        model_columns = [c.name for c in ClientDB.__table__.columns]

        filtered_data = {
            key: value
            for key, value in client_data.__dict__.items()
            if key in model_columns
        }

        db_client = ClientDB(**filtered_data)

        db.add(db_client)

        logging.info(
            f"Criando novo registro no DB para o usuário: {client_data.user_id}"
        )

    db.commit()

    db.refresh(db_client)

    return db_client
