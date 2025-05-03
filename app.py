
# Aplicación en Python para crear tests personalizados a partir de una base de preguntas
# Framework: Streamlit (interfaz web sencilla)

import streamlit as st
import pandas as pd
import random

# Cargar base de datos de preguntas desde un archivo CSV o Excel
def cargar_preguntas(archivo):
    if archivo.name.endswith('.csv'):
        return pd.read_csv(archivo)
    elif archivo.name.endswith('.xlsx'):
        return pd.read_excel(archivo)
    else:
        st.error("Formato de archivo no soportado. Usa .csv o .xlsx")
        return None

# Filtrar preguntas por tema y cantidad deseada
def seleccionar_preguntas(df, tema, num_preguntas):
    df_filtrado = df[df['Tema'] == tema]
    return df_filtrado.sample(n=min(num_preguntas, len(df_filtrado)))

# Interfaz Streamlit
st.title("Generador de Tests por Tema")

archivo = st.file_uploader("Sube tu base de datos de preguntas (.csv o .xlsx)")

if archivo:
    df_preguntas = cargar_preguntas(archivo)
    if df_preguntas is not None:
        temas_disponibles = df_preguntas['Tema'].unique()
        tema_seleccionado = st.selectbox("Selecciona un tema", temas_disponibles)
        num_preguntas = st.slider("Cantidad de preguntas", 1, 20, 5)

        if st.button("Generar test"):
            preguntas_test = seleccionar_preguntas(df_preguntas, tema_seleccionado, num_preguntas)
            respuestas_usuario = {}

            st.subheader("Test generado")
            for i, row in preguntas_test.iterrows():
                opciones = [row['Opción 1'], row['Opción 2'], row['Opción 3'], row['Opción 4']]
                respuesta = st.radio(row['Pregunta'], opciones, key=row['Pregunta'])
                respuestas_usuario[row['Pregunta']] = respuesta

            if st.button("Calcular puntuación"):
                puntuacion = 0
                for i, row in preguntas_test.iterrows():
                    correcta = row[f"Opción {row['Correcta']}"]
                    seleccionada = respuestas_usuario.get(row['Pregunta'], None)
                    if seleccionada == correcta:
                        puntuacion += 0.2
                    elif seleccionada is not None:
                        puntuacion -= 0.05
                st.success(f"Puntuación final: {puntuacion:.2f} puntos")
else:
    st.info("Sube un archivo para comenzar. El archivo debe tener las columnas: Tema, Pregunta, Opción 1, Opción 2, Opción 3, Opción 4, Correcta")
