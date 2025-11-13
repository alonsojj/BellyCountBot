import logging
import json
import re
from app.core.settings import get_settings
from app.models.enums import ConversationState, AccountingService
from groq import Groq

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class IaService:
    def __init__(self, chatbot_service=None):
        self.chatbot_service = chatbot_service
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
        elif stage == ConversationState.AGUARDANDO_OPCAO_INICIAL:
            system_prompt = (
                "Você é um classificador de intenções. Analise a conversa e a última mensagem do usuário."
                "\nSua tarefa é identificar a intenção do usuário e classificá-la como um 'service' ou uma 'option'."
                "\nRetorne **apenas um objeto JSON** com as chaves 'service', 'option' e 'description'."
                "\n"
                "As opções do menu inicial são:\n"
                "- 1. Sou novo por aqui.\n"
                "- 2. Preciso de um serviço específico.\n"
                "- 3. Tenho uma dúvida.\n"
                "\nPriorize a identificação de um 'service'. Se a intenção do usuário for claramente um serviço, "
                "a chave 'service' deve ser UMA das seguintes strings: "
                f"'[{', '.join([s.value for s in AccountingService])}]'. "
                "A chave 'option' deve ser 'None'."
                "\nSe a intenção do usuário corresponder a uma das opções numeradas do menu inicial, "
                "e um 'service' específico não for identificado, então a chave 'option' deve ser o *número* da opção (ex: '1', '2', '3'). "
                "Nesse caso, a chave 'service' deve ser 'None'."
                "\nA chave 'description' deve ser uma explicação curta (1-2 frases) sobre o serviço ou opção identificada."
                "\nSe o problema não se encaixar em nenhum serviço ou opção, use o serviço 'OUTRO' para a chave 'service' e 'None' para 'option'."
            )
        elif stage in [
            ConversationState.AGUARDANDO_ESCOLHA_SERVICO_PF,
            ConversationState.AGUARDANDO_ESCOLHA_SERVICO_PJ,
        ]:
            system_prompt = (
                "Você é um classificador de intenções. Analise a conversa e a última mensagem do usuário."
                "\nSua tarefa é identificar se a intenção do usuário corresponde a uma das opções apresentadas na última mensagem do chatbot."
                "\nRetorne **apenas um objeto JSON** com as chaves 'option' e 'description'."
                "\n"
            )

            last_assistant_message = None
            for msg in reversed(chat_history[:-1]):
                if msg["role"] == "assistant":
                    last_assistant_message = msg["content"]
                    break

            if last_assistant_message:
                options_pattern = re.compile(r"^(\d+)\.\s(.+)$", re.MULTILINE)
                numbered_options = options_pattern.findall(last_assistant_message)

                if numbered_options:
                    system_prompt += (
                        "\nAs opções que o chatbot apresentou ao usuário são:\n"
                    )
                    for num, desc in numbered_options:
                        system_prompt += f"- {num}. {desc}\n"
                    system_prompt += (
                        "\nCom base na última mensagem do usuário e nas opções acima, se a intenção do usuário corresponder a uma dessas opções, "
                        "retorne o *número* da opção (ex: '1', '2', '3') na chave 'option'."
                        "\nCaso contrário, a chave 'option' deve ser 'None'."
                    )
                else:
                    system_prompt += "\nNão foram encontradas opções numeradas na última mensagem do chatbot. A chave 'option' deve ser 'None'."
            else:
                system_prompt += "\nNão foi encontrada uma mensagem anterior do chatbot com opções. A chave 'option' deve ser 'None'."

            system_prompt += "\nA chave 'description' deve ser uma explicação curta (1-2 frases) sobre a opção identificada."

        elif stage == ConversationState.SERVICO_IA_CLASSIFY_AWAIT_DESCRIPTION:
            system_prompt = (
                "Você é um classificador de intenções. Analise a conversa e a última mensagem do usuário."
                "\nSua tarefa é identificar se a intenção do usuário corresponde a uma das opções apresentadas na última mensagem do chatbot."
                "\nRetorne **apenas um objeto JSON** com as chaves 'option', 'service' e 'description'."
                "\n"
            )

            # Tenta encontrar a última mensagem do assistente para extrair as opções
            last_assistant_message = None
            # Iterate in reverse, excluding the very last message which is the current user's
            for msg in reversed(chat_history[:-1]):
                if msg["role"] == "assistant":
                    last_assistant_message = msg["content"]
                    break

            if last_assistant_message:
                # Extrai as opções numeradas da última mensagem do assistente
                # This regex looks for lines starting with a number followed by a dot and a space
                options_pattern = re.compile(r"^(\d+)\.\s(.+)$", re.MULTILINE)
                numbered_options = options_pattern.findall(last_assistant_message)

                if numbered_options:
                    system_prompt += (
                        "\nAs opções que o chatbot apresentou ao usuário são:\n"
                    )
                    for num, desc in numbered_options:
                        system_prompt += f"- {num}. {desc}\n"
                    system_prompt += (
                        "\nCom base na última mensagem do usuário e nas opções acima, se a intenção do usuário corresponder a uma dessas opções, "
                        "retorne o *número* da opção (ex: '1', '2', '3') na chave 'option'."
                        "\nCaso contrário, a chave 'option' deve ser 'None'."
                    )
                else:
                    system_prompt += "\nNão foram encontradas opções numeradas na última mensagem do chatbot. Apenas classifique o serviço."
            else:
                system_prompt += "\nNão foi encontrada uma mensagem anterior do chatbot com opções. Apenas classifique o serviço."

            system_prompt += (
                "\nSe a chave 'option' for 'None', então a chave 'service' deve ser UMA das seguintes strings: "
                f"'[{', '.join([s.value for s in AccountingService if 'PLANEJAMENTO_' not in s.value])}]'. "
                "A chave 'description' deve ser uma explicação curta (1-2 frases) sobre o serviço identificado."
                "\nSe o problema não se encaixar em nenhum serviço, use o serviço 'OUTRO' para a chave 'service'."
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
            "Baseado no contexto acima, processe a ÚLTIMA MENSAGEM DO USUÁRIO:"
        )
        full_prompt.append(f"Usuário: {last_user_message}")

        return "\n".join(full_prompt)

    def handle_ai_request(self, chat_history: list, stage: ConversationState) -> dict:
        """
        Processa a requisição de IA usando um histórico de chat e o estágio da conversa.
        """
        if not self.client:
            logging.error("IA não pode responder: Cliente Groq não inicializado.")
            logging.debug("handle_ai_request returning from client not initialized.")
            return {
                "status": "fail",
                "content": "Desculpe, nosso serviço de IA está temporariamente indisponível.",
            }

        # Constrói o prompt contextual
        prompt = self._build_prompt(chat_history, stage)
        logging.debug(f"Prompt built: {prompt}")

        messages_to_send = [{"role": "user", "content": prompt}]

        # --- Geração da Resposta ---
        try:
            if stage == ConversationState.DOUBTS:
                chat_completion = self.client.chat.completions.create(
                    messages=messages_to_send,
                    model="llama-3.3-70b-versatile",
                )
                response_content = chat_completion.choices[0].message.content
                logging.debug("handle_ai_request returning answer success.")
                return {
                    "status": "success",
                    "type": "answer",
                    "content": response_content
                    + "\n\n*(Digite 'Voltar' para a etapa anterior.)*",
                }
            elif stage == ConversationState.AGUARDANDO_OPCAO_INICIAL:
                chat_completion = self.client.chat.completions.create(
                    messages=messages_to_send,
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"},
                )
                response_content = chat_completion.choices[0].message.content
                logging.info(
                    f"IA Classification RAW JSON (AGUARDANDO_OPCAO_INICIAL): {response_content}"
                )

                parsed_json = json.loads(response_content)
                service = parsed_json.get("service")
                description = parsed_json.get("description")
                option = parsed_json.get("option")

                if (
                    service not in [s.value for s in AccountingService]
                    and service != "OUTRO"
                    and option is None
                ):
                    logging.warning(
                        f"IA retornou serviço inválido e nenhuma opção: {service}"
                    )
                    return {
                        "status": "fail",
                        "content": "Não consegui identificar o serviço ou opção.",
                    }
                return {
                    "status": "success",
                    "type": "classification",
                    "service": service,
                    "description": description,
                    "option": option,
                }
            elif stage in [
                ConversationState.AGUARDANDO_ESCOLHA_SERVICO_PF,
                ConversationState.AGUARDANDO_ESCOLHA_SERVICO_PJ,
            ]:
                chat_completion = self.client.chat.completions.create(
                    messages=messages_to_send,
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"},
                )
                response_content = chat_completion.choices[0].message.content
                logging.info(
                    f"IA Classification RAW JSON (AGUARDANDO_ESCOLHA_SERVICO_PF/PJ): {response_content}"
                )

                parsed_json = json.loads(response_content)
                option = parsed_json.get("option")
                description = parsed_json.get("description")

                return {
                    "status": "success",
                    "type": "classification",
                    "service": None,
                    "description": description,
                    "option": option,
                }
            elif stage == ConversationState.SERVICO_IA_CLASSIFY_AWAIT_DESCRIPTION:
                chat_completion = self.client.chat.completions.create(
                    messages=messages_to_send,
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"},
                )
                response_content = chat_completion.choices[0].message.content
                logging.info(
                    f"IA Classification RAW JSON (SERVICO_IA_CLASSIFY_AWAIT_DESCRIPTION): {response_content}"
                )

                parsed_json = json.loads(response_content)
                service = parsed_json.get("service")
                description = parsed_json.get("description")
                option = parsed_json.get("option")

                if (
                    option is None
                    and service not in [s.value for s in AccountingService]
                    and service != "OUTRO"
                ):
                    logging.warning(f"IA retornou serviço inválido: {service}")
                    logging.debug("handle_ai_request returning from invalid service.")
                    return {
                        "status": "fail",
                        "content": "Não consegui identificar o serviço.",
                    }

                logging.debug("handle_ai_request returning classification success.")
                return {
                    "status": "success",
                    "type": "classification",
                    "service": service,
                    "description": description,
                    "option": option,
                }
            else:  # Fallback for any other state not explicitly handled
                chat_completion = self.client.chat.completions.create(
                    messages=messages_to_send,
                    model="llama-3.3-70b-versatile",
                )
                response_content = chat_completion.choices[0].message.content
                logging.debug(
                    "handle_ai_request returning answer success for unhandled state."
                )
                return {
                    "status": "success",
                    "type": "answer",
                    "content": response_content
                    + "\n\n*(Digite 'Voltar' para a etapa anterior.)*",
                }

        except Exception as e:
            logging.error(f"Erro ao se comunicar com a API da Groq: {e}")
            logging.debug("handle_ai_request returning from exception.")
            return {
                "status": "fail",
                "content": "Ocorreu um erro ao tentar processar sua mensagem.",
            }
