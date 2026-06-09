import os
import csv
from collections import Counter, defaultdict, deque
from pathlib import Path
import xml.etree.ElementTree as ET

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


GRAPHML_PATH = Path("coauthorship.graphml")
OUTPUT_DIR = Path("analysis_output")
SUMMARY_PATH = OUTPUT_DIR / "graph_summary.md"
DEGREE_PLOT_PATH = OUTPUT_DIR / "degree_distribution.png"
COMPONENT_PLOT_PATH = OUTPUT_DIR / "component_size_distribution.png"
DEGREE_CSV_PATH = OUTPUT_DIR / "degree_distribution.csv"
COMPONENT_CSV_PATH = OUTPUT_DIR / "component_size_distribution.csv"
WEIGHTED_DEGREE_PLOT_PATH = OUTPUT_DIR / "weighted_degree_distribution.png"
WEIGHTED_DEGREE_CSV_PATH = OUTPUT_DIR / "weighted_degree_distribution.csv"
VERTEX_METRICS_CSV_PATH = OUTPUT_DIR / "vertex_metrics.csv"
DEGREE_AVG_WEIGHTED_PLOT_PATH = OUTPUT_DIR / "average_weighted_degree_by_degree.png"

GRAPHML_NS = {"g": "http://graphml.graphdrawing.org/xmlns"}


def carregar_grafo(graphml_path):
    tree = ET.parse(graphml_path)
    root = tree.getroot()

    nodes = set()
    adjacency = defaultdict(set)
    weighted_degree = defaultdict(int)
    edge_count = 0

    for node in root.findall(".//g:node", GRAPHML_NS):
        node_id = node.get("id")
        if node_id:
            nodes.add(node_id)
            adjacency[node_id]
            weighted_degree[node_id]

    for edge in root.findall(".//g:edge", GRAPHML_NS):
        source = edge.get("source")
        target = edge.get("target")
        if not source or not target:
            continue

        weight = 1
        for data in edge.findall("g:data", GRAPHML_NS):
            if data.get("key") == "weight":
                try:
                    weight = int(data.text)
                except (TypeError, ValueError):
                    weight = 1
                break

        nodes.add(source)
        nodes.add(target)
        adjacency[source].add(target)
        adjacency[target].add(source)
        weighted_degree[source] += weight
        weighted_degree[target] += weight
        edge_count += 1

    return nodes, adjacency, weighted_degree, edge_count


