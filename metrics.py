import json
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd

# Cargar datos desde un archivo JSON
with open('datos_taxis.json', 'r') as archivo:
    informacion = json.load(archivo)

# Asegurar la existencia de las claves necesarias
taxis_info = informacion.get('taxis', [])
solicitudes_info = informacion.get('servicios', [])
metricas = informacion.get('estadisticas', {"servicios_satisfactorios": 0, "servicios_negados": 0})

# Crear gráfico circular de servicios satisfactorios y denegados
def generar_grafico_pie(estadisticas):
    etiquetas = ['Satisfactorios', 'Negados']
    valores = [
        estadisticas.get('servicios_satisfactorios', 0),
        estadisticas.get('servicios_negados', 0)
    ]

    plt.figure(figsize=(6, 6))
    plt.pie(valores, labels=etiquetas, autopct='%1.1f%%', startangle=90, colors=['lightgreen', 'red'])
    plt.title('Distribución de Servicios (Satisfactorios vs Negados)')
    plt.savefig("grafico_pie_servicios.png")
    plt.close()

generar_grafico_pie(metricas)

# Crear gráfico de dispersión para las posiciones de usuarios y taxis
def generar_grafico_dispersion(servicios):
    posiciones_usuarios = [(s.get('usuario', {}).get('x', 0), s.get('usuario', {}).get('y', 0)) for s in servicios]
    posiciones_taxis = [(s.get('taxi_posicion', {}).get('x', 0), s.get('taxi_posicion', {}).get('y', 0)) for s in servicios]

    usuarios_x, usuarios_y = zip(*posiciones_usuarios) if posiciones_usuarios else ([], [])
    taxis_x, taxis_y = zip(*posiciones_taxis) if posiciones_taxis else ([], [])

    plt.figure(figsize=(8, 6))
    plt.scatter(usuarios_x, usuarios_y, color='blue', label='Usuarios')
    plt.scatter(taxis_x, taxis_y, color='red', marker='x', label='Taxis')
    plt.title('Distribución de Usuarios y Taxis en el Plano XY')
    plt.xlabel('Coordenada X')
    plt.ylabel('Coordenada Y')
    plt.legend()
    plt.savefig("grafico_dispersion_posiciones.png")
    plt.close()

generar_grafico_dispersion(solicitudes_info)

# Crear gráfico de barras de servicios completados vs máximos permitidos
def generar_grafico_barras(taxis):
    identificadores = [taxi.get('id', 'Desconocido') for taxi in taxis]
    completados = [taxi.get('services_completed', 0) for taxi in taxis]
    limites = [taxi.get('max_services', 0) for taxi in taxis]

    plt.figure(figsize=(10, 6))
    plt.bar(identificadores, limites, label='Máximos Permitidos', alpha=0.7, color='lightgreen')
    plt.bar(identificadores, completados, label='Completados', alpha=0.7, color='blue')
    plt.title('Servicios Completados vs Máximos Permitidos')
    plt.xlabel('ID del Taxi')
    plt.ylabel('Cantidad de Servicios')
    plt.legend()
    plt.savefig("grafico_barras_servicios.png")
    plt.close()

generar_grafico_barras(taxis_info)

# Mostrar estadísticas generales en la consola
def mostrar_estadisticas(estadisticas):
    print("\nResumen de Estadísticas:")
    print(f"Servicios satisfactorios: {estadisticas.get('servicios_satisfactorios', 0)}")
    print(f"Servicios negados: {estadisticas.get('servicios_negados', 0)}")

mostrar_estadisticas(metricas)
