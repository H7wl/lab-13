import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium

# URL вашего GeoJSON-файла на GitHub
geojson_url = "https://raw.githubusercontent.com/ArtyomKeith/lab13_iv/main/campus.geojson"

# Загрузка GeoJSON
@st.cache_data
def load_geojson(url):
    return gpd.read_file(url)

# Загрузка данных
gdf = load_geojson(geojson_url)

# Центр карты
center_lat = gdf.geometry.centroid.y.mean()
center_lon = gdf.geometry.centroid.x.mean()

# Заголовок приложения
st.title("Интерактивная карта кампуса КазАТУ")
st.markdown("Используйте интерактивные элементы для изучения карты кампуса.")

# Выбор слоя карты
st.sidebar.header("Настройки карты")
map_tiles = st.sidebar.selectbox(
    "Выберите слой карты:",
    options=["Esri Satellite", "OpenStreetMap", "CartoDB positron", "Stamen Terrain"],
    index=0
)

# Фильтрация данных
st.sidebar.header("Фильтры")
search_term = st.sidebar.text_input("Поиск по названию объекта:")
object_type = st.sidebar.multiselect(
    "Тип объекта:",
    options=gdf['тип'].unique() if 'тип' in gdf.columns else [],
    default=gdf['тип'].unique() if 'тип' in gdf.columns else []
)

if search_term:
    filtered_gdf = gdf[gdf['название'].str.contains(search_term, case=False, na=False)]
else:
    filtered_gdf = gdf

if 'тип' in gdf.columns and object_type:
    filtered_gdf = filtered_gdf[filtered_gdf['тип'].isin(object_type)]

# Создание карты
campus_map = folium.Map(location=[center_lat, center_lon], zoom_start=17, tiles=map_tiles, attr=map_tiles)

# Добавление объектов
for _, row in filtered_gdf.iterrows():
    coords = row.geometry.exterior.coords if row.geometry.type == "Polygon" else row.geometry.coords
    popup_text = f"<b>{row['название']}</b><br>{row['описание']}"
    if row.geometry.type == "Polygon":
        folium.Polygon(
            locations=[(lat, lon) for lon, lat in coords],
            color="blue",
            fill=True,
            fill_opacity=0.4,
            popup=folium.Popup(popup_text, max_width=300),
        ).add_to(campus_map)
    elif row.geometry.type == "Point":
        folium.Marker(
            location=[row.geometry.y, row.geometry.x],
            popup=folium.Popup(popup_text, max_width=300),
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(campus_map)

# Отображение карты
st_data = st_folium(campus_map, width=800, height=500)

# Кнопка сброса
if st.sidebar.button("Сбросить фильтры"):
    st.experimental_rerun()

# Отображение информации о результатах
st.markdown(f"Найдено объектов: {len(filtered_gdf)}")