def calcular_componentes(nodes, adjacency):
    visited = set()
    component_sizes = []

    for node in nodes:
        if node in visited:
            continue

        queue = deque([node])
        visited.add(node)
        size = 0

        while queue:
            current = queue.popleft()
            size += 1
            for neighbor in adjacency[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        component_sizes.append(size)

    component_sizes.sort(reverse=True)
    return component_sizes


def plotar_distribuicao_graus(degree_counter, output_path):
    graus = sorted(degree_counter)
    frequencias = [degree_counter[grau] for grau in graus]

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(graus, frequencias, width=0.9, color="#1f77b4")
    ax.set_title("Distribuição de Graus")
    ax.set_xlabel("Grau do vértice")
    ax.set_ylabel("Número de vértices")

    if graus and max(graus) > 20:
        ax.set_yscale("log")
        ax.set_ylabel("Número de vértices (escala log)")

    #TICKS NO EIXO X
    if graus:
        max_grau = max(graus)

        # ticks principais
        ax.set_xticks(np.arange(0, max_grau + 1, 20))

        # ticks menores
        ax.set_xticks(np.arange(0, max_grau + 1, 10), minor=True)

        # tamanho dos ticks menores
        ax.tick_params(axis='x', which='minor', length=4)

    # grid 
    ax.grid(True, which='both', axis='both', linestyle=':', linewidth=0.5, alpha=0.7)

    fig.tight_layout()
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def plotar_distribuicao_grau_ponderado(weighted_degree_counter, output_path):
    graus = sorted(weighted_degree_counter)
    frequencias = [weighted_degree_counter[grau] for grau in graus]

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(graus, frequencias, width=0.9, color="#2ca02c")
    ax.set_title("Distribuição do Grau Ponderado")
    ax.set_xlabel("Grau ponderado")
    ax.set_ylabel("Número de vértices")

    if graus and max(graus) > 20:
        ax.set_yscale("log")
        ax.set_ylabel("Número de vértices (escala log)")

    #TICKS NO EIXO X
    if graus:
        max_grau = max(graus)

        # ticks principais
        ax.set_xticks(np.arange(0, max_grau + 1, 50))

        # ticks menores
        ax.set_xticks(np.arange(0, max_grau + 1, 25), minor=True)

        # tamanho dos ticks menores
        ax.tick_params(axis='x', which='minor', length=4)

    # grid
    ax.grid(True, which='both', axis='both', linestyle=':', linewidth=0.5, alpha=0.7)

    fig.tight_layout()
    fig.savefig(output_path, dpi=350)
    plt.close(fig)


def plotar_distribuicao_componentes(component_size_counter, output_path):
    tamanhos = sorted(component_size_counter)
    quantidades = [component_size_counter[tamanho] for tamanho in tamanhos]
    fig, (ax_full, ax_zoom) = plt.subplots(1, 2, figsize=(12, 5))

    ax_full.plot(tamanhos, quantidades, marker="o", linestyle="-", color="#ff7f0e", markersize=4)
    ax_full.set_title("Distribuição Completa")
    ax_full.set_xlabel("Tamanho da componente (k)")
    ax_full.set_ylabel("Quantidade de componentes de tamanho k")
    ax_full.set_xscale("log")
    ax_full.set_yscale("log")
    ax_full.grid(True, which="both", linestyle=":", linewidth=0.5, alpha=0.7)

    if tamanhos:
        maior_tamanho = max(tamanhos)
        tamanhos_zoom = [t for t in tamanhos if t < maior_tamanho]
        quantidades_zoom = [component_size_counter[t] for t in tamanhos_zoom]
    else:
        tamanhos_zoom = []
        quantidades_zoom = []

    if tamanhos_zoom:
        ax_zoom.plot(
            tamanhos_zoom,
            quantidades_zoom,
            marker="o",
            linestyle="-",
            color="#d62728",
            markersize=4,
        )
        ax_zoom.set_xscale("log")
        ax_zoom.set_yscale("log")
        ax_zoom.set_title("Sem a maior componente")
        ax_zoom.set_xlabel("Tamanho da componente (k)")
        ax_zoom.set_ylabel("Quantidade de componentes de tamanho k")
        
        # grid
        ax_zoom.grid(True, which="both", linestyle=":", linewidth=0.5, alpha=0.7)
    else:
        ax_zoom.text(0.5, 0.5, "Nao ha componentes para zoom", ha="center", va="center")
        ax_zoom.set_axis_off()

    fig.suptitle("Distribuição dos Tamanhos das Componentes", fontsize=14)
    fig.tight_layout()
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def plotar_comparacao_graus(nodes, adjacency, weighted_degree, average_output_path):
    graus_para_ponderados = defaultdict(list)
    for node in nodes:
        grau = len(adjacency[node])
        graus_para_ponderados[grau].append(weighted_degree[node])

    graus_ordenados = sorted(graus_para_ponderados)
    medias_ponderadas = [
        sum(graus_para_ponderados[grau]) / len(graus_para_ponderados[grau])
        for grau in graus_ordenados
    ]

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(graus_ordenados, medias_ponderadas, marker="o", markersize=4, color="#8c564b")
    ax.plot(graus_ordenados, graus_ordenados, linestyle="--", color="#7f7f7f", linewidth=1.5, label="y = x")
    ax.set_title("Média do Grau Ponderado por Grau")
    ax.set_xlabel("Grau")
    ax.set_ylabel("Média do grau ponderado")

    #TICKS NO EIXO X
    max_grau = max(graus_ordenados)
    ax.set_xticks(np.arange(0, max_grau + 1, 20))
    ax.set_xticks(np.arange(0, max_grau + 1, 10), minor=True)
    ax.tick_params(axis='x', which='minor', length=4)

    #TICKS NO EIXO Y
    max_grau = max(medias_ponderadas)
    ax.set_yticks(np.arange(0, max_grau + 1, 50))
    ax.set_yticks(np.arange(0, max_grau + 1, 25), minor=True)
    ax.tick_params(axis='y', which='minor', length=4)

    ax.grid(True, which="both", linestyle=":", linewidth=0.5, alpha=0.7)
    ax.legend()
    fig.tight_layout()
    fig.savefig(average_output_path, dpi=220)
    plt.close(fig)


def salvar_distribuicao_graus_csv(degree_counter, output_path):
    with output_path.open("w", newline="", encoding="utf-8") as arquivo:
        writer = csv.writer(arquivo)
        writer.writerow(["grau", "quantidade_vertices"])
        for grau in sorted(degree_counter):
            writer.writerow([grau, degree_counter[grau]])


def salvar_distribuicao_componentes_csv(component_size_counter, output_path):
    with output_path.open("w", newline="", encoding="utf-8") as arquivo:
        writer = csv.writer(arquivo)
        writer.writerow(["tamanho_componente", "quantidade_componentes"])
        for tamanho in sorted(component_size_counter):
            writer.writerow([tamanho, component_size_counter[tamanho]])


def salvar_distribuicao_grau_ponderado_csv(weighted_degree_counter, output_path):
    with output_path.open("w", newline="", encoding="utf-8") as arquivo:
        writer = csv.writer(arquivo)
        writer.writerow(["grau_ponderado", "quantidade_vertices"])
        for grau in sorted(weighted_degree_counter):
            writer.writerow([grau, weighted_degree_counter[grau]])


def salvar_metricas_vertices_csv(nodes, adjacency, weighted_degree, output_path):
    with output_path.open("w", newline="", encoding="utf-8") as arquivo:
        writer = csv.writer(arquivo)
        writer.writerow(["author_id", "grau", "grau_ponderado"])
        for node in sorted(nodes):
            writer.writerow([node, len(adjacency[node]), weighted_degree[node]])


def escrever_resumo(
    output_path,
    graphml_path,
    vertex_count,
    edge_count,
    average_degree,
    average_weighted_degree,
    component_sizes,
    degree_counter,
):
    component_count = len(component_sizes)
    largest_component = component_sizes[0] if component_sizes else 0
    isolated_vertices = degree_counter.get(0, 0)

    with output_path.open("w", encoding="utf-8") as arquivo:
        arquivo.write("# Resumo do Grafo\n\n")
        arquivo.write(f"- Arquivo analisado: `{graphml_path}`\n")
        arquivo.write(f"- Numero de vertices: `{vertex_count}`\n")
        arquivo.write(f"- Numero de arestas: `{edge_count}`\n")
        arquivo.write(f"- Grau medio: `{average_degree:.4f}`\n")
        arquivo.write(f"- Grau ponderado medio: `{average_weighted_degree:.4f}`\n")
        arquivo.write(f"- Numero de componentes conexas: `{component_count}`\n")
        arquivo.write(f"- Tamanho da maior componente: `{largest_component}`\n")
        arquivo.write(f"- Vertices isolados: `{isolated_vertices}`\n")
        arquivo.write("\n")
        arquivo.write("## Arquivos gerados\n\n")
        arquivo.write(f"- `{DEGREE_PLOT_PATH}`\n")
        arquivo.write(f"- `{COMPONENT_PLOT_PATH}`\n")
        arquivo.write(f"- `{DEGREE_CSV_PATH}`\n")
        arquivo.write(f"- `{COMPONENT_CSV_PATH}`\n")
        arquivo.write(f"- `{WEIGHTED_DEGREE_PLOT_PATH}`\n")
        arquivo.write(f"- `{WEIGHTED_DEGREE_CSV_PATH}`\n")
        arquivo.write(f"- `{VERTEX_METRICS_CSV_PATH}`\n")
        arquivo.write(f"- `{DEGREE_AVG_WEIGHTED_PLOT_PATH}`\n")


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    nodes, adjacency, weighted_degree, edge_count = carregar_grafo(GRAPHML_PATH)
    degree_counter = Counter(len(adjacency[node]) for node in nodes)
    weighted_degree_counter = Counter(weighted_degree[node] for node in nodes)
    vertex_count = len(nodes)
    average_degree = (2 * edge_count / vertex_count) if vertex_count else 0.0
    average_weighted_degree = (
        sum(weighted_degree[node] for node in nodes) / vertex_count if vertex_count else 0.0
    )

    component_sizes = calcular_componentes(nodes, adjacency)
    component_size_counter = Counter(component_sizes)

    plotar_distribuicao_graus(degree_counter, DEGREE_PLOT_PATH)
    plotar_distribuicao_grau_ponderado(weighted_degree_counter, WEIGHTED_DEGREE_PLOT_PATH)
    plotar_distribuicao_componentes(component_size_counter, COMPONENT_PLOT_PATH)
    plotar_comparacao_graus(nodes, adjacency, weighted_degree, DEGREE_AVG_WEIGHTED_PLOT_PATH)
    salvar_distribuicao_graus_csv(degree_counter, DEGREE_CSV_PATH)
    salvar_distribuicao_componentes_csv(component_size_counter, COMPONENT_CSV_PATH)
    salvar_distribuicao_grau_ponderado_csv(weighted_degree_counter, WEIGHTED_DEGREE_CSV_PATH)
    salvar_metricas_vertices_csv(nodes, adjacency, weighted_degree, VERTEX_METRICS_CSV_PATH)
    escrever_resumo(
        SUMMARY_PATH,
        GRAPHML_PATH,
        vertex_count,
        edge_count,
        average_degree,
        average_weighted_degree,
        component_sizes,
        degree_counter,
    )

    print(f"Número de vertices: {vertex_count}")
    print(f"Número de arestas: {edge_count}")
    print(f"Grau medio: {average_degree:.4f}")
    print(f"Grau ponderado medio: {average_weighted_degree:.4f}")
    print(f"Número de componentes conexas: {len(component_sizes)}")
    print(f"Maior componente: {component_sizes[0] if component_sizes else 0}")
    print(f"Resumo salvo em: {SUMMARY_PATH}")
    print(f"Figura de graus salva em: {DEGREE_PLOT_PATH}")
    print(f"Figura de componentes salva em: {COMPONENT_PLOT_PATH}")
    print(f"CSV de graus salvo em: {DEGREE_CSV_PATH}")
    print(f"CSV de componentes salvo em: {COMPONENT_CSV_PATH}")
    print(f"Figura de grau ponderado salva em: {WEIGHTED_DEGREE_PLOT_PATH}")
    print(f"CSV de grau ponderado salvo em: {WEIGHTED_DEGREE_CSV_PATH}")
    print(f"CSV de métricas por vértice salvo em: {VERTEX_METRICS_CSV_PATH}")
    print(f"Figura da média do grau ponderado por grau salva em: {DEGREE_AVG_WEIGHTED_PLOT_PATH}")


if __name__ == "__main__":
    main()
