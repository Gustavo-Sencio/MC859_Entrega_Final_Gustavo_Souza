import csv
from pathlib import Path
import xml.etree.ElementTree as ET


GRAPHML_PATH = Path("coauthorship.graphml")
OUTPUT_DIR = Path("neo4j_import")
NODES_CSV = OUTPUT_DIR / "authors_nodes.csv"
EDGES_CSV = OUTPUT_DIR / "coauthorship_edges.csv"

GRAPHML_NS = {"g": "http://graphml.graphdrawing.org/xmlns"}


NODE_FIELDS = [
    "author_id:ID(Author)",
    "author_name",
    "university",
    "city",
    "author_primary_macroarea",
    "author_macroareas",
    "author_topics",
    "article_count:int",
    ":LABEL",
]

EDGE_FIELDS = [
    ":START_ID(Author)",
    ":END_ID(Author)",
    "weight:int",
    ":TYPE",
]


def data_por_key(element):
    return {data.get("key"): data.text or "" for data in element.findall("g:data", GRAPHML_NS)}


def exportar_csvs():
    OUTPUT_DIR.mkdir(exist_ok=True)

    root = ET.parse(GRAPHML_PATH).getroot()

    node_count = 0
    with NODES_CSV.open("w", newline="", encoding="utf-8") as arquivo:
        writer = csv.writer(arquivo)
        writer.writerow(NODE_FIELDS)

        for node in root.findall(".//g:node", GRAPHML_NS):
            values = data_por_key(node)
            writer.writerow(
                [
                    values.get("author_id", node.get("id", "")),
                    values.get("author_name", ""),
                    values.get("university", ""),
                    values.get("city", ""),
                    values.get("author_primary_macroarea", ""),
                    values.get("author_macroareas", ""),
                    values.get("author_topics", ""),
                    values.get("article_count", "0"),
                    "Author",
                ]
            )
            node_count += 1

    edge_count = 0
    with EDGES_CSV.open("w", newline="", encoding="utf-8") as arquivo:
        writer = csv.writer(arquivo)
        writer.writerow(EDGE_FIELDS)

        for edge in root.findall(".//g:edge", GRAPHML_NS):
            values = data_por_key(edge)
            writer.writerow(
                [
                    edge.get("source", ""),
                    edge.get("target", ""),
                    values.get("weight", "1"),
                    "COAUTHORED_WITH",
                ]
            )
            edge_count += 1

    print(f"Nos exportados: {node_count} -> {NODES_CSV}")
    print(f"Arestas exportadas: {edge_count} -> {EDGES_CSV}")


if __name__ == "__main__":
    exportar_csvs()
