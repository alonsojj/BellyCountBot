import re
import httpx

from app.models import CNPJData, CnaeSecundario


def validar_cpf(cpf: str) -> bool:
    cpf = re.sub(r"[^0-9]", "", cpf)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    try:
        numeros = [int(digito) for digito in cpf]
    except ValueError:
        return False
    soma_produtos = sum(a * b for a, b in zip(numeros[0:9], range(10, 1, -1)))
    digito_esperado = (soma_produtos * 10 % 11) % 10
    if numeros[9] != digito_esperado:
        return False
    soma_produtos = sum(a * b for a, b in zip(numeros[0:10], range(11, 1, -1)))
    digito_esperado = (soma_produtos * 10 % 11) % 10
    if numeros[10] != digito_esperado:
        return False
    return True


def validar_cnpj(cnpj: str) -> bool:
    cnpj = re.sub(r"[^0-9]", "", cnpj)
    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return False
    try:
        numeros = [int(digito) for digito in cnpj]
    except ValueError:
        return False
    pesos = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(numeros[i] * pesos[i] for i in range(12))
    resto = soma % 11
    digito_verificador1 = 0 if resto < 2 else 11 - resto
    if numeros[12] != digito_verificador1:
        return False
    soma = 0
    pesos = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(numeros[i] * pesos[i] for i in range(13))
    resto = soma % 11
    digito_verificador2 = 0 if resto < 2 else 11 - resto
    if numeros[13] != digito_verificador2:
        return False
    return True


async def consultar_cnpj_empresa(cnpj: str) -> CNPJData:
    if not validar_cnpj(cnpj):
        return CNPJData(
            sucesso=False,
            erro="CNPJ inválido",
            codigo_erro="INVALID_CNPJ",
        )

    clean_cnpj = re.sub(r"[^0-9]", "", cnpj)
    url = f"https://brasilapi.com.br/api/cnpj/v1/{clean_cnpj}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)

            if response.status_code == 200:
                data = response.json()

                data["cnaes_secundarios"] = [
                    CnaeSecundario(**cnae) for cnae in data.get("cnaes_secundarios", [])
                ]
                return CNPJData(**data)
            elif response.status_code == 404:
                return CNPJData(
                    sucesso=False,
                    erro="CNPJ não encontrado",
                    codigo_erro="NOT_FOUND",
                )
            else:
                return CNPJData(
                    sucesso=False,
                    erro=f"Erro na API externa: {response.status_code} - {response.text}",
                    codigo_erro="EXTERNAL_API_ERROR",
                )

        except httpx.RequestError as e:
            return CNPJData(
                sucesso=False,
                erro=f"Erro de conexão com a API: {str(e)}",
                codigo_erro="CONNECTION_ERROR",
            )
        except Exception as e:
            return CNPJData(
                sucesso=False,
                erro=f"Erro inesperado ao consultar CNPJ: {str(e)}",
                codigo_erro="UNEXPECTED_ERROR",
            )
