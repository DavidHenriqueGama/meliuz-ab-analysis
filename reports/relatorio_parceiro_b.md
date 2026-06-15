# Relatório de Teste A/B — Parceiro B
**Período:** 01/05/2011 a 30/06/2011  
**Variantes testadas:** 3  
**Arquivo fonte:** `dataset_02_parceiroB.csv`  
**Análise gerada em:** 15/06/2026 11:57  

---

## 1. Métricas Consolidadas por Variante

| Variante | Compradores | GMV Total | Comissão | Cashback | **Lucro Méliuz** | Margem | Cashback/GMV | Ticket Médio | Compradores/dia |
|---|---|---|---|---|---|---|---|---|---|
| Grupo 1 ✅ | 7,990 | R$ 4.093.818,00 | R$ 450.321,00 | R$ 163.751,00 | **R$ 286.570,00** | 63.64% | 4.00% | R$ 512,37 | 131.0 |
| Grupo 2 | 5,452 | R$ 2.863.019,00 | R$ 314.935,00 | R$ 171.778,00 | **R$ 143.157,00** | 45.46% | 6.00% | R$ 525,13 | 89.4 |
| Grupo 3 | 5,029 | R$ 2.629.963,00 | R$ 289.290,00 | R$ 236.697,00 | **R$ 52.593,00** | 18.18% | 9.00% | R$ 522,96 | 82.4 |

---

## 2. Significância Estatística

Teste t de Student — compradores diários de cada variante vs. Grupo 1 (controle).  
Nível de confiança adotado: **95% (α = 0,05)**

| Comparação | p-value | Significativo? |
|---|---|---|
| Grupo 1 vs Grupo 2 | 0.0000 | ✅ Sim |
| Grupo 1 vs Grupo 3 | 0.0000 | ✅ Sim |

---

## 3. Análise de Rentabilidade

**Variante Vencedora: Grupo 1**

O controle se manteve como variante mais rentável.
- Margem operacional: **63.64%**
- Lucro total: **R$ 286.570,00**

---

## 4. Decisão e Recomendação

> **Escalar para 100% do tráfego: Grupo 1**

Nenhuma variante apresentou ganho estatisticamente significativo em compradores. O Grupo 1 (controle) permanece como melhor opção por ter a maior margem operacional.

### Observações importantes

⚠️ **Cashback acima de 8% do GMV** em ao menos uma variante — risco de unsustainability.
- Ticket médio estável entre variantes (~R$ 520,15) — o cashback não alterou o comportamento de compra por pedido.
- Recomenda-se monitorar retenção e LTV após escalonamento.
