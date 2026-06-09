import csv
from collections import defaultdict
from itertools import combinations
from pathlib import Path
import xml.etree.ElementTree as ET


ARTICLES_CSV = Path("articles.csv")
AUTHORS_CSV = Path("authors.csv")
AUTHOR_THEMATIC_CSV = Path("author_macroareas_output/author_macroareas_from_articles.csv")
OUTPUT_GRAPHML = Path("coauthorship.graphml")

GRAPHML_NS = "http://graphml.graphdrawing.org/xmlns"
XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"
SCHEMA_LOCATION = (
    "http://graphml.graphdrawing.org/xmlns "
    "http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd"
)

ET.register_namespace("", GRAPHML_NS)
ET.register_namespace("xsi", XSI_NS)


def carregar_autores_base(caminho_autores):
    autores = {}
    with caminho_autores.open("r", newline="", encoding="utf-8") as arquivo:
        reader = csv.DictReader(arquivo)
        for row in reader:
            author_id = row.get("author_id")
            if not author_id:
                continue
            autores[author_id] = {
                "author_id": author_id,
                "nome": row.get("nome", ""),
                "universidade": row.get("universidade", ""),
                "cidade": row.get("cidade", ""),
                "macro_area_principal_no_recorte": "",
                "macro_areas_no_recorte": "",
                "temas_no_recorte": "",
            }
    return autores


def carregar_autores_tematicos(caminho_autores, autores):
    with caminho_autores.open("r", newline="", encoding="utf-8") as arquivo:
        reader = csv.DictReader(arquivo)
        for row in reader:
            author_id = row.get("author_id")
            if not author_id:
                continue
            if author_id not in autores:
                autores[author_id] = {
                    "author_id": author_id,
                    "nome": "",
                    "universidade": "",
                    "cidade": "",
                    "macro_area_principal_no_recorte": "",
                    "macro_areas_no_recorte": "",
                    "temas_no_recorte": "",
                }
            autores[author_id].update(
                {
                    "macro_area_principal_no_recorte": row.get("macro_area_principal_no_recorte", ""),
                    "macro_areas_no_recorte": row.get("macro_areas_no_recorte", ""),
                    "temas_no_recorte": row.get("temas_no_recorte", ""),
                }
            )
    return autores


def carregar_artigos():
    artigos = {}
    artigos_por_autor = defaultdict(int)

    with ARTICLES_CSV.open("r", newline="", encoding="utf-8") as arquivo:
        reader = csv.DictReader(arquivo)
        for row in reader:
            eid = row.get("eid")
            author_id = row.get("author_id")
            if not eid or not author_id:
                continue

            artigo = artigos.setdefault(
                eid,
                {
                    "titulo": row.get("titulo", ""),
                    "ano": row.get("ano", ""),
                    "source": row.get("source", ""),
                    "authors": set(),
                },
            )

            if author_id not in artigo["authors"]:
                artigo["authors"].add(author_id)
                artigos_por_autor[author_id] += 1

    return artigos, artigos_por_autor


def construir_arestas(artigos):
    pesos = defaultdict(int)

    for artigo in artigos.values():
        autores = sorted(artigo["authors"])
        for origem, destino in combinations(autores, 2):
            pesos[(origem, destino)] += 1

    return pesos


def subelemento_data(elemento_pai, key, valor):
    data = ET.SubElement(elemento_pai, f"{{{GRAPHML_NS}}}data", key=key)
    data.text = "" if valor is None else str(valor)


def adicionar_keys(root):
    definicoes = [
        ("author_id", "node", "author_id", "string"),
        ("author_name", "node", "nome", "string"),
        ("university", "node", "universidade", "string"),
        ("city", "node", "cidade", "string"),
        ("author_primary_macroarea", "node", "macro_area_principal_no_recorte", "string"),
        ("author_macroareas", "node", "macro_areas_no_recorte", "string"),
        ("author_topics", "node", "temas_no_recorte", "string"),
        ("article_count", "node", "article_count", "int"),
        ("weight", "edge", "weight", "int"),
    ]

    for key_id, alvo, nome, tipo in definicoes:
        ET.SubElement(
            root,
            f"{{{GRAPHML_NS}}}key",
            id=key_id,
            **{"for": alvo, "attr.name": nome, "attr.type": tipo},
        )


def montar_graphml(autores, artigos_por_autor, arestas):
    root = ET.Element(
        f"{{{GRAPHML_NS}}}graphml",
        {f"{{{XSI_NS}}}schemaLocation": SCHEMA_LOCATION},
    )
    adicionar_keys(root)

    graph = ET.SubElement(
        root,
        f"{{{GRAPHML_NS}}}graph",
        edgedefault="undirected",
        id="coauthorship",
    )

    todos_autores = set(autores) | set(artigos_por_autor)
    for author_id in sorted(todos_autores):
        metadados = autores.get(author_id, {})
        node = ET.SubElement(graph, f"{{{GRAPHML_NS}}}node", id=author_id)
        subelemento_data(node, "author_id", metadados.get("author_id", author_id))
        subelemento_data(node, "author_name", metadados.get("nome", ""))
        subelemento_data(node, "university", metadados.get("universidade", ""))
        subelemento_data(node, "city", metadados.get("cidade", ""))
        subelemento_data(node, "author_primary_macroarea", metadados.get("macro_area_principal_no_recorte", ""))
        subelemento_data(node, "author_macroareas", metadados.get("macro_areas_no_recorte", ""))
        subelemento_data(node, "author_topics", metadados.get("temas_no_recorte", ""))
        subelemento_data(node, "article_count", artigos_por_autor.get(author_id, 0))

    for indice, ((origem, destino), peso) in enumerate(sorted(arestas.items()), start=1):
        edge = ET.SubElement(
            graph,
            f"{{{GRAPHML_NS}}}edge",
            id=f"e{indice}",
            source=origem,
            target=destino,
        )
        subelemento_data(edge, "weight", peso)

    return ET.ElementTree(root)


def main():
    autores = carregar_autores_base(AUTHORS_CSV)
    autores = carregar_autores_tematicos(AUTHOR_THEMATIC_CSV, autores)
    artigos, artigos_por_autor = carregar_artigos()
    arestas = construir_arestas(artigos)

    graphml = montar_graphml(autores, artigos_por_autor, arestas)
    graphml.write(OUTPUT_GRAPHML, encoding="utf-8", xml_declaration=True)

    autores_tematicos = sum(
        1 for autor in autores.values() if autor.get("macro_area_principal_no_recorte") or autor.get("temas_no_recorte")
    )
    print(f"Arquivo base de autores usado: {AUTHORS_CSV}")
    print(f"Arquivo tematico de autores usado: {AUTHOR_THEMATIC_CSV}")
    print(f"Autores com atributos tematicos no grafo: {autores_tematicos}")
    print(f"Artigos processados: {len(artigos)}")
    print(f"Autores no grafo: {len(set(autores) | set(artigos_por_autor))}")
    print(f"Arestas no grafo: {len(arestas)}")
    print(f"GraphML salvo em: {OUTPUT_GRAPHML}")


if __name__ == "__main__":
    main()
