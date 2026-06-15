# Relatório de Teste A/B — Parceiro C
**Período:** 01/07/2011 a 14/08/2011  
**Variantes testadas:** 2  
**Arquivo fonte:** `dataset_03_parceiroC.csv`  
**Análise gerada em:** 15/06/2026 11:57  

---

## 1. Métricas Consolidadas por Variante

| Variante | Compradores | GMV Total | Comissão | Cashback | **Lucro Méliuz** | Margem | Cashback/GMV | Ticket Médio | Compradores/dia |
|---|---|---|---|---|---|---|---|---|---|
| Grupo 1 ✅ | 4,549 | R$ 1.738.460,00 | R$ 121.693,00 | R$ 86.924,00 | **R$ 34.769,00** | 28.57% | 5.00% | R$ 382,16 | 101.1 |
| Grupo 2 | 4,522 | R$ 1.685.235,00 | R$ 117.967,00 | R$ 117.967,00 | **R$ 0,00** | 0.00% | 7.00% | R$ 372,67 | 100.5 |

---

## 2. Significância Estatística

Teste t de Student — compradores diários de cada variante vs. Grupo 1 (controle).  
Nível de confiança adotado: **95% (α = 0,05)**

| Comparação | p-value | Significativo? |
|---|---|---|
| Grupo 1 vs Grupo 2 | 0.9218 | ❌ Não |

---

## 3. Análise de Rentabilidade

**Variante Vencedora: Grupo 1**

O controle se manteve como variante mais rentável.
- Margem operacional: **28.57%**
- Lucro total: **R$ 34.769,00**

---

## 4. Decisão e Recomendação

> **Escalar para 100% do tráfego: Grupo 1**

Nenhuma variante apresentou ganho estatisticamente significativo em compradores. O Grupo 1 (controle) permanece como melhor opção por ter a maior margem operacional.

### Observações importantes

⚠️ **Grupo 2 operou com lucro zero ou negativo** — o cashback consumiu toda a comissão. Evitar esse nível de cashback.
- Ticket médio estável entre variantes (~R$ 377,42) — o cashback não alterou o comportamento de compra por pedido.
- Recomenda-se monitorar retenção e LTV após escalonamento.
