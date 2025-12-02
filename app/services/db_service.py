import logging
from sqlalchemy.orm import Session
from typing import Optional


from app.models.client_db import ClientDB

from app.models.client_model import Client as ClientSchema


def get_client(db: Session, document_number: str) -> Optional[ClientDB]:
    """
    Consulta e retorna um cliente do banco de dados pelo document_number.
    """
    return (
        db.query(ClientDB).filter(ClientDB.document_number == document_number).first()
    )


def create_or_update_client(db: Session, client_data: ClientSchema) -> ClientDB:
    """
    Cria um novo cliente se ele não existir, ou atualiza um cliente existente.
    """

    db_client = get_client(db, client_data.document_number)

    # Get all column names from ClientDB for filtering
    model_columns = [c.name for c in ClientDB.__table__.columns]

    # Prepare data from client_data, excluding 'user_id' if it's not a direct column in ClientDB
    # and mapping it to 'phone' if 'phone' is a column in ClientDB.
    client_data_dict = client_data.__dict__.copy()

    # Handle user_id to phone mapping
    if "user_id" in client_data_dict and "phone" in model_columns:
        if client_data_dict["user_id"] is not None:
            client_data_dict["phone"] = client_data_dict["user_id"]
        del client_data_dict[
            "user_id"
        ]  # Remove user_id as it's not a direct column in ClientDB

    if db_client:
        # Update existing client
        update_data = {
            key: value
            for key, value in client_data_dict.items()
            if key in model_columns and value is not None
        }

        for key, value in update_data.items():
            setattr(db_client, key, value)

        logging.info(
            f"Atualizando dados no DB para o usuário: {db_client.document_number}"
        )

    else:
        # Create new client
        filtered_data = {
            key: value
            for key, value in client_data_dict.items()
            if key in model_columns
        }

        # CRITICAL: Ensure document_number is present and not None for new client creation
        if 'document_number' not in filtered_data or filtered_data['document_number'] is None:
            logging.error(f"Attempted to create new client with NULL document_number. client_data: {client_data_dict}")
            raise ValueError("Cannot create client: document_number is missing or NULL.")

        db_client = ClientDB(**filtered_data)

        db.add(db_client)

        logging.info(
            f"Criando novo registro no DB para o usuário: {client_data.document_number}"
        )

    db.commit()

    db.refresh(db_client)

    return db_client
