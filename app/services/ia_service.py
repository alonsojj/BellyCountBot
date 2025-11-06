import logging
import json
from app.core.settings import get_settings
from app.models.enums import ConversationState, AccountingService
from groq import Groq

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class IaService:
    def __init__(self):
        try:
            settings = get_settings()
            self.api_key = settings.GROQ_API_KEY
            if not self.api_key:
                logging.critical("GROQ_API_KEY não encontrada nas configurações!")
                raise ValueError("GROQ_API_KEY não encontrada nas configurações")

            self.client = Groq(api_key=self.api_key)
            logging.info("IaService (Groq) inicializado com sucesso.")
        except Exception as e:
            logging.error(f"Erro ao inicializar o IaService: {e}")
            self.client = None

    def _build_prompt(self, chat_history: list, stage: ConversationState) -> str:
        """
        Constrói um prompt único e contextual para a IA, informando o histórico
        e destacando a última mensagem do usuário.
        """
        # 1. Define a personalidade e o objetivo base da IA
        if stage == ConversationState.DOUBTS:
            system_prompt = (
                "Você é o CountBelly, um assistente virtual especialista em contabilidade "
                "do escritório DAS. Seu objetivo é ajudar clientes de forma "
                "profissional, clara e amigável. Responda apenas a perguntas "
                "relacionadas a contabilidade, finanças e aos serviços da DAS."
                "\n\nO usuário tem uma dúvida. Responda diretamente à última pergunta dele, usando o histórico como contexto."
            )
        elif stage == ConversationState.SERVICO_IA_CLASSIFY_AWAIT_DESCRIPTION:
            system_prompt = (
                "Você é um classificador de serviços contábeis. Analise a conversa e a última mensagem do usuário "
                "para identificar o serviço necessário. Retorne **apenas um objeto JSON**."
                "\nO JSON deve ter duas chaves: 'service' e 'description'."
                "\nA chave 'service' deve ser UMA das seguintes strings: "
                f"'[{', '.join([s.value for s in AccountingService if 'PLANEJAMENTO_' not in s.value])}]'. "
                "A chave 'description' deve ser uma explicação curta (1-2 frases) sobre o serviço identificado."
                "\nSe o problema não se encaixar em nenhum, use o serviço 'OUTRO'."
            )
        else:
            system_prompt = "Você é um assistente de contabilidade."

        # 2. Formata o histórico e a última mensagem
        full_prompt = [system_prompt, "\n"]

        if len(chat_history) > 1:
            full_prompt.append("--- HISTÓRICO DA CONVERSA (PARA CONTEXTO) ---")
            # Pega todo o histórico, exceto a última mensagem do usuário
            history_messages = chat_history[:-1]
            for msg in history_messages:
                full_prompt.append(f"{msg['role'].capitalize()}: {msg['content']}")
            full_prompt.append("--- FIM DO HISTÓRICO ---")
            full_prompt.append("\n")

        # Pega a última mensagem do usuário
        last_user_message = chat_history[-1]["content"]
        full_prompt.append(
            f"Baseado no contexto acima, processe a ÚLTIMA MENSAGEM DO USUÁRIO:"
        )
        full_prompt.append(f"Usuário: {last_user_message}")

        return "\n".join(full_prompt)

    def handle_ai_request(self, chat_history: list, stage: ConversationState) -> dict:
        """
        Processa a requisição de IA usando um histórico de chat e o estágio da conversa.
        """
        if not self.client:
            logging.error("IA não pode responder: Cliente Groq não inicializado.")
            return {
                "status": "fail",
                "content": "Desculpe, nosso serviço de IA está temporariamente indisponível.",
            }

        # Constrói o prompt contextual
        prompt = self._build_prompt(chat_history, stage)

        messages_to_send = [{"role": "user", "content": prompt}]

        # --- Geração da Resposta ---
        try:
            # Lógica de Classificação JSON
            if stage == ConversationState.SERVICO_IA_CLASSIFY_AWAIT_DESCRIPTION:
                chat_completion = self.client.chat.completions.create(
                    messages=messages_to_send,
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"},
                )
                response_content = chat_completion.choices[0].message.content
                logging.info(f"IA Classification RAW JSON: {response_content}")

                parsed_json = json.loads(response_content)
                service = parsed_json.get("service")
                description = parsed_json.get("description")

                if service not in [s.value for s in AccountingService]:
                    logging.warning(f"IA retornou serviço inválido: {service}")
                    return {
                        "status": "fail",
                        "content": "Não consegui identificar o serviço.",
                    }

                return {
                    "status": "success",
                    "type": "classification",
                    "service": service,
                    "description": description,
                }

            else:
                chat_completion = self.client.chat.completions.create(
                    messages=messages_to_send,
                    model="llama-3.3-70b-versatile",
                )
                response_content = chat_completion.choices[0].message.content
                return {
                    "status": "success",
                    "type": "answer",
                    "content": response_content
                    + "\n\n*(Digite 'Voltar' para a etapa anterior.)*",
                }

        except Exception as e:
            logging.error(f"Erro ao se comunicar com a API da Groq: {e}")
            return {
                "status": "fail",
                "content": "Ocorreu um erro ao tentar processar sua mensagem.",
            }
