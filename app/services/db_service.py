from sqlalchemy.orm import Session
from typing import Optional

from app.models import Client, ClientDB


def get_client(db: Session, user_id: str) -> Optional[Client]:
    """
    Consulta e retorna um cliente do banco de dados pelo user_id.
    """
    return db.query(Client).filter(Client.user_id == user_id).first()


def create_or_update_client(db: Session, client_data: ClientDB) -> Client:
    """
    Cria um novo cliente se ele não existir, ou atualiza um cliente existente.
    """
    db_client = get_client(db, client_data.user_id)

    if db_client:
        update_data = client_data.__dict__
        for key, value in update_data.items():
            if value is not None:
                setattr(db_client, key, value)
    else:
        db_client = Client(**client_data.__dict__)
        db.add(db_client)

    db.commit()
    db.refresh(db_client)

    return db_client
