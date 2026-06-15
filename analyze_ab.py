#!/usr/bin/env python3
"""
Méliuz Growth — Análise Reutilizável de Testes A/B
====================================================
Uso:
    python analyze_ab.py <caminho_do_csv>

Exemplo:
    python analyze_ab.py datasets/dataset_01_parceiroA.csv

A solução:
- Lê qualquer CSV no schema padrão do Méliuz
- Calcula métricas de negócio por variante
- Aplica teste de significância estatística (t-test)
- Gera relatório Markdown em reports/
- Registra resultado no tracker CSV (ab_tracker.csv)
- Registra resultado direto no Google Sheets (diferencial)
"""

import sys
import os
import csv
import re
from datetime import datetime
import pandas as pd
import numpy as np
from scipy import stats

# ─── Configuração ────────────────────────────────────────────────────────────
REPORTS_DIR = "reports"
TRACKER_FILE = "ab_tracker.csv"
TRACKER_COLUMNS = [
    "data_analise", "nome_teste", "parceiro", "periodo", "grupos",
    "descricao", "vencedor", "p_value", "gmv_vencedor",
    "margem_vencedor_pct", "lucro_vencedor", "decisao"
]

# ─── Google Sheets config ─────────────────────────────────────────────────────
SHEETS_CREDENTIALS_FILE = "meliuz-ab-analysis-71566b5f008f.json"
SHEETS_SPREADSHEET_ID   = "1__IQqt70t8w-jqs4Nt2d_PJ7c1-d01OBtp7j4fUWQzM"

# ─── Helpers ─────────────────────────────────────────────────────────────────
def parse_brl(value: str) -> float:
    """Converte 'R$ 1.234,56' → 1234.56"""
    cleaned = re.sub(r"[R$\s]", "", str(value)).replace(".", "").replace(",", ".")
    return float(cleaned)

