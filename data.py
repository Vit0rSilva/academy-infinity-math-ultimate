"""Conteúdo acadêmico da plataforma.

O catálogo fica em código para que as páginas sejam rápidas e fáceis de versionar.
O banco de dados guarda somente dados mutáveis: usuários, progresso e tentativas.
"""

MODULES = [
    {
        "slug": "conjuntos-logica",
        "number": 1,
        "level": "Iniciante",
        "icon": "🧠",
        "title": "Conjuntos e Lógica Matemática",
        "summary": "Fundamentos de conjuntos, proposições, conectivos e demonstração.",
        "objectives": [
            "Operar união, interseção e diferença de conjuntos.",
            "Construir e interpretar tabelas-verdade.",
            "Reconhecer tautologias, contradições e contingências.",
        ],
        "lessons": [
            {"title": "Conjuntos e relações", "body": "Pertinência relaciona elemento e conjunto; inclusão relaciona dois conjuntos. As operações básicas são união, interseção, diferença e complemento."},
            {"title": "Proposições e conectivos", "body": "Uma proposição possui valor verdadeiro ou falso. Negação, conjunção, disjunção, implicação e equivalência permitem formar expressões compostas."},
            {"title": "Quantificadores e prova", "body": "Os quantificadores universal e existencial formalizam afirmações. Contraexemplos refutam universais; argumentos válidos sustentam conclusões."},
        ],
        "example": "Se A = {1, 2, 3} e B = {3, 4}, então A ∩ B = {3} e A ∪ B = {1, 2, 3, 4}.",
    },
    {
        "slug": "espacos-euclidianos",
        "number": 2,
        "level": "Intermediário",
        "icon": "📐",
        "title": "Espaços Euclidianos",
        "summary": "Vetores, bases, dimensão, norma, produto interno e subespaços.",
        "objectives": [
            "Verificar se um conjunto é subespaço vetorial.",
            "Determinar dependência linear, base e dimensão.",
            "Calcular norma, distância e produto interno.",
        ],
        "lessons": [
            {"title": "Vetores em Rⁿ", "body": "Vetores representam grandezas com componentes. Soma e multiplicação por escalar obedecem aos axiomas do espaço vetorial."},
            {"title": "Base e dimensão", "body": "Uma base é um conjunto linearmente independente que gera o espaço. A quantidade de vetores da base é a dimensão."},
            {"title": "Geometria euclidiana", "body": "O produto interno mede alinhamento; dele surgem norma, distância, ângulo e ortogonalidade."},
        ],
        "example": "u=(1,2) e v=(3,4): u·v=11 e ||u||=√5.",
    },
    {
        "slug": "transformacoes-lineares",
        "number": 3,
        "level": "Avançado",
        "icon": "🔄",
        "title": "Transformações Lineares",
        "summary": "Núcleo, imagem, matrizes, posto e isomorfismos.",
        "objectives": [
            "Testar a linearidade de uma transformação.",
            "Calcular núcleo, imagem e posto.",
            "Reconhecer transformações inversíveis.",
        ],
        "lessons": [
            {"title": "Definição e matriz", "body": "Uma transformação linear preserva soma e multiplicação escalar e pode ser representada por uma matriz depois da escolha de bases."},
            {"title": "Núcleo e imagem", "body": "O núcleo contém vetores levados ao zero. A imagem contém todos os resultados possíveis da transformação."},
            {"title": "Isomorfismos", "body": "Uma transformação bijetora preserva a estrutura entre espaços. Em matrizes quadradas, determinante não nulo garante inversibilidade."},
        ],
        "example": "T(x,y)=(2x+y,x+3y) tem matriz [[2,1],[1,3]] e det=5, logo é inversível.",
    },
    {
        "slug": "sequencias-filas",
        "number": 4,
        "level": "Master",
        "icon": "📈",
        "title": "Sequências e Teoria de Filas",
        "summary": "P.A., P.G. e modelos M/M/1 para sistemas de atendimento.",
        "objectives": [
            "Calcular termos e somas de P.A. e P.G.",
            "Interpretar taxas de chegada e atendimento.",
            "Avaliar estabilidade e desempenho de filas M/M/1.",
        ],
        "lessons": [
            {"title": "Progressão aritmética", "body": "Na P.A., a diferença entre termos consecutivos é constante: aₙ=a₁+(n−1)r."},
            {"title": "Progressão geométrica", "body": "Na P.G., a razão entre termos consecutivos é constante: aₙ=a₁qⁿ⁻¹."},
            {"title": "Fila M/M/1", "body": "Com chegadas e serviços exponenciais e um servidor, o sistema é estável quando λ<μ; sua utilização é ρ=λ/μ."},
        ],
        "example": "Para λ=8 e μ=10 clientes/h, ρ=0,8 e L=λ/(μ−λ)=4 clientes.",
    },
    {
        "slug": "modelagem-matematica",
        "number": 5,
        "level": "Especialista",
        "icon": "🧩",
        "title": "Modelagem Matemática Aplicada",
        "summary": "Do problema real ao modelo, calibração, validação, simulação e decisão.",
        "objectives": [
            "Traduzir situações reais em variáveis, parâmetros e hipóteses.",
            "Construir e comparar modelos lineares, exponenciais e logísticos.",
            "Calibrar, validar e comunicar as limitações de um modelo.",
            "Executar análise de sensibilidade e cenários.",
        ],
        "lessons": [
            {"title": "Ciclo de modelagem", "body": "Defina o problema, escolha variáveis e hipóteses, formule relações matemáticas, resolva, valide e refine. Um modelo é uma representação útil, não uma cópia perfeita da realidade."},
            {"title": "Modelos de crescimento", "body": "O modelo linear possui taxa absoluta constante; o exponencial possui taxa relativa constante; o logístico inclui capacidade de suporte e saturação."},
            {"title": "Calibração e validação", "body": "Calibrar é estimar parâmetros com dados. Validar é confrontar previsões com dados não usados no ajuste, analisando resíduos e métricas de erro."},
            {"title": "Simulação e sensibilidade", "body": "Cenários revelam consequências das hipóteses. A sensibilidade mede como pequenas mudanças em parâmetros afetam a saída e identifica fatores críticos."},
        ],
        "example": "Para uma população com limite K, o modelo logístico P(t)=K/(1+Ae⁻ʳᵗ) representa crescimento inicial rápido seguido de saturação.",
    },
]


