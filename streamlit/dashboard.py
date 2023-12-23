import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Configuración de diseño para reducir los márgenes
st.set_page_config(page_title="Dashboard Vehículos", page_icon="🚗", layout="wide", initial_sidebar_state="expanded")

# Cargar el CSV
file_path = 'Australian_Vehicle_Prices.csv'
df = pd.read_csv(file_path)

# Título estilizado en blanco con letras grises
styled_title = (
    "<h1 style='text-align: center; font-size: 36px; color: #808080; background-color: #ffffff; padding: 10px;'>Dashboard Vehículos</h1>"
)

# Mostrar el título estilizado en Streamlit
st.markdown(styled_title, unsafe_allow_html=True)

# Widget para seleccionar una sola marca
selected_brand = st.selectbox('Selecciona una Marca', df['Brand'].unique())

# Filtrar datos por la marca seleccionada
filtered_df = df[df['Brand'] == selected_brand]

# Filas para organizar los gráficos
row1_1, row1_2, row1_3 = st.columns(3)
row2_1, row2_2, row2_3 = st.columns(3)

# Configuración de la base de datos con SQLAlchemy
Base = declarative_base()

class LikedBrand(Base):
    __tablename__ = "liked_brands"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.now)

engine = create_engine("sqlite:///liked_brands.db")
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Verifica si 'like_button_state' está definido en st.session_state
if 'like_button_state' not in st.session_state:
    # Si no está definido, inicialízalo como False
    st.session_state.like_button_state = False

# Checkbox para añadir a favoritos
like_button = st.checkbox(f"Añadir {selected_brand} a favoritos", st.session_state.like_button_state)

db = SessionLocal()

if like_button:
    was_liked = db.query(db.query(LikedBrand).filter_by(brand=selected_brand).exists()).scalar()
    if not was_liked:
        # Guarda la marca que te gusta en la base de datos
        liked_brand = LikedBrand(brand=selected_brand)
        db.add(liked_brand)
        db.commit()

        # Realizar una solicitud POST a FastAPI
        response = requests.post("http://fastapi:8000/save_brand/", json={"name": str(selected_brand)})

        # Verificar la respuesta
        if response.status_code == 200:
            st.success(response.json()["message"])
        else:
            st.error(f"Error al enviar datos a FastAPI. Código de respuesta: {response.status_code}")
else:
    was_liked = db.query(db.query(LikedBrand).filter_by(brand=selected_brand).exists()).scalar()
    if was_liked:
        db.query(LikedBrand).filter_by(brand=selected_brand).delete()
        db.commit()
        # Realizar una solicitud POST a FastAPI
        response = requests.post("http://fastapi:8000/delete_brand/", json={"name": str(selected_brand)})
        # Verificar la respuesta
        if response.status_code == 200:
            st.warning(response.json()["message"])
        else:
            st.error(f"Error al enviar datos a FastAPI. Código de respuesta: {response.status_code}")
db.close()
git
# Visualización 1: Gráfico de barras para contar la cantidad de autos por modelo
fig_bar_by_model = px.bar(filtered_df['Model'].value_counts(), x=filtered_df['Model'].value_counts().index,
                          y=filtered_df['Model'].value_counts().values,
                          labels={'x': 'Modelo', 'y': 'Cantidad de Autos'},
                          title=f'Cantidad de Autos por Modelo para {selected_brand}',
                          height=300, width=400)

# Visualización 2: Gráfico de donas para mostrar la distribución de modelos
fig_donut = px.pie(filtered_df, names='Model', title=f'Distribución de Modelos para {selected_brand}',
                   hole=0.5, color_discrete_sequence=px.colors.qualitative.Set3,
                   height=300, width=400)

# Visualización 3: Gráfico de dispersión 3D con Precio, Kilómetros y Año del modelo
fig_3d_scatter = px.scatter_3d(filtered_df, x='Price', y='Kilometres', z='Year', color='UsedOrNew',
                               labels={'x': 'Precio', 'y': 'Kilómetros', 'z': 'Año del Modelo'},
                               title=f'Detalles 3D para {selected_brand}',
                               height=300, width=400)

# Visualización 4: Gráfico de barras apiladas para la distribución de tipos de carrocería (BodyType)
fig_body_type = px.bar(filtered_df, x='Brand', color='BodyType',
                      title=f'Distribución de Tipos de Carrocería para {selected_brand}',
                      labels={'Brand': 'Marca', 'BodyType': 'Tipo de Carrocería'},
                      height=300, width=400)

# Visualización 5: Gráfico de dispersión para la relación entre Precio y Eficiencia de Consumo de Combustible
fig_fuel_price_scatter = px.scatter(filtered_df, x='FuelConsumption', y='Price', color='Model',
                                    labels={'x': 'Eficiencia de Combustible', 'y': 'Precio'},
                                    title=f'Relación entre Precio y Eficiencia de Combustible para {selected_brand}',
                                    height=300, width=400)

# Visualización 6: Gráfico de barras para la distribución de tipos de transmisión
fig_transmission_horizontal = px.bar(filtered_df, y='Transmission',
                                     title=f'Distribución de Tipos de Transmisión para {selected_brand}',
                                     labels={'Transmission': 'Tipo de Transmisión'},
                                     orientation='h',
                                     height=300, width=400)

# Mostrar las visualizaciones en las filas organizadas
row1_1.plotly_chart(fig_bar_by_model)
row1_2.plotly_chart(fig_donut)
row1_3.plotly_chart(fig_3d_scatter)
row2_1.plotly_chart(fig_body_type)
row2_2.plotly_chart(fig_fuel_price_scatter)
row2_3.plotly_chart(fig_transmission_horizontal)

# Consulta todas las marcas que han sido marcadas como "Me gusta"
all_liked_brands = SessionLocal().query(LikedBrand).all()

# Muestra las marcas en Streamlit
if len(all_liked_brands) != 0:
    st.write("Marcas que te gustan:")
    for liked_brand in all_liked_brands:
        st.write(liked_brand.brand)