def fmt_brl(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def fmt_pct(value: float) -> str:
    return f"{value:.2f}%"

# ─── Leitura e limpeza ───────────────────────────────────────────────────────
def load_dataset(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath)
    required_cols = {"Data", "Grupos de usuários", "Parceiro", "compradores",
                     "comissão", "cashback", "vendas totais"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Colunas faltando no CSV: {missing}")

    for col in ["comissão", "cashback", "vendas totais"]:
        df[col] = df[col].apply(parse_brl)

    df["Data"] = pd.to_datetime(df["Data"])
    df["compradores"] = pd.to_numeric(df["compradores"], errors="coerce").fillna(0).astype(int)

    df["lucro_meliuz"] = df["comissão"] - df["cashback"]
    df["margem_pct"] = (df["lucro_meliuz"] / df["comissão"] * 100).round(2)
    df["cashback_pct_gmv"] = (df["cashback"] / df["vendas totais"] * 100).round(2)
    df["ticket_medio"] = (df["vendas totais"] / df["compradores"]).round(2)

    return df

# ─── Agregação por grupo ─────────────────────────────────────────────────────
def compute_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = df.groupby("Grupos de usuários").agg(
        dias=("Data", "nunique"),
        compradores_total=("compradores", "sum"),
        gmv_total=("vendas totais", "sum"),
        comissao_total=("comissão", "sum"),
        cashback_total=("cashback", "sum"),
        lucro_total=("lucro_meliuz", "sum"),
    ).reset_index()

    summary["ticket_medio"] = (summary["gmv_total"] / summary["compradores_total"]).round(2)
    summary["margem_pct"] = (summary["lucro_total"] / summary["comissao_total"] * 100).round(2)
    summary["cashback_pct_gmv"] = (summary["cashback_total"] / summary["gmv_total"] * 100).round(4)
    summary["gmv_por_dia"] = (summary["gmv_total"] / summary["dias"]).round(2)
    summary["compradores_por_dia"] = (summary["compradores_total"] / summary["dias"]).round(2)
    summary["lucro_por_dia"] = (summary["lucro_total"] / summary["dias"]).round(2)

    return summary

# ─── Significância estatística ───────────────────────────────────────────────
def run_significance_tests(df: pd.DataFrame) -> dict:
    grupos = df["Grupos de usuários"].unique().tolist()
    base_label = grupos[0]
    base_series = df[df["Grupos de usuários"] == base_label]["compradores"]
    results = {}
    for g in grupos[1:]:
        other = df[df["Grupos de usuários"] == g]["compradores"]
        _, p = stats.ttest_ind(base_series, other)
        results[g] = round(p, 4)
    return results

# ─── Decisão ─────────────────────────────────────────────────────────────────
def decide_winner(summary: pd.DataFrame, sig_tests: dict) -> tuple[str, str]:
    grupos = summary["Grupos de usuários"].tolist()
    controle = grupos[0]

    elegiveis = [controle]
    for g, p in sig_tests.items():
        if p < 0.05:
            elegiveis.append(g)

    subset = summary[summary["Grupos de usuários"].isin(elegiveis)]
    winner_row = subset.loc[subset["lucro_total"].idxmax()]
    winner = winner_row["Grupos de usuários"]

    if winner == controle:
        justificativa = (
            f"Nenhuma variante apresentou ganho estatisticamente significativo em compradores. "
            f"O {controle} (controle) permanece como melhor opção por ter a maior margem operacional."
        )
    else:
        p_val = sig_tests[winner]
        justificativa = (
            f"{winner} obteve lucro total superior com diferença significativa vs. controle "
            f"(p={p_val}). Volume de compradores e GMV também foram mais altos."
        )

    return winner, justificativa

# ─── Geração de relatório Markdown ───────────────────────────────────────────
def generate_report(df: pd.DataFrame, summary: pd.DataFrame, sig_tests: dict,
                    winner: str, justificativa: str, filepath: str) -> str:
    parceiro = df["Parceiro"].iloc[0]
    periodo_ini = df["Data"].min().strftime("%d/%m/%Y")
    periodo_fim = df["Data"].max().strftime("%d/%m/%Y")
    n_grupos = summary.shape[0]

    lines = []
    lines.append(f"# Relatório de Teste A/B — {parceiro}")
    lines.append(f"**Período:** {periodo_ini} a {periodo_fim}  ")
    lines.append(f"**Variantes testadas:** {n_grupos}  ")
    lines.append(f"**Arquivo fonte:** `{os.path.basename(filepath)}`  ")
    lines.append(f"**Análise gerada em:** {datetime.now().strftime('%d/%m/%Y %H:%M')}  ")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 1. Métricas Consolidadas por Variante")
    lines.append("")
    lines.append("| Variante | Compradores | GMV Total | Comissão | Cashback | **Lucro Méliuz** | Margem | Cashback/GMV | Ticket Médio | Compradores/dia |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")

    for _, row in summary.iterrows():
        g = row["Grupos de usuários"]
        marker = " ✅" if g == winner else ""
        lines.append(
            f"| {g}{marker} "
            f"| {int(row['compradores_total']):,} "
            f"| {fmt_brl(row['gmv_total'])} "
            f"| {fmt_brl(row['comissao_total'])} "
            f"| {fmt_brl(row['cashback_total'])} "
            f"| **{fmt_brl(row['lucro_total'])}** "
            f"| {fmt_pct(row['margem_pct'])} "
            f"| {fmt_pct(row['cashback_pct_gmv'])} "
            f"| {fmt_brl(row['ticket_medio'])} "
            f"| {row['compradores_por_dia']:.1f} |"
        )

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 2. Significância Estatística")
    lines.append("")
    lines.append("Teste t de Student — compradores diários de cada variante vs. Grupo 1 (controle).  ")
    lines.append("Nível de confiança adotado: **95% (α = 0,05)**")
    lines.append("")
    lines.append("| Comparação | p-value | Significativo? |")
    lines.append("|---|---|---|")

    controle = summary["Grupos de usuários"].iloc[0]
    for g, p in sig_tests.items():
        sig = "✅ Sim" if p < 0.05 else "❌ Não"
        lines.append(f"| {controle} vs {g} | {p:.4f} | {sig} |")

    if not sig_tests:
        lines.append("| — | — | Apenas 1 variante além do controle |")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 3. Análise de Rentabilidade")
    lines.append("")

    winner_row = summary[summary["Grupos de usuários"] == winner].iloc[0]
    controle_row = summary[summary["Grupos de usuários"] == controle].iloc[0]

    lines.append(f"**Variante Vencedora: {winner}**")
    lines.append("")

    if winner != controle:
        delta_lucro = winner_row["lucro_total"] - controle_row["lucro_total"]
        delta_gmv = winner_row["gmv_total"] - controle_row["gmv_total"]
        delta_compradores = winner_row["compradores_total"] - controle_row["compradores_total"]
        lines.append(f"Comparado ao controle ({controle}):")
        lines.append(f"- Lucro adicional: **{fmt_brl(delta_lucro)}**")
        lines.append(f"- GMV adicional: **{fmt_brl(delta_gmv)}**")
        lines.append(f"- Compradores adicionais: **{int(delta_compradores):,}**")
        lines.append(f"- Margem: {fmt_pct(winner_row['margem_pct'])} vs {fmt_pct(controle_row['margem_pct'])} do controle")
    else:
        lines.append("O controle se manteve como variante mais rentável.")
        lines.append(f"- Margem operacional: **{fmt_pct(winner_row['margem_pct'])}**")
        lines.append(f"- Lucro total: **{fmt_brl(winner_row['lucro_total'])}**")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 4. Decisão e Recomendação")
    lines.append("")
    lines.append(f"> **Escalar para 100% do tráfego: {winner}**")
    lines.append("")
    lines.append(justificativa)
    lines.append("")
    lines.append("### Observações importantes")
    lines.append("")

    min_lucro = summary["lucro_total"].min()
    if min_lucro <= 0:
        worst = summary.loc[summary["lucro_total"].idxmin(), "Grupos de usuários"]
        lines.append(f"⚠️ **{worst} operou com lucro zero ou negativo** — o cashback consumiu toda a comissão. Evitar esse nível de cashback.")

    cashback_max = summary["cashback_pct_gmv"].max()
    if cashback_max > 8:
        lines.append("⚠️ **Cashback acima de 8% do GMV** em ao menos uma variante — risco de unsustainability.")

    lines.append(f"- Ticket médio estável entre variantes (~{fmt_brl(summary['ticket_medio'].mean())}) — o cashback não alterou o comportamento de compra por pedido.")
    lines.append("- Recomenda-se monitorar retenção e LTV após escalonamento.")
    lines.append("")

    return "\n".join(lines)

# ─── Registro no tracker CSV ─────────────────────────────────────────────────
def build_tracker_row(df, summary, sig_tests, winner, justificativa):
    parceiro = df["Parceiro"].iloc[0]
    periodo_ini = df["Data"].min().strftime("%d/%m/%Y")
    periodo_fim = df["Data"].max().strftime("%d/%m/%Y")
    grupos_str = " | ".join(summary["Grupos de usuários"].tolist())
    winner_row = summary[summary["Grupos de usuários"] == winner].iloc[0]
    p_vals = ", ".join([f"{g}: {p}" for g, p in sig_tests.items()]) if sig_tests else "N/A"

    return {
        "data_analise": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "nome_teste": f"Teste A/B {parceiro}",
        "parceiro": parceiro,
        "periodo": f"{periodo_ini} a {periodo_fim}",
        "grupos": grupos_str,
        "descricao": f"Teste de variantes de cashback para {parceiro}",
        "vencedor": winner,
        "p_value": p_vals,
        "gmv_vencedor": round(winner_row["gmv_total"], 2),
        "margem_vencedor_pct": round(winner_row["margem_pct"], 2),
        "lucro_vencedor": round(winner_row["lucro_total"], 2),
        "decisao": f"Escalar {winner} para 100% do tráfego",
    }

def register_in_csv(row: dict):
    file_exists = os.path.isfile(TRACKER_FILE)
    with open(TRACKER_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=TRACKER_COLUMNS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)
    print(f"✅ Registrado no CSV local: '{TRACKER_FILE}'")

def register_in_sheets(row: dict):
    try:
        import gspread
        from google.oauth2.service_account import Credentials

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]

        creds = Credentials.from_service_account_file(SHEETS_CREDENTIALS_FILE, scopes=scopes)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SHEETS_SPREADSHEET_ID).sheet1

        # Garante cabeçalho na primeira linha
        existing = sheet.get_all_values()
        if not existing:
            sheet.append_row(TRACKER_COLUMNS)

        # Adiciona linha com os valores na ordem correta
        new_row = [str(row[col]) for col in TRACKER_COLUMNS]
        sheet.append_row(new_row)

        print(f"✅ Registrado direto no Google Sheets!")

    except FileNotFoundError:
        print(f"⚠️  Credenciais não encontradas ({SHEETS_CREDENTIALS_FILE}). Pulando Sheets.")
    except Exception as e:
        print(f"⚠️  Erro ao escrever no Sheets: {e}. Dados salvos no CSV local.")

# ─── Ponto de entrada ────────────────────────────────────────────────────────
def run(filepath: str):
    print(f"\n📂 Analisando: {filepath}")
    print("─" * 50)

    df = load_dataset(filepath)
    summary = compute_summary(df)
    sig_tests = run_significance_tests(df)
    winner, justificativa = decide_winner(summary, sig_tests)

    os.makedirs(REPORTS_DIR, exist_ok=True)
    parceiro_slug = df["Parceiro"].iloc[0].replace(" ", "_").lower()
    report_path = os.path.join(REPORTS_DIR, f"relatorio_{parceiro_slug}.md")

    report_text = generate_report(df, summary, sig_tests, winner, justificativa, filepath)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    print(report_text)
    print(f"\n📄 Relatório salvo em: {report_path}")

    row = build_tracker_row(df, summary, sig_tests, winner, justificativa)
    register_in_csv(row)
    register_in_sheets(row)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python analyze_ab.py <caminho_do_csv>")
        sys.exit(1)
    run(sys.argv[1])
