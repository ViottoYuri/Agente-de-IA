import streamlit as st
import re
import json
from typing import Dict, List
from groq import Groq
import streamlit as st

# ==========================================================
# CONFIGURAÇÃO E INICIALIZAÇÃO DO CLIENTE GROQ
# ==========================================================

# Tenta pegar a chave do Streamlit Secrets
try:
    # Acessa a chave diretamente
    api_key = st.secrets["GROQ_API_KEY"] 
except KeyError:
    # Caso a chave não exista no secrets (exige que o arquivo secrets.toml esteja correto)
    st.error("❌ A chave **GROQ_API_KEY** não está definida nos secrets do Streamlit! Verifique o arquivo `.streamlit/secrets.toml` ou a configuração de secrets na Cloud.")
    st.stop()

# Tenta inicializar o cliente Groq
try:
    client = Groq(api_key=api_key)
except Exception as e:
    # Captura qualquer erro que possa ocorrer na inicialização do cliente (incluindo o TypeError)
    st.error(f"❌ Erro ao inicializar o cliente Groq. Isso pode ser um problema de versão ou de ambiente. Detalhes do erro: {e}")
    st.stop()


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
    # return all(re.fullmatch(pattern, ch) for ch in formula)
    
    # Validação mais simples, apenas verifica se a fórmula contém caracteres não permitidos
    caracteres_invalidos = re.findall(r"[^A-Z¬∧V→↔()\s]", formula)
    return not bool(caracteres_invalidos)


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

    # A função call_llm agora está disponível, garantindo que o cliente Groq foi inicializado
    formula = call_llm(prompt)

    #Mantém símbolos definidos pelo usuário
    
    for simb, desc in significados.items():
        if desc.lower() in texto.lower():
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
            try:
                simb, desc = linha.split("=", 1) # Usar 1 para garantir que a descrição possa conter "="
                simb = simb.strip()
                # Remove aspas duplas, simples e espaços em branco da descrição
                desc = desc.strip().replace('"', "").replace("'", "") 
                if simb and desc:
                    mapeamento[simb] = desc
            except ValueError:
                # Ignora linhas mal formatadas
                continue

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
        # Normaliza as chaves do dicionário de significados (apenas letras maiúsculas)
        significados_validos = {k: v for k, v in st.session_state.significados.items() if k.isupper()}
        
        with st.spinner("Traduzindo para CPC..."):
            formula = nl_para_cpc(texto_nl, significados_validos)
            st.success("Fórmula gerada:")
            st.code(formula, language="text")

if st.button("Sugerir proposições"):
    if texto_nl.strip() == "":
        st.warning("Digite uma frase para sugerir proposições.")
    else:
        with st.spinner("Gerando sugestões..."):
            sugestoes = sugerir_proposicoes(texto_nl)
            
            if sugestoes:
                st.write("Sugestões do sistema:")
                st.json(sugestoes)
                
                # Garante que apenas letras maiúsculas sejam adicionadas
                sugestoes_validas = {k: v for k, v in sugestoes.items() if k.isupper() and len(k) == 1}
                st.session_state.significados.update(sugestoes_validas)
            else:
                st.info("Nenhuma sugestão de proposição foi gerada.")


# ==========================================================
# CPC → NL
# ==========================================================

st.header("⚙️ Fórmula Proposicional → Linguagem Natural")
texto_cpc = st.text_input("Digite a fórmula lógica:", "")

if st.button("Gerar frase (CPC → NL)"):
    if not validar_formula(texto_cpc):
        st.error("Fórmula inválida. Use apenas letras maiúsculas (A-Z), operadores lógicos (¬, ∧, V, →, ↔) e parênteses.")
    else:
        # Normaliza as chaves do dicionário de significados
        significados_validos = {k: v for k, v in st.session_state.significados.items() if k.isupper()}
        
        with st.spinner("Traduzindo para Linguagem Natural..."):
            frase = cpc_para_nl(texto_cpc, significados_validos)
            st.success("Frase gerada:")
            st.write(frase)
