# Méliuz Growth — Solução Reutilizável de Análise de Testes A/B

## Sobre

Solução desenvolvida para o teste técnico da vaga de **Estágio de Growth AI-Native** da Méliuz.

Automatiza a análise de testes A/B de cashback, eliminando o trabalho manual de 2–4h por teste.
Basta indicar um novo CSV no schema padrão que a solução entrega o relatório completo e registra no tracker.

---

## Estrutura do Repositório

```
meliuz-ab-analysis/
├── analyze_ab.py          # Script principal (reutilizável)
├── ab_tracker.csv         # Planilha de acompanhamento (gerada automaticamente)
├── datasets/              # CSVs de entrada
│   ├── dataset_01_parceiroA.csv
│   ├── dataset_02_parceiroB.csv
│   └── dataset_03_parceiroC.csv
├── reports/               # Relatórios gerados
│   ├── relatorio_parceiro_a.md
│   ├── relatorio_parceiro_b.md
│   └── relatorio_parceiro_c.md
├── requirements.txt
└── README.md
```

---

## Como Rodar

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Analisar um teste

```bash
python analyze_ab.py datasets/dataset_01_parceiroA.csv
```

Para qualquer novo teste, basta trocar o arquivo:

```bash
python analyze_ab.py datasets/dataset_novo_parceiroX.csv
```

**Não é necessário alterar nada no código.** A solução detecta automaticamente o parceiro, o período e os grupos.

### 3. Ver o tracker de testes

O arquivo `ab_tracker.csv` é atualizado automaticamente a cada análise e pode ser importado no Google Sheets.

---

## O Que a Solução Faz

Para cada dataset, o script:

1. **Lê e limpa** os dados (converte moeda BRL, trata tipos)
2. **Calcula métricas** por variante:
   - GMV total e por dia
   - Comissão, cashback e **lucro líquido do Méliuz**
   - Margem operacional (%)
   - Cashback como % do GMV
   - Ticket médio e compradores por dia
3. **Testa significância estatística** (t-test, α = 0,05) comparando compradores diários de cada variante vs. o controle (Grupo 1)
4. **Decide o vencedor** com base em lucro total — priorizando variantes com diferença significativa; fallback para o controle
5. **Gera relatório Markdown** pronto para apresentação
6. **Registra no tracker CSV** com nome do teste, período, vencedor, margem e decisão

---

## Critério de Decisão

> **Pergunta central:** Qual variante devemos escalar para 100% do tráfego?

A lógica segue esta hierarquia:

1. Somente variantes com **p-value < 0,05** frente ao controle entram na disputa de escalonamento
2. Entre as elegíveis, vence quem tiver **maior lucro total** (comissão − cashback)
3. Em empate de lucro, desempate por **GMV total**
4. Se nenhuma variante bate o controle com significância, **o controle vence** (menor risco)

---

## Resultados dos 3 Testes

| Parceiro | Período | Vencedor | Margem | Lucro Total |
|---|---|---|---|---|
| Parceiro A | Jan–Abr 2011 | **Grupo 1** | 63,4% | R$ 404.711 |
| Parceiro B | Mai–Jun 2011 | **Grupo 1** | 63,6% | R$ 286.570 |
| Parceiro C | Jul–Ago 2011 | **Grupo 1** | 28,6% | R$ 34.769 |

Em todos os testes, cashback maior gerou mais compradores mas destruiu margem sem compensação suficiente em volume.

---

## Requisitos

```
pandas>=2.0
scipy>=1.10
numpy>=1.24
```

---

## Uso com IA (Claude Code / Cursor / GPT)

Esta solução foi arquitetada para funcionar por linguagem natural. Em qualquer ferramenta de IA com acesso ao terminal:

> "Analise o teste A/B do arquivo `datasets/dataset_novo.csv` e me diga qual variante escalar."

A IA executa `python analyze_ab.py datasets/dataset_novo.csv` e retorna o relatório completo.

O script é parametrizado e robusto: funciona com qualquer número de variantes e qualquer parceiro, sem alteração de código.
