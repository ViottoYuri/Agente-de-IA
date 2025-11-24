# Agente-de-IA

Desenho da arquitetura:
+-------------------------+
|  Interface Web (UI)     |
|  (Streamlit / Flask)    |
+-----------+-------------+
            |
            v
+-------------------------+
|  Módulo Tradutor        |
|  a) NL → Lógica         |
|  b) Lógica → NL         |
+-----------+-------------+
            |
            v
+-------------------------+
|  Processamento Linguístico|
|  (spaCy / NLTK / Regras) |
+-----------+-------------+
            |
            v
+-------------------------+
|    Modelo LLM (API)     |
| (ChatGPT / HuggingFace) |
+-----------+-------------+
            |
            v
+-------------------------+
|  Módulo de Avaliação    |
|  Verificação semântica  |
+-------------------------+

Explicaçã de funcionamento:

1 - Usuário envia uma frase em NL (linguagem natural) ou uma fórmula CPC.
2 - A interface web captura o texto e envia para o Módulo Tradutor.
3 - O tradutor:
  .Identifica operadores ("e", "ou", "não", "se... então")
  .Mapeia para símbolos lógicos (∧, ∨, ¬, →)
  .Se necessário, chama o modelo LLM para interpretar frases mais complexas.
4 - A tradução passa pelo módulo linguístico, que ajusta:
  .Desambiguação,
  .Normalização,
  .Identificação de proposições.
5 - O Módulo de Avaliação verifica:
  .Estrutura lógica,
  .Parênteses,
  .Operadores válidos,
Contradições óbvias.
6 - O resultado é exibido na interface.
Regtra de tradução:

 NL -> CPC
| Linguagem Natural | Operador Lógico |
| ----------------- | --------------- |
| e / ambos         | ∧               |
| ou                | ∨               |
| não               | ¬               |
| se ... então      | →               |
| se e somente se   | ↔               |

O sistema permite que o usuário defina a proposição Ou usa identificação automática:

Substantivos → variáveis
Eventos → proposições simples

Uso de LLMs:

O modelo é utilizado quando:
Existem ambiguidades (“ou exclusivo”, “ou inclusivo”, “logo”, “pois”).
Frases longas ou compostas com múltiplas camadas.
Tradução inversa (CPC → NL) mantendo naturalidade.

Exemplos de Input/Output:

1 - (NL -> CPC) - Entrada: "Se chover então fico em casa."
    Saida: P → Q | P = chover | Q = ficar em casa.
Acerto: interpretação correta da estrutura condicional.
Erros: o texto de entrada pode ser ambíguo se houver contexto adicional.

2 - (CPC -> NL) - Entrada - ¬P ∧ (Q ∨ R)
    Saida: “Não P e (Q ou R).”.
Erros e acertos:
  Acerto: ordem e parênteses preservados.
  Erros: pouco natural; poderia gerar frase mais fluida.

Limitações e possibilidades de melhoria:

Limitações:
Dificuldade com ambiguidades semânticas (“ou exclusivo”).
Frases longas demais podem gerar traduções incompletas.
O usuário precisa definir proposições manualmente às vezes.
LLMs podem:
inventar proposições,
ignorar detalhes sutis,
alterar relações lógicas se a frase for mal formulada.

Melhorias:
Criar parser sintático próprio para NL → lógica proposicional.
Adicionar modo pedagógico, explicando cada passo da tradução.
Treinar modelo próprio com dataset específico (NL ↔ CPC).

Link do video do agente funcionando:
https://1drv.ms/v/c/3d4921b29891711b/IQCGsTwy8UdHQol6kbGwRkzcAWFDN4oXZiHJ1DhoEpjALko
