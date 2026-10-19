import unicodedata
import re

SYSTEM_PROMPT = """
Você é o assistente oficial de Inteligência Artificial para análise de 'Voice of Customer' (VoC) da Olist, desenvolvido no contexto do Tech Challenge (Fase 4) da Pós-Tech FIAP.
Seu objetivo é analisar avaliações de clientes de forma estritamente fundamentada em dados reais, garantindo rastreabilidade e rigor analítico.
"""

def limpar_texto(txt: str) -> str:
    """Remove acentos, pontuações (?, !, ., etc) e padroniza para minúsculas."""
    if not txt: 
        return ""
    # Remove acentos (é -> e, ã -> a)
    txt = ''.join(c for c in unicodedata.normalize('NFD', str(txt)) if unicodedata.category(c) != 'Mn')
    # Remove pontuação e caracteres especiais (Mantém apenas letras e números)
    txt = re.sub(r'[^\w\s]', ' ', txt)
    return txt.replace(" e ", " ").lower().strip()

def detetar_intencao(pergunta_utilizador: str) -> str:
    # Agora a intenção lê sempre o texto 100% limpo!
    pergunta_limpa = limpar_texto(pergunta_utilizador)

    termos_negativos = ["reclama", "reclamac", "problema", "ruim", "pior", "piores", "defeito", "atraso", "falha", "negativ", "critica", "erro", "insatisfeit"]
    termos_positivos = ["elogi", "gost", "maravilhoso", "excelente", "perfeito", "bom", "otimo", "favorito", "amaram", "satisfeit", "melhores", "melhor"]

    if any(termo in pergunta_limpa for termo in termos_negativos):
        return "negativa"
    elif any(termo in pergunta_limpa for termo in termos_positivos):
        return "positiva"
    return "neutra"

def analisar_pergunta_rag(pergunta, categorias_validas, categoria_forcada=None):
    """Motor central de NLP para roteamento da interface."""
    pergunta_segura = pergunta if pergunta else "visao geral"
    pergunta_lower = pergunta_segura.lower()
    pergunta_limpa = limpar_texto(pergunta_segura)
    
    # Flags de UI (Gráficos e Porcentagens)
    pediu_grafico = any(termo in pergunta_limpa for termo in ["grafico", "pizza", "barra", "plot"])
    pergunta_porcentagem = any(termo in pergunta_limpa for termo in ["porcentagem", "por cento", "percentual"]) or "%" in pergunta_segura
    
    # Gatilhos Estritos de Comparação
    termos_comparacao = [
        "comparar", "reclamar ou", "elogiar ou", "positivas ou", "negativas ou", 
        "elogios ou", "reclamacoes ou", "reclamando ou", "elogiando ou"
    ]
    pede_comparacao = any(t in pergunta_limpa for t in termos_comparacao)
    
    # --- DETEÇÃO DE CATEGORIA 100% SEGURA ---
    categoria_alvo = categoria_forcada
    if not categoria_alvo:
        # Apelidos manuais para evitar que palavras soltas ativem categorias erradas
        apelidos_seguros = {
            "relogio": "relogios_presentes", "relogios": "relogios_presentes",
            "informatica": "informatica_acessorios", "acessorios": "informatica_acessorios",
            "cama": "cama_mesa_banho", "mesa": "cama_mesa_banho", "banho": "cama_mesa_banho",
            "beleza": "beleza_saude", "saude": "beleza_saude",
            "esporte": "esporte_lazer", "lazer": "esporte_lazer",
            "moveis": "moveis_decoracao", "decoracao": "moveis_decoracao",
            "festa": "artigos_de_festas", "festas": "artigos_de_festas",
            "brinquedo": "brinquedos", "brinquedos": "brinquedos",
            "bebe": "bebes", "bebes": "bebes",
            "ferramenta": "construcao_ferramentas_ferramentas", "ferramentas": "construcao_ferramentas_ferramentas",
            "pet": "pet_shop", "petshop": "pet_shop"
        }
        
        palavras = pergunta_limpa.split()
        for p in palavras:
            if p in apelidos_seguros:
                categoria_alvo = apelidos_seguros[p]
                break
                
        # Se não encontrou apelido, procura pelo nome exato longo
        if not categoria_alvo:
            for cat_possivel in categorias_validas:
                cat_mapeada = cat_possivel.replace("_", " ")
                if len(cat_mapeada) > 3 and (cat_mapeada in pergunta_limpa or cat_possivel in pergunta_limpa):
                    categoria_alvo = cat_possivel
                    break

    # --- ROTEAMENTO INTELIGENTE ---
    pede_problemas = False
    pede_ranking = False
    
    if not categoria_alvo and not pede_comparacao:
        termos_problema = ["problema", "problemas", "motivo", "motivos", "defeito", "atraso", "logistica"]
        if any(t in pergunta_limpa for t in termos_problema):
            pede_problemas = True
        
        # Se perguntar quem recebe mais elogios/críticas, mostra o ranking automaticamente
        if not pede_problemas:
            termos_ranking = ["categoria", "categorias", "ranking", "principais", "quais", "top", "maior", "mais"]
            if any(t in pergunta_limpa for t in termos_ranking) or detetar_intencao(pergunta_segura) != "neutra":
                pede_ranking = True

    return {
        "pergunta_segura": pergunta_segura,
        "pergunta_lower": pergunta_lower,
        "pediu_grafico": pediu_grafico,
        "pergunta_porcentagem": pergunta_porcentagem,
        "pede_comparacao": pede_comparacao,
        "categoria_alvo": categoria_alvo,
        "pede_ranking": pede_ranking,
        "pede_problemas": pede_problemas
    }