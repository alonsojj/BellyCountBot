from typing import List, Optional
from pydantic import BaseModel, Field

class CnaeSecundario(BaseModel):
    codigo: int
    descricao: str

class CNPJData(BaseModel):
    sucesso: bool = True
    erro: Optional[str] = None
    codigo_erro: Optional[str] = None

    uf: Optional[str] = None
    cep: Optional[str] = None
    qsa: List = Field(default_factory=list)
    cnpj: Optional[str] = None
    pais: Optional[str] = None
    email: Optional[str] = None
    porte: Optional[str] = None
    bairro: Optional[str] = None
    numero: Optional[str] = None
    ddd_fax: Optional[str] = None
    municipio: Optional[str] = None
    logradouro: Optional[str] = None
    cnae_fiscal: Optional[int] = None
    codigo_pais: Optional[str] = None
    complemento: Optional[str] = None
    codigo_porte: Optional[int] = None
    razao_social: Optional[str] = None
    nome_fantasia: Optional[str] = None
    capital_social: Optional[int] = None
    ddd_telefone_1: Optional[str] = None
    ddd_telefone_2: Optional[str] = None
    opcao_pelo_mei: Optional[bool] = None
    codigo_municipio: Optional[int] = None
    cnaes_secundarios: List[CnaeSecundario] = Field(default_factory=list)
    natureza_juridica: Optional[str] = None
    regime_tributario: List = Field(default_factory=list)
    situacao_especial: Optional[str] = None
    opcao_pelo_simples: Optional[bool] = None
    situacao_cadastral: Optional[int] = None
    data_opcao_pelo_mei: Optional[str] = None
    data_exclusao_do_mei: Optional[str] = None
    cnae_fiscal_descricao: Optional[str] = None
    codigo_municipio_ibge: Optional[int] = None
    data_inicio_atividade: Optional[str] = None
    data_situacao_especial: Optional[str] = None
    data_opcao_pelo_simples: Optional[str] = None
    data_situacao_cadastral: Optional[str] = None
    nome_cidade_no_exterior: Optional[str] = None
    codigo_natureza_juridica: Optional[int] = None
    data_exclusao_do_simples: Optional[str] = None
    motivo_situacao_cadastral: Optional[int] = None
    ente_federativo_responsavel: Optional[str] = None
    identificador_matriz_filial: Optional[int] = None
    qualificacao_do_responsavel: Optional[int] = None
    descricao_situacao_cadastral: Optional[str] = None
    descricao_tipo_de_logradouro: Optional[str] = None
    descricao_motivo_situacao_cadastral: Optional[str] = None
    descricao_identificador_matriz_filial: Optional[str] = None
