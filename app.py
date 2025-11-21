import streamlit as st
import re
import json
from typing import Dict, List
from groq import Groq
import streamlit as st

# Pega a chave do Streamlit Secrets
api_key = st.secrets.get("GROQ_API_KEY")

if not api_key:
    st.error("❌ A chave GROQ_API_KEY não está definida nos secrets!")
    st.stop()

client = Groq(api_key=api_key)

def call_llm(prompt: str, temperature=0.1):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature
    )
    return response.choices[0].message.content.strip()


# ==========================================================
# FUNÇÕES DE APOIO
# ==========================================================

def extrair_simbolos(formula: str) -> List[str]:
    return sorted(set(re.findall(r"\b[A-Z]\b", formula)))

def validar_formula(formula: str) -> bool:
    pattern = r"[A-Z]|¬|∧|V|→|↔|\(|\)|\s"
    return all(re.fullmatch(pattern, ch) for ch in formula)


# ==========================================================
# TRADUTOR: NL → CPC
# ==========================================================

def nl_para_cpc(texto: str, significados: Dict[str, str]):
    prompt = f"""
Você é um tradutor especializado em lógica proposicional.

Converta o texto abaixo em uma fórmula do Cálculo Proposicional Clássico (CPC).

Regras:
- Use proposições atômicas como P, Q, R, S, T...
- Operadores permitidos: ¬, ∧, V, →, ↔
- Use parênteses quando necessário.
- NÃO explique. Apenas retorne a fórmula.

Texto: "{texto}"

Se houver ambiguidade, mantenha a forma mais simples possível.
    """

    formula = call_llm(prompt)

    # Mantém símbolos definidos pelo usuário
    for simb, desc in significados.items():
        if desc.lower() in texto.lower():
            formula = formula.replace(simb, simb)

    return formula


# ==========================================================
# TRADUTOR: CPC → NL
# ==========================================================

def cpc_para_nl(formula: str, significados: Dict[str, str]):
    prompt = f"""
Você é um tradutor especializado em lógica proposicional.

Explique a fórmula abaixo em português claro.

Fórmula: {formula}

Substitua os símbolos usando:
{json.dumps(significados, indent=2)}

Retorne uma frase natural e clara.
    """
    return call_llm(prompt)


# ==========================================================
# SUGESTOR DE PROPOSIÇÕES
# ==========================================================

def sugerir_proposicoes(texto: str):
    prompt = f"""
Analise a frase abaixo e sugira proposições atômicas (P, Q, R...) com descrições.

Formato:
P = "..."
Q = "..."
R = "..."

Texto: "{texto}"
    """

    saida = call_llm(prompt)
    linhas = saida.split("\n")

    mapeamento = {}
    for linha in linhas:
        if "=" in linha:
            simb, desc = linha.split("=")
            simb = simb.strip()
            desc = desc.replace('"', "").strip()
            mapeamento[simb] = desc

    return mapeamento


# ==========================================================
# INTERFACE STREAMLIT
# ==========================================================

st.title("🔁 Tradutor NL ↔ Lógica Proposicional (CPC)")
st.write("Tradução automática entre linguagem natural e fórmulas do Cálculo Proposicional Clássico — agora usando **Groq (Llama 3.1)** 🚀")


# Tabela de significados
st.subheader("📌 Definição das Proposições")

if "significados" not in st.session_state:
    st.session_state.significados = {"P": "proposição 1", "Q": "proposição 2"}

st.session_state.significados = st.data_editor(
    st.session_state.significados,
    num_rows="dynamic",
    key="tabela"
)

st.divider()


# ==========================================================
# NL → CPC
# ==========================================================

st.header("📝 Linguagem Natural → Fórmula Proposicional")
texto_nl = st.text_area("Digite a frase:", "")

if st.button("Gerar fórmula (NL → CPC)"):
    if texto_nl.strip() == "":
        st.warning("Digite uma frase.")
    else:
        formula = nl_para_cpc(texto_nl, st.session_state.significados)
        st.success("Fórmula gerada:")
        st.code(formula, language="text")

if st.button("Sugerir proposições"):
    sugestoes = sugerir_proposicoes(texto_nl)
    st.write("Sugestões do sistema:")
    st.json(sugestoes)
    st.session_state.significados.update(sugestoes)


# ==========================================================
# CPC → NL
# ==========================================================

st.header("⚙️ Fórmula Proposicional → Linguagem Natural")
texto_cpc = st.text_input("Digite a fórmula lógica:", "")

if st.button("Gerar frase (CPC → NL)"):
    if not validar_formula(texto_cpc):
        st.error("Fórmula inválida. Use apenas A-Z, ¬, ∧, V, →, ↔, parênteses.")
    else:
        frase = cpc_para_nl(texto_cpc, st.session_state.significados)
        st.success("Frase gerada:")
        st.write(frase)
