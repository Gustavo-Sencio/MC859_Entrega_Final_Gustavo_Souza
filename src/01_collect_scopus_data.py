import csv
import time

import requests

API_KEY = "KEY"
URL = "https://api.elsevier.com/content/search/scopus"

HEADERS = {
    "X-ELS-APIKey": API_KEY,
    "Accept": "application/json",
}

# AF-ID da UNICAMP + institutos
AFIDS = "(AF-ID (60029570) OR AF-ID (60242502) OR AF-ID (60340244) OR AF-ID (60340366))"

POR_PAGINA = 25
ANOS = range(2021, 2026)  # 2021 -> 2025
MAX_AUTORES_ARTIGO = 5
PAUSA_ENTRE_REQUISICOES = 0.4
MAX_RETRIES = 3

autores_dict = {}


def normalizar_afid(valor):
    if not valor:
        return []

    if isinstance(valor, str):
        return [valor]

    if isinstance(valor, list):
        resultado = []
        for v in valor:
            if isinstance(v, str):
                resultado.append(v)
            elif isinstance(v, dict) and "$" in v:
                resultado.append(v["$"])
        return resultado

    if isinstance(valor, dict) and "$" in valor:
        return [valor["$"]]

    return []


def normalizar_lista_autores(autores):
    if not autores:
        return []
    if isinstance(autores, list):
        return autores
    if isinstance(autores, dict):
        return [autores]
    return []


def fazer_requisicao(params):
    for tentativa in range(1, MAX_RETRIES + 1):
        try:
            resposta = requests.get(URL, headers=HEADERS, params=params, timeout=60)
            resposta.raise_for_status()
            return resposta.json()
        except requests.RequestException as erro:
            if tentativa == MAX_RETRIES:
                raise RuntimeError(f"Falha na requisicao da Scopus: {erro}") from erro

            espera = tentativa * 2
            print(
                f"Erro na requisicao ({tentativa}/{MAX_RETRIES}): {erro}. "
                f"Tentando novamente em {espera}s..."
            )
            time.sleep(espera)


def extrair_total_resultados(data):
    bruto = data.get("search-results", {}).get("opensearch:totalResults", "0")
    try:
        return int(bruto)
    except (TypeError, ValueError):
        return 0


def extrair_proximo_cursor(data):
    cursor = data.get("search-results", {}).get("cursor")
    if isinstance(cursor, dict):
        return cursor.get("@next")
    return None


def iterar_artigos(query):
    cursor = "*"
    pagina = 1
    total_esperado = None
    total_recebido = 0

    while cursor:
        params = {
            "query": query,
            "count": POR_PAGINA,
            "cursor": cursor,
            "view": "COMPLETE",
        }

        data = fazer_requisicao(params)
        if total_esperado is None:
            total_esperado = extrair_total_resultados(data)
            print(f"Total encontrado para a consulta: {total_esperado}")

        artigos = data.get("search-results", {}).get("entry", [])
        if not artigos:
            break

        print(
            f"Pagina {pagina}: {len(artigos)} artigos "
            f"(acumulado {min(total_recebido + len(artigos), total_esperado)}/{total_esperado})"
        )

        yield from artigos

        total_recebido += len(artigos)
        cursor = extrair_proximo_cursor(data)
        pagina += 1

        if total_recebido >= total_esperado:
            break

        time.sleep(PAUSA_ENTRE_REQUISICOES)


print("Abrindo arquivo de artigos...")

articles_file = open("articles.csv", "w", newline="", encoding="utf-8")
articles_writer = csv.writer(articles_file)
articles_writer.writerow(["eid", "titulo", "ano", "source", "author_id"])

artigos_descartados_por_autores = 0
artigos_processados = 0

for ano in ANOS:
    query_ano = f"{AFIDS} AND PUBYEAR = {ano}"
    print("\n==============================")
    print(f"Coletando ano {ano}")
    print("==============================")

    for paper in iterar_artigos(query_ano):
        autores = normalizar_lista_autores(paper.get("author"))
        if len(autores) > MAX_AUTORES_ARTIGO:
            artigos_descartados_por_autores += 1
            continue

        eid = paper.get("eid")
        titulo = paper.get("dc:title", "")
        ano_paper = paper.get("prism:coverDate", "")[:4]
        source = paper.get("prism:publicationName", "")
        afiliacoes = paper.get("affiliation", [])

        mapa_afiliacoes = {}
        for aff in afiliacoes:
            nome_uni = aff.get("affilname", "")
            cidade = aff.get("affiliation-city", "")
            afids = normalizar_afid(aff.get("afid"))

            for afid in afids:
                mapa_afiliacoes[afid] = (nome_uni, cidade)

        for autor in autores:
            author_id = autor.get("authid")
            nome = autor.get("authname")
            lista_afids = normalizar_afid(autor.get("afid"))

            universidade = ""
            cidade = ""

            for afid in lista_afids:
                if afid in mapa_afiliacoes:
                    universidade, cidade = mapa_afiliacoes[afid]
                    break

            if author_id and author_id not in autores_dict:
                autores_dict[author_id] = [author_id, nome, universidade, cidade]

            if author_id:
                articles_writer.writerow([eid, titulo, ano_paper, source, author_id])

        artigos_processados += 1

articles_file.close()

print("\nSalvando tabela de autores...")

with open("authors.csv", "w", newline="", encoding="utf-8") as arquivo_autores:
    writer = csv.writer(arquivo_autores)
    writer.writerow(["author_id", "nome", "universidade", "cidade"])
    writer.writerows(autores_dict.values())

print(f"Artigos aceitos: {artigos_processados}")
print(f"Artigos descartados por terem mais de {MAX_AUTORES_ARTIGO} autores: {artigos_descartados_por_autores}")
print("Finalizado com sucesso!")
