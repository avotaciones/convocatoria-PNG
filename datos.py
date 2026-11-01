"""Carga del Parquet y normalización de datos de aspirantes."""

import re
from pathlib import Path

import pandas as pd
import streamlit as st

DATA_PATH = Path(__file__).parent / "datos.parquet"
META_PATH = Path(__file__).parent / "datos_meta.txt"


def normalizar_estado(valor) -> str:
    if valor is None:
        return ""
    s = str(valor).strip().lower()
    if s in ("admitido", "admitida"):
        return "Admitido"
    if s in ("no admitido", "no admitida", "no_admitido", "noadmitido",
             "rechazado", "rechazada"):
        return "No admitido"
    return ""


def normalizar_convocatoria(valor) -> str:
    if valor is None or valor == "":
        return ""
    if hasattr(valor, "strftime"):
        return valor.strftime("%m-%Y")
    s = str(valor).strip()
    m = re.fullmatch(r"(\d{1,2})-(\d{4})", s)
    if m:
        return f"{int(m.group(1)):02d}-{m.group(2)}"
    return s


def categorizar_causal(texto: str) -> list[str]:
    if not texto:
        return []
    t = texto.lower()
    cats = set()

    if "falta de tarjeta" in t:
        cats.add("Falta de tarjeta profesional")
    if any(k in t for k in ("tarjeta profesional vencida", "no legible",
                            "tachones", "enmendaduras")):
        cats.add("Tarjeta profesional vencida/ilegible")
    if "falta de documentos que acrediten la formación" in t:
        cats.add("Falta de docs. de formación académica")
    if "falta de documentos que acrediten la experiencia" in t:
        cats.add("Falta de docs. de experiencia")
    if "requisito mínimo de educación" in t:
        cats.add("No cumple requisito de educación")
    if "requisito mínimo de experiencia" in t:
        cats.add("No cumple requisito de experiencia")
    if "certificaciones no acreditan" in t and ("experiencia" in t or "tiempo" in t):
        cats.add("Certificaciones no acreditan experiencia")
    if "certificación no acredita" in t and "formación académica" in t:
        cats.add("Certificación académica no acredita formación")
    if "incumplimiento de los requisitos mínimos" in t:
        cats.add("Incumplimiento de requisitos mínimos")
    if "incumplimiento de los términos" in t:
        cats.add("Incumplimiento de términos y condiciones")

    if not cats:
        cats.add("Otras")
    return sorted(cats)


@st.cache_data(show_spinner="Cargando datos…")
def cargar_datos() -> tuple[pd.DataFrame, str]:
    """Devuelve (DataFrame normalizado, timestamp del snapshot)."""
    if not DATA_PATH.exists():
        return pd.DataFrame(
            columns=["registro", "convocatoria", "estado", "causalTexto", "categorias"]
        ), ""

    df = pd.read_parquet(DATA_PATH, engine="pyarrow")

    # Normalizar (por si el Parquet trae variantes)
    df["estado"] = df["estado"].astype(str).map(normalizar_estado)
    df = df[df["estado"] != ""].reset_index(drop=True)
    df["convocatoria"] = df["convocatoria"].astype(str).map(normalizar_convocatoria)
    df["registro"] = df["registro"].astype(str).str.strip()
    df["causalTexto"] = df["causalTexto"].fillna("").astype(str).str.strip()

    # Derivar categorías (no se guardan en Parquet)
    df["categorias"] = df["causalTexto"].apply(categorizar_causal)

    actualizado = ""
    if META_PATH.exists():
        actualizado = META_PATH.read_text(encoding="utf-8").strip()

    return df, actualizado
