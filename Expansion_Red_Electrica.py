# Proyecto de red eléctrica: Mapeado con nodos conectados a la central eléctrica

'''
Colaboradores:
Angel Leonardo Vaca Ojeda (23310142)
Nestor Alejandro Beltran Rodriguez (22110124)
Jorge Alexis Becerra Fernandez (22310340)
'''

#Primero importamos las librerias necesarias para representar el grafo
#IMPORTANTE WACHOS primero descargar la libreria en la terminal -> !pip install networkx matplotlib

import networkx as nx
import matplotlib.pyplot as plt
import random
import numpy as np
from queue import PriorityQueue
from matplotlib.widgets import Button
#agregue la libreria heap, nos va a ayudar a dar un menor valor a nodos padre priorizandolos
import heapq


G = nx.Graph()

#Definimos la cuadricula primero
n_filas = 5
n_columnas = 5

posiciones = {}
nodos_colonia = set()
central = None

# Crear nodos de la cuadricula
for i in range(n_filas):
    for j in range(n_columnas):
        nodo_id = i * n_columnas + j
        x, y = j * 20, i * 20
        posiciones[nodo_id] = (x, y)
        G.add_node(nodo_id, tipo='vacio', pos=(x, y))

# Seleccionar una central eléctrica aleatoria (nodo amarillo)
central = random.choice(list(G.nodes))
G.nodes[central]['tipo'] = 'central'

# Esta funcion nos jala para hacer que las colonias aleatorias que esten conectadas con la red electrica'
def expandir_colonias(G, central, max_colonias=6):
    visitados = set()
    pq = PriorityQueue()
    visitados.add(central)
    contador_colonias = 0

    for vecino in obtener_vecinos(central):
        peso = random.randint(1, 15)
        pq.put((peso, central, vecino))

    while not pq.empty() and contador_colonias < max_colonias:
        peso, u, v = pq.get()
        if v not in visitados:
            G.add_edge(u, v, peso=peso)
            G.nodes[v]['tipo'] = 'colonia'
            nodos_colonia.add(v)
            visitados.add(v)
            contador_colonias += 1
            for vecino in obtener_vecinos(v):
                if vecino not in visitados:
                    peso = random.randint(5, 15)
                    pq.put((peso, v, vecino))

# Revisa los nodos vecinos sumando y restando el valor i y j
def obtener_vecinos(nodo):
    i, j = divmod(nodo, n_columnas)
    vecinos = []
    if i > 0:
        vecinos.append((i - 1) * n_columnas + j)
    if i < n_filas - 1:
        vecinos.append((i + 1) * n_columnas + j)
    if j > 0:
        vecinos.append(i * n_columnas + (j - 1))
    if j < n_columnas - 1:
        vecinos.append(i * n_columnas + (j + 1))
    return vecinos

expandir_colonias(G, central)

# Ponemos valores de peso a lazar en los aristas de 2 - 15

for i in range(n_filas):
    for j in range(n_columnas):
        nodo_actual = i * n_columnas + j
        for vecino in obtener_vecinos(nodo_actual):
            if not G.has_edge(nodo_actual, vecino):
                peso = random.randint(2, 15)
                G.add_edge(nodo_actual, vecino, peso=peso)

#Definimos una funcion para poder usar la libreria network

def visualizar_mapa_red(G, titulo="Red eléctrica - Mapeo inicial"):
    pos = nx.get_node_attributes(G, 'pos')
    colores = {'vacio': 'lightgray', 'colonia': 'green', 'central': 'yellow'}
    node_colors = [colores[G.nodes[n]['tipo']] for n in G.nodes]

    plt.figure(figsize=(10, 8))
    plt.get_current_fig_manager().full_screen_toggle()
    nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=700, font_size=8)

    pesos = {(u, v): G[u][v]['peso'] for u, v in G.edges}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=pesos, font_size=6)

    leyendas = {
        'colonia': 'Colonia con luz',
        'vacio': 'Colonia sin luz',
        'central': 'Central eléctrica'
    }

    for tipo, color in colores.items():
        plt.scatter([], [], c=color, label=leyendas[tipo], edgecolors='black')
    
    plt.legend(scatterpoints=1, frameon=True, labelspacing=1, title="Leyenda")
    plt.axis('equal')
    plt.tight_layout()
    plt.title(titulo)
    
    #Agregamos la wea del boton para mostrar el prim
    ax_boton = plt.axes([0.80, 0.10, 0.15, 0.05])
    boton = Button(ax_boton, 'Mostrar ruta Prim')

    def cerrar(event):
        plt.close()

    boton.on_clicked(cerrar)
    plt.show()

