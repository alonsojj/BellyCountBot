from app.core.settings import get_settings
from groq import Groq


class IaService:
    def __init__(self):
        try:
            settings = get_settings()
            self.api_key = settings.GROQ_API_KEY
            if not self.api_key:
                raise ValueError("GROQ_API_KEY não encontrada no arquivo .env")

            self.client = Groq(api_key=self.api_key)
        except Exception as e:
            print(f"Erro ao inicializar o GroqService: {e}")
            self.client = None

    def get_response(self, user_prompt: str) -> str:
        """
        Envia um prompt para a IA da Groq e retorna a resposta.
        """
        if not self.client:
            return "Desculpe, o serviço de IA não está disponível no momento."

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "Voce é um atendente prestativo",
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                model="llama-3.3-70b-versatile",
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(f"Erro ao se comunicar com a API da Groq: {e}")
            return "Ocorreu um erro ao tentar processar sua mensagem."


if __name__ == "__main__":
    service = IaService()
    prompt = "Olá! Qual a capital do Brasil?"
    response = service.get_response(prompt)
    print(f"Pergunta: {prompt}")
    print(f"Resposta da IA: {response}")
