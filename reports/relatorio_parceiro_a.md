# Relatório de Teste A/B — Parceiro A
**Período:** 01/01/2011 a 02/04/2011  
**Variantes testadas:** 3  
**Arquivo fonte:** `dataset_01_parceiroA.csv`  
**Análise gerada em:** 15/06/2026 11:57  

---

## 1. Métricas Consolidadas por Variante

| Variante | Compradores | GMV Total | Comissão | Cashback | **Lucro Méliuz** | Margem | Cashback/GMV | Ticket Médio | Compradores/dia |
|---|---|---|---|---|---|---|---|---|---|
| Grupo 1 ✅ | 9,633 | R$ 5.605.173,00 | R$ 638.135,00 | R$ 233.424,00 | **R$ 404.711,00** | 63.42% | 4.16% | R$ 581,87 | 104.7 |
| Grupo 2 | 10,814 | R$ 6.423.096,00 | R$ 728.178,00 | R$ 370.659,00 | **R$ 357.519,00** | 49.10% | 5.77% | R$ 593,96 | 117.5 |
| Grupo 3 | 11,410 | R$ 6.785.856,00 | R$ 767.887,00 | R$ 503.600,00 | **R$ 264.287,00** | 34.42% | 7.42% | R$ 594,73 | 124.0 |

---

## 2. Significância Estatística

Teste t de Student — compradores diários de cada variante vs. Grupo 1 (controle).  
Nível de confiança adotado: **95% (α = 0,05)**

| Comparação | p-value | Significativo? |
|---|---|---|
| Grupo 1 vs Grupo 2 | 0.1349 | ❌ Não |
| Grupo 1 vs Grupo 3 | 0.0338 | ✅ Sim |

---

## 3. Análise de Rentabilidade

**Variante Vencedora: Grupo 1**

O controle se manteve como variante mais rentável.
- Margem operacional: **63.42%**
- Lucro total: **R$ 404.711,00**

---

## 4. Decisão e Recomendação

> **Escalar para 100% do tráfego: Grupo 1**

Nenhuma variante apresentou ganho estatisticamente significativo em compradores. O Grupo 1 (controle) permanece como melhor opção por ter a maior margem operacional.

### Observações importantes

- Ticket médio estável entre variantes (~R$ 590,19) — o cashback não alterou o comportamento de compra por pedido.
- Recomenda-se monitorar retenção e LTV após escalonamento.
