
# Aplicación en Python para crear tests personalizados a partir de una base de preguntas
# Framework: Streamlit (interfaz web sencilla)

import streamlit as st
import pandas as pd
import random
import io
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt

# Cargar base de datos de preguntas desde un archivo CSV o Excel
def cargar_preguntas(archivo):
    if archivo.name.endswith('.csv'):
        return pd.read_csv(archivo)
    elif archivo.name.endswith('.xlsx'):
        return pd.read_excel(archivo)
    else:
        st.error("Formato de archivo no soportado. Usa .csv o .xlsx")
        return None

# Filtrar preguntas por tema y dificultad y cantidad deseada
def seleccionar_preguntas(df, tema, dificultad, num_preguntas):
    df_filtrado = df[(df['Tema'] == tema) & (df['Dificultad'] == dificultad)]
    return df_filtrado.sample(n=min(num_preguntas, len(df_filtrado)))

# Crear PDF con resultados
def generar_pdf(nombre_usuario, resultados, puntuacion):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 50

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, f"Resultados del test - {nombre_usuario}")
    y -= 25
    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    y -= 40

    for r in resultados:
        pregunta = r['Pregunta']
        dada = r['Respuesta dada'] or "Sin responder"
        correcta = r['Respuesta correcta']
        resultado = r['Resultado']

        c.drawString(50, y, f"Pregunta: {pregunta[:90]}" + ("..." if len(pregunta) > 90 else ""))
        y -= 15
        c.drawString(60, y, f"Tu respuesta: {dada}")
        y -= 15
        c.drawString(60, y, f"Respuesta correcta: {correcta}  Resultado: {resultado}")
        y -= 25
        if y < 100:
            c.showPage()
            y = height - 50

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, f"Puntuación final: {puntuacion:.2f} puntos")
    c.save()
    buffer.seek(0)
    return buffer

# Interfaz Streamlit
st.title("Generador de Tests por Tema")

archivo = st.file_uploader("Sube tu base de datos de preguntas (.csv o .xlsx)")
if not archivo and os.path.exists("Preguntas_TEST1_tematitzat.xlsx"):
    archivo = open("Preguntas_TEST1_tematitzat.xlsx", "rb")

if archivo:
    df_preguntas = cargar_preguntas(archivo)
    if df_preguntas is not None:
        nombre_usuario = st.text_input("Escribe tu nombre")

        temas_disponibles = df_preguntas['Tema'].unique()
        tema_seleccionado = st.selectbox("Selecciona un tema", temas_disponibles)

        dificultades_disponibles = df_preguntas['Dificultad'].unique()
        dificultad_seleccionada = st.selectbox("Selecciona una dificultad", dificultades_disponibles)

        num_preguntas = st.slider("Cantidad de preguntas", 1, 20, 5)

        if st.button("Generar test"):
            preguntas_test = seleccionar_preguntas(df_preguntas, tema_seleccionado, dificultad_seleccionada, num_preguntas)
            respuestas_usuario = {}

            st.subheader("Test generado")
            for i, row in preguntas_test.iterrows():
                opciones = [row['Opción 1'], row['Opción 2'], row['Opción 3'], row['Opción 4']]
                respuesta = st.radio(row['Pregunta'], opciones, index=None, key=row['Pregunta'])
                respuestas_usuario[row['Pregunta']] = respuesta

            if st.button("Calcular puntuación"):
                puntuacion = 0
                resultados = []
                correctas = 0
                incorrectas = 0
                omitidas = 0

                for i, row in preguntas_test.iterrows():
                    correcta = row[f"Opción {row['Correcta']}"]
                    seleccionada = respuestas_usuario.get(row['Pregunta'], None)
                    correcta_bool = seleccionada == correcta
                    if correcta_bool:
                        puntuacion += 0.2
                        correctas += 1
                    elif seleccionada is not None:
                        puntuacion -= 0.05
                        incorrectas += 1
                    else:
                        omitidas += 1
                    resultados.append({
                        "Usuario": nombre_usuario,
                        "Pregunta": row['Pregunta'],
                        "Respuesta dada": seleccionada,
                        "Respuesta correcta": correcta,
                        "Resultado": "✅" if correcta_bool else "❌"
                    })

                st.success(f"Puntuación final: {puntuacion:.2f} puntos")

                st.subheader("Distribución de resultados")
                fig1, ax1 = plt.subplots()
                etiquetas = ['Correctas', 'Incorrectas', 'Omitidas']
                valores = [correctas, incorrectas, omitidas]
                ax1.pie(valores, labels=etiquetas, autopct='%1.1f%%', startangle=90)
                ax1.axis('equal')
                st.pyplot(fig1)

                st.subheader("Resumen en barras")
                fig2, ax2 = plt.subplots()
                ax2.barh(etiquetas, valores, color=['green', 'red', 'gray'])
                st.pyplot(fig2)

                df_resultados = pd.DataFrame(resultados)
                csv_buffer = io.StringIO()
                df_resultados.to_csv(csv_buffer, index=False)
                st.download_button(
                    label="Descargar resultados en CSV",
                    data=csv_buffer.getvalue(),
                    file_name=f"resultados_{nombre_usuario}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime='text/csv'
                )

                pdf_buffer = generar_pdf(nombre_usuario, resultados, puntuacion)
                st.download_button(
                    label="Descargar resultados en PDF",
                    data=pdf_buffer,
                    file_name=f"resultados_{nombre_usuario}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime='application/pdf'
                )
else:
    st.info("Sube un archivo para comenzar. El archivo debe tener las columnas: Tema, Pregunta, Opción 1, Opción 2, Opción 3, Opción 4, Correcta, Dificultad")
