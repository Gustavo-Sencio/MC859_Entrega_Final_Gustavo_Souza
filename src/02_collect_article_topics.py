import csv
import time
from pathlib import Path

import requests

API_KEY = "KEY"
URL_ABSTRACT = "https://api.elsevier.com/content/abstract/eid/"

HEADERS = {
    "X-ELS-APIKey": API_KEY,
    "Accept": "application/json",
}

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_CSV = PROJECT_ROOT / "data" / "raw" / "articles.csv"
INTERIM_DIR = PROJECT_ROOT / "data" / "interim"
OUTPUT_CSV = INTERIM_DIR / "article_topics.csv"
CHECKPOINT_DIR = INTERIM_DIR / "checkpoints"
PROGRESS_CSV = CHECKPOINT_DIR / "article_topics_progress.csv"

PAUSA_ENTRE_REQUISICOES = 0.5
MAX_RETRIES = 3

CAMPOS_SAIDA = [
    "eid",
    "titulo",
    "ano",
    "source",
    "temas_pesquisa",
]


def carregar_artigos_base():
    artigos = {}
    with INPUT_CSV.open("r", newline="", encoding="utf-8") as arquivo:
        reader = csv.DictReader(arquivo)
        for row in reader:
            eid = row.get("eid", "")
            if not eid or eid in artigos:
                continue

            artigos[eid] = {
                "eid": eid,
                "titulo": row.get("titulo", ""),
                "ano": row.get("ano", ""),
                "source": row.get("source", ""),
                "temas_pesquisa": "",
            }
    return artigos


def preparar_arquivo_progresso():
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    if PROGRESS_CSV.exists():
        return

    with PROGRESS_CSV.open("w", newline="", encoding="utf-8") as arquivo:
        writer = csv.DictWriter(arquivo, fieldnames=CAMPOS_SAIDA)
        writer.writeheader()


def carregar_progresso(artigos):
    processados = set()
    if not PROGRESS_CSV.exists():
        return processados

    with PROGRESS_CSV.open("r", newline="", encoding="utf-8") as arquivo:
        reader = csv.DictReader(arquivo)
        for row in reader:
            eid = row.get("eid")
            if not eid or eid not in artigos:
                continue

            artigos[eid].update(
                {
                    "temas_pesquisa": row.get("temas_pesquisa", ""),
                }
            )
            processados.add(eid)

    return processados


def fazer_requisicao(eid):
    params = {"view": "FULL"}

    for tentativa in range(1, MAX_RETRIES + 1):
        resposta = requests.get(
            URL_ABSTRACT + eid,
            headers=HEADERS,
            params=params,
            timeout=60,
        )

        if resposta.status_code == 429:
            reset = resposta.headers.get("X-RateLimit-Reset")
            mensagem = f"Quota atingida ao buscar {eid}."
            if reset:
                mensagem += f" X-RateLimit-Reset={reset}"
            raise RuntimeError(mensagem)

        try:
            resposta.raise_for_status()
            return resposta.json()
        except requests.RequestException as erro:
            if tentativa == MAX_RETRIES:
                print(f"Falha definitiva para {eid}: {erro}")
                return None

            espera = tentativa * 2
            print(
                f"Erro ao buscar {eid} ({tentativa}/{MAX_RETRIES}): {erro}. "
                f"Tentando novamente em {espera}s..."
            )
            time.sleep(espera)

    return None


def normalizar_lista(valor):
    if not valor:
        return []
    if isinstance(valor, list):
        return valor
    return [valor]


def primeiro_valor_textual(valor):
    if isinstance(valor, dict):
        if "$" in valor and valor["$"]:
            return str(valor["$"]).strip()
        for item in valor.values():
            texto = primeiro_valor_textual(item)
            if texto:
                return texto
    elif isinstance(valor, list):
        for item in valor:
            texto = primeiro_valor_textual(item)
            if texto:
                return texto
    elif isinstance(valor, str):
        return valor.strip()
    return ""


def coletar_valores_por_chave(objeto, chave):
    valores = []

    if isinstance(objeto, dict):
        for key, value in objeto.items():
            if key == chave:
                valores.extend(normalizar_lista(value))
            else:
                valores.extend(coletar_valores_por_chave(value, chave))
    elif isinstance(objeto, list):
        for item in objeto:
            valores.extend(coletar_valores_por_chave(item, chave))

    return valores


def extrair_areas_artigo(data):
    if not data:
        return ""

    areas = []
    for item in coletar_valores_por_chave(data, "subject-area"):
        nome = primeiro_valor_textual(item)
        if nome and nome not in areas:
            areas.append(nome)

    return " | ".join(areas)


def enriquecer_artigo(eid, artigo):
    data = fazer_requisicao(eid)
    artigo["temas_pesquisa"] = extrair_areas_artigo(data)
    return artigo


def anexar_progresso(artigo):
    with PROGRESS_CSV.open("a", newline="", encoding="utf-8") as arquivo:
        writer = csv.DictWriter(arquivo, fieldnames=CAMPOS_SAIDA)
        writer.writerow({campo: artigo.get(campo, "") for campo in CAMPOS_SAIDA})


def salvar_saida_final(artigos):
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as arquivo:
        writer = csv.DictWriter(arquivo, fieldnames=CAMPOS_SAIDA)
        writer.writeheader()
        for artigo in artigos.values():
            writer.writerow({campo: artigo.get(campo, "") for campo in CAMPOS_SAIDA})


def main():
    artigos = carregar_artigos_base()
    preparar_arquivo_progresso()
    processados = carregar_progresso(artigos)

    print(f"Total de artigos unicos: {len(artigos)}")
    print(f"Artigos ja processados no checkpoint: {len(processados)}")
    print("Buscando temas/areas dos artigos...")

    for indice, (eid, artigo) in enumerate(artigos.items(), start=1):
        if eid in processados:
            continue

        print(f"{indice}/{len(artigos)} -> {eid}")
        artigo_enriquecido = enriquecer_artigo(eid, artigo)
        artigos[eid] = artigo_enriquecido
        anexar_progresso(artigo_enriquecido)
        processados.add(eid)
        time.sleep(PAUSA_ENTRE_REQUISICOES)

    salvar_saida_final(artigos)
    print(f"Arquivo final salvo em {OUTPUT_CSV}")
    print(f"Checkpoint incremental salvo em {PROGRESS_CSV}")


if __name__ == "__main__":
    main()
