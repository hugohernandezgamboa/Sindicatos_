# ──────────────────────────────────────────────────────────────
# app.py  –  Explorador interactivo de sindicatos y patrones
# Coloca este archivo en la misma carpeta que Sindicatos_limpio.xlsx
# Requiere: streamlit, pandas, openpyxl  (listar en requirements.txt)
# ──────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
import pathlib
import io

# ─── Configuración general ───────────────────────────────────
st.set_page_config(page_title="Explorador de Sindicatos", layout="wide")

# Carpeta donde vive este script
BASE_DIR = pathlib.Path(__file__).parent
EXCEL_FILE = BASE_DIR / "Sindicatos_limpio.xlsx"      # nombre exacto del archivo

# ─── Carga de datos (con caché) ───────────────────────────────
@st.cache_data
def load_data() -> pd.DataFrame:
    """Lee el Excel con ruta relativa y normaliza SÍ/NO."""
    df = pd.read_excel(EXCEL_FILE)

    # Columnas que contienen SÍ / NO
    bin_cols = ["NUEVOS REFORMA", "Legitimados", "REPOSITORIO"]
    for col in bin_cols:
        if col in df.columns:
            df[col] = (df[col]
                       .astype(str)
                       .str.strip()
                       .str.upper()
                       .replace({"SI": "Sí", "NO": "No"}))
    return df

df = load_data()

# ─── Barra lateral de filtros ────────────────────────────────
st.sidebar.header("🔍 Filtros")
filter_cols = ["NUEVOS REFORMA", "Legitimados", "REPOSITORIO"]

filtered_df = df.copy()
for col in filter_cols:
    if col in df.columns:
        options = sorted(df[col].dropna().unique())
        sel = st.sidebar.multiselect(col, options, default=options)
        filtered_df = filtered_df[filtered_df[col].isin(sel)]

# ─── Título y métrica ────────────────────────────────────────
st.title("📊 Explorador interactivo de Sindicatos y Patrones")
st.subheader("📄 Resultados filtrados")
st.metric("Registros", f"{len(filtered_df):,}")

# ─── Tabla de datos ──────────────────────────────────────────
st.dataframe(filtered_df, use_container_width=True)

# ─── Gráficas de barras (Sí/No) ──────────────────────────────
st.subheader("📊 Distribución Sí / No por variable")
c1, c2, c3 = st.columns(3)

def bar_yes_no(df_: pd.DataFrame, col: str, container):
    if col in df_.columns:
        counts = df_[col].value_counts().reindex(["Sí", "No"]).fillna(0)
        container.markdown(f"**{col}**")
        container.bar_chart(counts)

bar_yes_no(filtered_df, "NUEVOS REFORMA", c1)
bar_yes_no(filtered_df, "Legitimados", c2)
bar_yes_no(filtered_df, "REPOSITORIO", c3)

# ─── Botón de descarga del Excel filtrado ─────────────────────
def to_excel(dataframe: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        dataframe.to_excel(writer, index=False, sheet_name="Filtrados")
    return buffer.getvalue()

st.download_button(
    label="📥 Descargar Excel filtrado",
    data=to_excel(filtered_df),
    file_name="sindicatos_filtrados.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

# ──────────────────────────────────────────────────────────────
# Fin del archivo
# ──────────────────────────────────────────────────────────────


