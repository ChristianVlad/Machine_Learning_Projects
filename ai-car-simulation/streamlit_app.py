import streamlit as st
import mlflow
from mlflow.tracking import MlflowClient
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Resultados NEAT", layout="wide")

# Conecta con MLflow
client = MlflowClient()
experiment_name = "Carros_Auton_REINFORCE"
experiment = client.get_experiment_by_name(experiment_name)

if not experiment:
    st.error(f"No se encontró el experimento llamado '{experiment_name}'.")
    st.stop()

# Buscar runs
runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id])

if runs.empty:
    st.warning("No hay ejecuciones registradas aún.")
    st.stop()

st.title("🚗 Evolución de entrenamiento con NEAT + MLflow")
st.write(f"Experimento: **{experiment_name}**")

# Tabla de resumen
st.subheader("Resumen de runs")
st.dataframe(runs[["run_id", "start_time", "metrics.max_fitness", "metrics.avg_fitness", "params.map_file"]])

# Seleccionar run
selected_run_id = st.selectbox("Selecciona un run para ver más detalles:", runs["run_id"].tolist())

selected_run = client.get_run(selected_run_id)

# Métricas por generación
metrics = selected_run.data.metrics

# Mostrar métricas básicas
st.write("### Parámetros")
st.json(selected_run.data.params)

st.write("### Métricas finales")
st.json(metrics)

# Mostrar imagen si se loggeó
st.write("### Imagen del gráfico de fitness")

artifact_uri = selected_run.info.artifact_uri
fitness_plot_path = f"{artifact_uri}/fitness_plot.png"

# Streamlit no puede abrir directamente desde URI tipo `file:/`, usamos workaround:
import tempfile
import os
import urllib.request

# Descarga temporal si existe el archivo
try:
    tmp_path = tempfile.mktemp(suffix=".png")
    urllib.request.urlretrieve(fitness_plot_path, tmp_path)
    st.image(tmp_path, caption="Evolución del Fitness", use_column_width=True)
except:
    st.warning("No se encontró el gráfico `fitness_plot.png` en este run.")