visualizar_mapa_red(G, titulo="Generacion de los nodos")


#--- Aqui empieza el codigo para el segundo mapeo de los nodos que se conecten con el metodo prim

def obtener_subgrafo_luz(G):
    # Filtra nodos centrales y colonias (los que tienen ya tienen luz para que entiendan)
    nodos_con_luz = [n for n, attr in G.nodes(data=True) if attr['tipo'] in ['central', 'colonia']]
    return G.subgraph(nodos_con_luz).copy()

# Este es el prim mejorado (lo extendi pa que lo estudien)

def mst_prim(G_sub):
    if len(G_sub.nodes) == 0:
        return nx.Graph()
    
    nodo_inicio = None
    for n in G_sub.nodes:
        if G_sub.nodes[n]['tipo'] == 'central':
            nodo_inicio = n
            break
    
    mst = nx.Graph()
    visitados = set([nodo_inicio])
    aristas_disponibles = []
    
    # Inicializar con las aristas del nodo inicial
    for vecino in G_sub.neighbors(nodo_inicio):
        peso = G_sub[nodo_inicio][vecino]['peso']
        heapq.heappush(aristas_disponibles, (peso, nodo_inicio, vecino))
    
    while aristas_disponibles:
        peso, u, v = heapq.heappop(aristas_disponibles)
        
        if v not in visitados:
            mst.add_edge(u, v, peso=peso)
            visitados.add(v)
            
            # Agregar nuevas aristas al heap
            for vecino in G_sub.neighbors(v):
                if vecino not in visitados:
                    nuevo_peso = G_sub[v][vecino]['peso']
                    heapq.heappush(aristas_disponibles, (nuevo_peso, v, vecino))
    
    return mst

def visualizar_red_con_mst(G, mst, titulo="Red eléctrica conectada con prim"):
    pos = nx.get_node_attributes(G, 'pos')
    
    colores = []
    for n in G.nodes:
        tipo = G.nodes[n]['tipo']
        if tipo == 'central':
            colores.append('yellow')
        elif tipo == 'colonia':
            colores.append('green')
        else:
            colores.append('lightgray')
    
    plt.figure(figsize=(12, 9))
    plt.get_current_fig_manager().full_screen_toggle()  # Abrir en pantalla completa
    
    # Dibujar grafo completo con nodos y aristas normales
    nx.draw_networkx_nodes(G, pos, node_color=colores, node_size=700, edgecolors='black')
    nx.draw_networkx_edges(G, pos, alpha=0.4)
    nx.draw_networkx_labels(G, pos, font_size=8)

    pesos = {(u, v): G[u][v]['peso'] for u, v in G.edges}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=pesos, font_size=6)
    
    #Remarcamos el camino que usa prim
    nx.draw_networkx_edges(mst, pos, edge_color='blue', width=3)
    
    nx.draw_networkx_nodes(mst, pos, node_color=[colores[n] for n in mst.nodes], node_size=900, edgecolors='black')
    
    total_mst = sum(G[u][v]['peso'] for u, v in mst.edges)

    # Leyenda
    leyendas = {
        'colonia': 'Colonia con luz',
        'central': 'Central eléctrica',
        'vacio': 'Colonia sin luz',
        'mst': f'Conexion Prim (Total:{total_mst})'
    }
    for tipo, color in {'colonia': 'green', 'central': 'yellow', 'vacio': 'lightgray', 'mst': 'blue'}.items():
        plt.scatter([], [], c=color, label=leyendas[tipo], edgecolors='black' if tipo != 'mst' else 'none')
    
    plt.legend(scatterpoints=1, frameon=True, labelspacing=1, title="Leyenda")
    plt.title(titulo)
    plt.axis('equal')
    plt.tight_layout()

    ax_boton = plt.axes([0.80, 0.10, 0.15, 0.05])
    boton = Button(ax_boton, 'Mostrar ruta Kruskal')

    def cerrar(event):
        plt.close()

    boton.on_clicked(cerrar)

    plt.show()

