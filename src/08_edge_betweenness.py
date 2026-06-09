#!/usr/bin/env python3
"""
Calcula edge betweenness centrality exata em um grafo de coautoria não direcionado.

Entrada esperada:
- neo4j_import/authors_nodes.csv
- neo4j_import/coauthorship_edges.csv

Saída:
- CSV com o betweenness de todas as arestas
- CSV auxiliar com as 30 arestas de maior edge betweenness

Observações:
- O cálculo usa a versão não ponderada do grafo, para ficar alinhado com a
  betweenness de nós usada no relatório.
- Em grafos com dezenas de milhares de nós, o cálculo exato pode demorar bastante.
"""

from __future__ import annotations

import argparse
import csv
import math
import time
from collections import deque
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Calcula as arestas com maior edge betweenness centrality."
    )
    parser.add_argument(
        "--nodes",
        default="neo4j_import/authors_nodes.csv",
        help="CSV de nós exportado para o Neo4j.",
    )
    parser.add_argument(
        "--edges",
        default="neo4j_import/coauthorship_edges.csv",
        help="CSV de arestas exportado para o Neo4j.",
    )
    parser.add_argument(
        "--output",
        default="tabela_relatorio/all_edge_betweenness.csv",
        help="CSV de saída com o betweenness de todas as arestas.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=30,
        help="Quantidade de arestas a salvar no ranking auxiliar.",
    )
    return parser.parse_args()


def load_data(
    nodes_path: Path, edges_path: Path
) -> Tuple[List[str], Dict[str, Dict[str, str]], List[Tuple[str, str]]]:
    nodes_df = pd.read_csv(nodes_path, dtype=str)
    edges_df = pd.read_csv(edges_path, dtype=str)

    node_id_col = "author_id:ID(Author)"
    name_col = "author_name"
    macroarea_col = "author_primary_macroarea"

    node_ids = nodes_df[node_id_col].astype(str).tolist()
    node_attrs = {
        row[node_id_col]: {
            "author_name": row.get(name_col, ""),
            "author_primary_macroarea": row.get(macroarea_col, ""),
        }
        for _, row in nodes_df.iterrows()
    }

    edges = list(
        zip(
            edges_df[":START_ID(Author)"].astype(str),
            edges_df[":END_ID(Author)"].astype(str),
        )
    )
    return node_ids, node_attrs, edges


def build_graph(
    node_ids: Sequence[str], edges: Iterable[Tuple[str, str]]
) -> Tuple[List[str], Dict[str, int], List[List[int]], List[Tuple[int, int]]]:
    id_to_idx = {node_id: idx for idx, node_id in enumerate(node_ids)}
    adjacency: List[List[int]] = [[] for _ in node_ids]
    undirected_edges: List[Tuple[int, int]] = []
    seen = set()

    for src_id, dst_id in edges:
        if src_id == dst_id:
            continue
        try:
            src = id_to_idx[src_id]
            dst = id_to_idx[dst_id]
        except KeyError:
            continue

        edge = (src, dst) if src < dst else (dst, src)
        if edge in seen:
            continue
        seen.add(edge)
        adjacency[src].append(dst)
        adjacency[dst].append(src)
        undirected_edges.append(edge)

    return list(node_ids), id_to_idx, adjacency, undirected_edges


def edge_betweenness_unweighted(
    adjacency: Sequence[Sequence[int]],
    sources: Sequence[int],
) -> Dict[Tuple[int, int], float]:
    n = len(adjacency)
    scores: Dict[Tuple[int, int], float] = {}
    source_count = len(sources)
    start = time.time()

    for processed, s in enumerate(sources, start=1):
        stack: List[int] = []
        preds: List[List[int]] = [[] for _ in range(n)]
        sigma = [0.0] * n
        dist = [-1] * n

        sigma[s] = 1.0
        dist[s] = 0
        queue = deque([s])

        while queue:
            v = queue.popleft()
            stack.append(v)
            next_dist = dist[v] + 1
            for w in adjacency[v]:
                if dist[w] < 0:
                    queue.append(w)
                    dist[w] = next_dist
                if dist[w] == next_dist:
                    sigma[w] += sigma[v]
                    preds[w].append(v)

        delta = [0.0] * n
        while stack:
            w = stack.pop()
            if sigma[w] == 0:
                continue
            coeff = (1.0 + delta[w]) / sigma[w]
            for v in preds[w]:
                contribution = sigma[v] * coeff
                edge = (v, w) if v < w else (w, v)
                scores[edge] = scores.get(edge, 0.0) + contribution
                delta[v] += contribution

        if processed % 100 == 0 or processed == source_count:
            elapsed = time.time() - start
            rate = processed / elapsed if elapsed > 0 else 0.0
            eta = (source_count - processed) / rate if rate > 0 else math.inf
            eta_str = f"{eta:.1f}s" if math.isfinite(eta) else "inf"
            print(
                f"[{processed}/{source_count}] fontes processadas "
                f"({rate:.2f} fontes/s, ETA {eta_str})"
            )

    # Grafo não direcionado: cada caminho é contado duas vezes.
    for edge in list(scores.keys()):
        scores[edge] /= 2.0
    return scores


def build_output_rows(
    scores: Dict[Tuple[int, int], float],
    node_ids: Sequence[str],
    node_attrs: Dict[str, Dict[str, str]],
    top_n: int | None = None,
) -> List[Dict[str, object]]:
    rows = []
    ranked_edges = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    if top_n is not None:
        ranked_edges = ranked_edges[:top_n]
    for (src_idx, dst_idx), score in ranked_edges:
        src_id = node_ids[src_idx]
        dst_id = node_ids[dst_idx]
        src_attrs = node_attrs[src_id]
        dst_attrs = node_attrs[dst_id]
        src_macro = src_attrs.get("author_primary_macroarea", "")
        dst_macro = dst_attrs.get("author_primary_macroarea", "")
        rows.append(
            {
                "author_id_source": src_id,
                "author_name_source": src_attrs.get("author_name", ""),
                "macroarea_source": src_macro,
                "author_id_target": dst_id,
                "author_name_target": dst_attrs.get("author_name", ""),
                "macroarea_target": dst_macro,
                "same_macroarea": src_macro == dst_macro,
                "edge_betweenness": round(score, 6),
            }
        )
    return rows


def write_csv(rows: Sequence[Dict[str, object]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError("Nenhuma linha gerada para escrita.")
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    nodes_path = Path(args.nodes)
    edges_path = Path(args.edges)
    output_path = Path(args.output)
    top_output_path = output_path.with_name(f"top{args.top}_" + output_path.name)

    print("Carregando dados...")
    node_ids, node_attrs, edges = load_data(nodes_path, edges_path)
    node_ids, _, adjacency, undirected_edges = build_graph(node_ids, edges)
    print(
        f"Grafo carregado: {len(node_ids)} nós, {len(undirected_edges)} arestas não direcionadas."
    )

    sources = list(range(len(node_ids)))
    print("Executando cálculo exato de edge betweenness.")
    scores = edge_betweenness_unweighted(adjacency, sources)
    all_rows = build_output_rows(scores, node_ids, node_attrs)
    top_rows = all_rows[: args.top]
    write_csv(all_rows, output_path)
    write_csv(top_rows, top_output_path)

    print(f"Resultado salvo em: {output_path}")
    print(f"Top {args.top} salvo em: {top_output_path}")
    print("Top arestas:")
    for row in top_rows[: min(5, len(top_rows))]:
        print(
            f"- {row['author_name_source']} <-> {row['author_name_target']}: "
            f"{row['edge_betweenness']}"
        )


if __name__ == "__main__":
    main()