QUIZZES = {
    "conjuntos-logica": [
        {"id": 1, "question": "Se A={1,2,3} e B={3,4}, qual é A∩B?", "options": ["{1,2,4}", "{3}", "{1,2,3,4}", "∅"], "answer": 1, "explanation": "A interseção reúne os elementos comuns aos dois conjuntos."},
        {"id": 2, "question": "A expressão P ∨ ¬P é classificada como:", "options": ["Contradição", "Contingência", "Tautologia", "Implicação"], "answer": 2, "explanation": "Ela é verdadeira para qualquer valor de P."},
        {"id": 3, "question": "Qual símbolo representa o quantificador universal?", "options": ["∃", "∀", "∈", "⊂"], "answer": 1, "explanation": "∀ significa 'para todo'."},
    ],
    "espacos-euclidianos": [
        {"id": 1, "question": "Dois vetores em R² formam uma base quando:", "options": ["São iguais", "São ortogonais apenas", "São linearmente independentes", "Têm norma 1"], "answer": 2, "explanation": "Dois vetores LI geram R² e formam uma base."},
        {"id": 2, "question": "Qual é o produto interno de (1,2) e (3,4)?", "options": ["7", "10", "11", "14"], "answer": 2, "explanation": "1·3 + 2·4 = 11."},
        {"id": 3, "question": "A norma de (3,4) é:", "options": ["5", "7", "12", "25"], "answer": 0, "explanation": "√(3²+4²)=5."},
    ],
    "transformacoes-lineares": [
        {"id": 1, "question": "Uma matriz quadrada representa um isomorfismo quando:", "options": ["Seu determinante é zero", "É triangular", "Seu determinante é não nulo", "Tem apenas zeros"], "answer": 2, "explanation": "Determinante não nulo equivale a matriz inversível."},
        {"id": 2, "question": "Para uma transformação ser injetora, seu núcleo deve ser:", "options": ["Todo o domínio", "Apenas o vetor nulo", "Igual à imagem", "Vazio"], "answer": 1, "explanation": "ker(T)={0} é o critério de injetividade linear."},
        {"id": 3, "question": "T(x,y)=(x+y,2x+2y) possui imagem de dimensão:", "options": ["0", "1", "2", "3"], "answer": 1, "explanation": "A segunda componente é duas vezes a primeira; o posto é 1."},
    ],
    "sequencias-filas": [
        {"id": 1, "question": "Em uma P.A. com a₁=2 e r=3, qual é a₄?", "options": ["8", "9", "11", "14"], "answer": 2, "explanation": "a₄=2+(4−1)·3=11."},
        {"id": 2, "question": "Uma fila M/M/1 é estável quando:", "options": ["λ>μ", "λ=μ", "λ<μ", "λ=0 apenas"], "answer": 2, "explanation": "A taxa de serviço precisa superar a taxa de chegada."},
        {"id": 3, "question": "Se λ=6 e μ=10, a utilização ρ é:", "options": ["0,4", "0,6", "1,6", "4"], "answer": 1, "explanation": "ρ=λ/μ=6/10=0,6."},
    ],
    "modelagem-matematica": [
        {"id": 1, "question": "Qual é a primeira etapa de um bom ciclo de modelagem?", "options": ["Escolher uma fórmula sofisticada", "Definir claramente o problema e o objetivo", "Eliminar todos os dados", "Publicar o resultado"], "answer": 1, "explanation": "O objetivo define quais variáveis, dados e simplificações são relevantes."},
        {"id": 2, "question": "Qual modelo é mais adequado para crescimento com saturação?", "options": ["Linear", "Logístico", "P.A.", "Constante"], "answer": 1, "explanation": "O modelo logístico inclui uma capacidade de suporte."},
        {"id": 3, "question": "Validar um modelo significa:", "options": ["Ajustar parâmetros e encerrar", "Comparar previsões com dados independentes", "Garantir que ele seja perfeito", "Adicionar mais variáveis sempre"], "answer": 1, "explanation": "A validação avalia a capacidade preditiva fora dos dados de calibração."},
        {"id": 4, "question": "A análise de sensibilidade investiga:", "options": ["A estética dos gráficos", "O efeito de mudanças nos parâmetros sobre as saídas", "Somente o tempo de execução", "A autoria dos dados"], "answer": 1, "explanation": "Ela identifica os parâmetros que mais influenciam os resultados."},
        {"id": 5, "question": "Um modelo matemático deve ser entendido como:", "options": ["Uma cópia exata da realidade", "Uma representação simplificada adequada a um objetivo", "Uma prova de certeza absoluta", "Um conjunto sem hipóteses"], "answer": 1, "explanation": "Todo modelo simplifica e depende de hipóteses e finalidade."},
    ],
}


def get_module(slug):
    """Retorna um módulo pelo slug ou ``None``."""
    return next((module for module in MODULES if module["slug"] == slug), None)