G_luz = obtener_subgrafo_luz(G)
mst_luz = mst_prim(G_luz)

# Ya que tenemos la ruta con el prim solo la resaltamoss
visualizar_red_con_mst(G, mst_luz)

#--- Aqui empieza el tercer mapeo que va a usar kruskal para conectar los nodos vacios (colonias sin luz)

def kruskal_expandir_completo(G, mst):
    G_exp = nx.Graph()
    G_exp.add_nodes_from(G.nodes(data=True))
    G_exp.add_edges_from(mst.edges(data=True))

    aristas_todas = [(G[u][v]['peso'], u, v) for u, v in G.edges if not G_exp.has_edge(u, v)]
    aristas_todas.sort()

    for peso, u, v in aristas_todas:
        if not nx.has_path(G_exp, u, v):
            G_exp.add_edge(u, v, peso=peso)

    return G_exp

def visualizar_kruskal_completo(G, mst, kruskal_final, titulo="Red eléctrica final usando Kruskal"):
    pos = nx.get_node_attributes(G, 'pos')

    colores = []
    for n in G.nodes:
        tipo = G.nodes[n]['tipo']
        if tipo == 'central':
            colores.append('yellow')
        elif tipo == 'colonia':
            colores.append('green')
        else:
            colores.append('blue')

    plt.figure(figsize=(12, 9))
    plt.get_current_fig_manager().full_screen_toggle()  # Abrir en pantalla completa
    nx.draw_networkx_nodes(G, pos, node_color=colores, node_size=700, edgecolors='black')
    nx.draw_networkx_labels(G, pos, font_size=8)
    nx.draw_networkx_edges(G, pos, alpha=0.3)
    pesos = {(u, v): G[u][v]['peso'] for u, v in G.edges}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=pesos, font_size=6)

    # Dejamos el resaltado del camino con prim
    nx.draw_networkx_edges(mst, pos, edge_color='green', width=3)

    # Nuevas conexiones de kruskal final en azul
    nuevas = [e for e in kruskal_final.edges if e not in mst.edges and (e[1], e[0]) not in mst.edges]
    nx.draw_networkx_edges(kruskal_final, pos, edgelist=nuevas, edge_color='blue', width=2)

    total_final = sum(G[u][v]['peso'] for u, v in kruskal_final.edges)
    print(f"Costo total de red expandida (Kruskal): {total_final}")
    

    leyendas = {
        'colonia': 'Colonia con luz',
        'central': 'Central eléctrica',
        'vacio': 'Colonia sin luz',
        'mst': 'Conexion Prim',
        'kruskal': f'Conexion Kruskal (Total: {total_final})'
    }
    colores_leyenda = {'colonia': 'green', 'central': 'yellow', 'vacio': 'lightgray', 'mst': 'green', 'kruskal': 'blue'}
    for tipo, color in colores_leyenda.items():
        plt.scatter([], [], c=color, label=leyendas[tipo], edgecolors='black' if tipo not in ['mst', 'kruskal'] else 'none')

    plt.legend(scatterpoints=1, frameon=True, labelspacing=1, title="Leyenda")
    plt.title(titulo)
    plt.axis('equal')
    plt.tight_layout()

    ax_boton = plt.axes([0.80, 0.10, 0.15, 0.05])
    boton = Button(ax_boton, 'Cerrar visualización')

    def cerrar(event):
        plt.close()

    boton.on_clicked(cerrar)

    plt.show()

red_final = kruskal_expandir_completo(G, mst_luz)
visualizar_kruskal_completo(G, mst_luz, red_final)
