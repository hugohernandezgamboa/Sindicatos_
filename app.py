import streamlit as st
import pandas as pd
import io

# ---------- Configuración inicial ----------
st.set_page_config(page_title="Explorador de Sindicatos", layout="wide")

# ---------- Carga de datos ----------
@st.cache_data
def load_data():
    return pd.read_excel("C:/Users/h_maq/Downloads/Sindicatos_Only.xlsx")

df = load_data()

# ---------- Título ----------
st.title("📊 Explorador interactivo de Sindicatos y Patrones")

# ---------- Filtros (solo 3 variables) ----------
st.sidebar.header("🔍 Filtros")
filtered_df = df.copy()

filtro_columnas = ["NUEVOS REFORMA", "Legitimados", "REPOSITORIO"]

for col in filtro_columnas:
    if col in df.columns:
        unique_vals = sorted(df[col].dropna().unique())
        if len(unique_vals) > 1:
            with st.sidebar.expander(f"Filtrar {col}", expanded=False):
                sel = st.sidebar.multiselect(f"{col}:", unique_vals, default=unique_vals, key=col)
                filtered_df = filtered_df[filtered_df[col].isin(sel)]

# ---------- Métricas ----------
st.subheader("📄 Resultados filtrados")
st.write(f"Total de registros: {len(filtered_df):,}")
st.dataframe(filtered_df, use_container_width=True)

# ---------- Gráficas de SI / NO por variable ----------
st.subheader("📊 Distribución de SI / NO por variable")

col1, col2, col3 = st.columns(3)

def graficar_estado(df_, columna, contenedor):
    if columna in df_.columns:
        conteo = (
            df_[columna]
            .str.upper()
            .value_counts()
            .rename_axis(columna)
            .reset_index(name="Frecuencia")
            .set_index(columna)
        )
        with contenedor:
            st.markdown(f"**{columna}**")
            st.bar_chart(conteo)

graficar_estado(filtered_df, "NUEVOS REFORMA", col1)
graficar_estado(filtered_df, "Legitimados", col2)
graficar_estado(filtered_df, "REPOSITORIO", col3)

# ---------- Botón para descargar resultados ----------
def to_excel(df_):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df_.to_excel(writer, index=False, sheet_name="Filtrados")
    return buffer.getvalue()

st.download_button(
    "📥 Descargar Excel filtrado",
    data=to_excel(filtered_df),
    file_name="sindicatos_filtrados.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

