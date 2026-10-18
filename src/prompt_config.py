# src/prompt_config.py

SYSTEM_PROMPT = """
Você é o assistente oficial de Inteligência Artificial para análise de 'Voice of Customer' (VoC) da Olist, desenvolvido no contexto do Tech Challenge (Fase 4) da Pós-Tech FIAP.
Seu objetivo é analisar avaliações de clientes de forma estritamente fundamentada em dados reais, garantindo rastreabilidade e rigor analítico.
"""

def detetar_intencao(pergunta_utilizador: str) -> str:
    pergunta_lower = pergunta_utilizador.lower()

    # Palavras-chave altamente restritas para problemas/reclamações
    termos_negativos = [
        "reclama", "reclamac", "problema", "ruim", "pior", "piores",
        "defeito", "atraso", "falha", "negativ", "critica", "erro", "insatisfeit"
    ]

    termos_positivos = [
        "elogi", "gost", "maravilhoso", "excelente", "perfeito",
        "bom", "otimo", "favorito", "amaram", "satisfeit"
    ]

    if any(termo in pergunta_lower for termo in termos_negativos):
        return "negativa"
    elif any(termo in pergunta_lower for termo in termos_positivos):
        return "positiva"
    return "neutra"