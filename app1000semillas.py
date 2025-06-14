import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math

st.set_page_config(page_title="Análisis de Pesadas", layout="centered")

st.title("🌾 Análisis de Peso de 1000 Semillas")
st.write(
    "Cálculo del peso promedio de 1000 semillas a partir del peso de ocho o más réplicas de 100 semillas..."
)

# Elegir método de entrada
opcion_entrada = st.radio("Selecciona cómo ingresar los datos:", ["📤 Subir archivo CSV", "⌨️ Ingresar manualmente"])
pesadas = []

if opcion_entrada == "📤 Subir archivo CSV":
    archivo = st.file_uploader("Cargar archivo CSV con una columna de pesadas", type=["csv"])
    if archivo is not None:
        try:
            df = pd.read_csv(archivo)
            columnas_numericas = df.select_dtypes(include=['float', 'int']).columns.tolist()
            if not columnas_numericas:
                st.error("❌ El archivo no contiene columnas numéricas.")
            else:
                columna = st.selectbox("Selecciona la columna con los datos:", columnas_numericas)
                pesadas = df[columna].dropna().tolist()
        except Exception as e:
            st.error(f"❌ Error al procesar el archivo: {e}")

elif opcion_entrada == "⌨️ Ingresar manualmente":
    entrada_manual = st.text_area("Ingresa los pesos separados por coma (ej: 10.1, 9.9, 10.05):")
    if entrada_manual:
        try:
            pesadas = [float(x.strip()) for x in entrada_manual.split(",") if x.strip()]
        except ValueError:
            st.error("❌ Asegúrate de ingresar solo números separados por comas.")

# Procesar si hay suficientes datos
if pesadas:
    if len(pesadas) < 8:
        st.warning("⚠️ Se necesitan al menos 8 valores para calcular el peso de 1000 semillas.")
    else:
        # Calcular estadísticas
        media = sum(pesadas) / len(pesadas)
        suma_cuadrados = sum((x - media) ** 2 for x in pesadas)
        desviacion_estandar = math.sqrt(suma_cuadrados / (len(pesadas) - 1))
        coef_var = (desviacion_estandar / media) * 100
        peso_1000 = media * 10
        limite_superior = media + 2 * desviacion_estandar
        fuera_rango = [x for x in pesadas if x > limite_superior]

        # Mostrar resultados
        st.subheader("📈 Resultados")
        st.markdown(f"- Media: **{media:.2f} g**")
        st.markdown(f"- Desviación estándar: **{desviacion_estandar:.4f} g**")
        st.markdown(f"- Coeficiente de variación: **{coef_var:.2f}%**")
        st.markdown(f"- Peso estimado de 1000 semillas: **{peso_1000:.2f} g**")

        if coef_var >= 4:
            st.warning("⚠️ El coeficiente de variación es mayor o igual a 4%. Se recomienda duplicar el número de muestras.")
        else:
            st.success("✅ El coeficiente de variación es aceptable.")

        if fuera_rango:
            st.error(f"❌ Pesadas que superan la media + 2*desviación estándar: {fuera_rango}")
        else:
            st.success("✅ Ninguna pesada supera la media + 2*desviación estándar.")

        # Gráfico
        st.subheader("📊 Gráfico de Pesadas")
        colores = ['red' if x > limite_superior else 'skyblue' for x in pesadas]

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(range(1, len(pesadas) + 1), pesadas, color=colores, edgecolor='black')
        ax.axhline(y=media, color='green', linestyle='--', label=f'Media = {media:.2f}')
        ax.fill_between(range(0, len(pesadas) + 2), media - desviacion_estandar,
                        media + desviacion_estandar, color='green', alpha=0.15,
                        label='±1 desviación estándar')

        for i, peso in enumerate(pesadas):
            ajuste_altura = 0.01 * max(pesadas)
            tamaño_fuente = 9 if len(pesadas) <= 20 else 7
            rotacion = 0 if len(pesadas) <= 20 else 60
            ax.text(i + 1, peso + ajuste_altura, f"{peso:.2f}", ha='center', va='bottom',
                    fontsize=tamaño_fuente, rotation=rotacion)

        ax.set_title('Pesadas con marcación de valores fuera de rango')
        ax.set_xlabel('Número de muestra')
        ax.set_ylabel('Peso (g)')
        ax.set_xticks(range(1, len(pesadas) + 1))
        ax.set_xticklabels(range(1, len(pesadas) + 1), rotation=45 if len(pesadas) > 20 else 0)
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.5)

        st.pyplot(fig)

        # Formulario de correo
        st.subheader("📧 Solicitar informe por correo electrónico")
        with st.form("form_mail"):
            correo = st.text_input("Ingrese su correo electrónico para solicitar el informe:")
            enviar = st.form_submit_button("📨 Enviar solicitud")

            if enviar:
                if "@" in correo and "." in correo:
                    st.success(f"✅ Solicitud enviada. Te contactaremos a {correo}.")
                    try:
                        with open("solicitudes_mail.csv", "a") as f:
                            f.write(correo + "\n")
                    except Exception as e:
                        st.warning(f"⚠️ No se pudo guardar la dirección: {e}")
                else:
                    st.error("❌ Por favor, ingrese un correo válido.")
else:
    st.info("📌 Esperando datos para el análisis.")
