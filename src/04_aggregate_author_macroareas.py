import csv
from collections import Counter, defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
AUTHORS_CSV = PROJECT_ROOT / "data" / "raw" / "authors.csv"
ARTICLES_CSV = PROJECT_ROOT / "data" / "raw" / "articles.csv"
ARTICLE_MACROAREAS_CSV = PROJECT_ROOT / "data" / "interim" / "article_macroareas_output" / "articles_research_macroareas.csv"
OUTPUT_DIR = PROJECT_ROOT / "data" / "interim" / "author_macroareas_output"
OUTPUT_CSV = OUTPUT_DIR / "author_macroareas_from_articles.csv"


def split_pipe_list(text):
    return [item.strip() for item in text.split("|") if item.strip()]


def carregar_autores():
    autores = {}
    with AUTHORS_CSV.open("r", newline="", encoding="utf-8") as arquivo:
        reader = csv.DictReader(arquivo)
        for row in reader:
            author_id = row.get("author_id", "")
            if not author_id:
                continue
            autores[author_id] = {
                "author_id": author_id,
                "nome": row.get("nome", ""),
                "universidade": row.get("universidade", ""),
                "cidade": row.get("cidade", ""),
            }
    return autores


def carregar_artigos_por_autor():
    artigos_por_autor = defaultdict(set)
    with ARTICLES_CSV.open("r", newline="", encoding="utf-8") as arquivo:
        reader = csv.DictReader(arquivo)
        for row in reader:
            eid = row.get("eid", "")
            author_id = row.get("author_id", "")
            if eid and author_id:
                artigos_por_autor[author_id].add(eid)
    return artigos_por_autor


def carregar_macroareas_por_artigo():
    macroareas_por_artigo = {}
    with ARTICLE_MACROAREAS_CSV.open("r", newline="", encoding="utf-8") as arquivo:
        reader = csv.DictReader(arquivo)
        for row in reader:
            eid = row.get("eid", "")
            if not eid:
                continue
            macroareas_por_artigo[eid] = {
                "macro_area_principal": row.get("macro_area_principal", ""),
                "macro_areas": split_pipe_list(row.get("macro_areas", "")),
                "macroarea_scores": row.get("macroarea_scores", ""),
                "temas_pesquisa": split_pipe_list(row.get("temas_pesquisa", "")),
            }
    return macroareas_por_artigo


def formatar_contagens(counter):
    return " | ".join(f"{item}:{count}" for item, count in counter.most_common())


def parse_macroarea_scores(scores_text):
    counter = Counter()
    if not scores_text.strip():
        return counter

    for item in scores_text.split(";"):
        item = item.strip()
        if not item or ":" not in item:
            continue
        macroarea, count = item.rsplit(":", 1)
        macroarea = macroarea.strip()
        try:
            counter[macroarea] += int(count.strip())
        except ValueError:
            continue

    return counter


def escolher_macroarea_principal(article_counter, theme_counter):
    if not article_counter:
        return ""

    maior_contagem_artigo = max(article_counter.values())
    candidatas = [area for area, count in article_counter.items() if count == maior_contagem_artigo]

    if len(candidatas) == 1:
        return candidatas[0]

    if theme_counter:
        maior_contagem_tema = max(theme_counter[area] for area in candidatas)
        candidatas = [area for area in candidatas if theme_counter[area] == maior_contagem_tema]

    if len(candidatas) == 1:
        return candidatas[0]

    if "Engineering" in candidatas and len(candidatas) > 1:
        candidatas_sem_engineering = [area for area in candidatas if area != "Engineering"]
        if len(candidatas_sem_engineering) == 1:
            return candidatas_sem_engineering[0]
        if candidatas_sem_engineering:
            candidatas = candidatas_sem_engineering

    return f"Tie: {' | '.join(sorted(candidatas))}"


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    autores = carregar_autores()
    artigos_por_autor = carregar_artigos_por_autor()
    macroareas_por_artigo = carregar_macroareas_por_artigo()
    macroareas_principais_counter = Counter()
    empates = 0
    sem_macroarea = 0
    autores_com_macroareas = 0
    distribuicao_artigos_com_macroareas = Counter()

    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as arquivo:
        fieldnames = [
            "author_id",
            "nome",
            "universidade",
            "cidade",
            "total_artigos_no_recorte",
            "total_artigos_com_macroareas",
            "macro_area_principal_no_recorte",
            "macro_areas_no_recorte",
            "num_macro_areas_no_recorte",
            "macroarea_scores_no_recorte",
            "macroarea_scores_por_tema_no_recorte",
            "temas_no_recorte",
            "total_temas_distintos_no_recorte",
            "temas_no_recorte_com_contagem",
        ]
        writer = csv.DictWriter(arquivo, fieldnames=fieldnames)
        writer.writeheader()

        for author_id in sorted(autores):
            metadados = autores[author_id]
            eids = artigos_por_autor.get(author_id, set())

            macroareas_counter = Counter()
            macroareas_por_tema_counter = Counter()
            temas_counter = Counter()
            artigos_com_macroareas = 0

            for eid in eids:
                info = macroareas_por_artigo.get(eid)
                if not info:
                    continue

                if info["macro_areas"]:
                    artigos_com_macroareas += 1

                for macroarea in info["macro_areas"]:
                    macroareas_counter[macroarea] += 1

                macroareas_por_tema_counter.update(parse_macroarea_scores(info.get("macroarea_scores", "")))

                for tema in info["temas_pesquisa"]:
                    temas_counter[tema] += 1

            macroareas_ordenadas = [item for item, _ in macroareas_counter.most_common()]
            macroarea_principal = escolher_macroarea_principal(
                macroareas_counter,
                macroareas_por_tema_counter,
            )
            temas_ordenados = [item for item, _ in temas_counter.most_common()]

            if not macroarea_principal:
                sem_macroarea += 1
            else:
                autores_com_macroareas += 1
                if macroarea_principal.startswith("Tie:"):
                    empates += 1
                else:
                    macroareas_principais_counter[macroarea_principal] += 1

            distribuicao_artigos_com_macroareas[artigos_com_macroareas] += 1

            writer.writerow(
                {
                    **metadados,
                    "total_artigos_no_recorte": len(eids),
                    "total_artigos_com_macroareas": artigos_com_macroareas,
                    "macro_area_principal_no_recorte": macroarea_principal,
                    "macro_areas_no_recorte": " | ".join(macroareas_ordenadas),
                    "num_macro_areas_no_recorte": len(macroareas_counter),
                    "macroarea_scores_no_recorte": formatar_contagens(macroareas_counter),
                    "macroarea_scores_por_tema_no_recorte": formatar_contagens(macroareas_por_tema_counter),
                    "temas_no_recorte": " | ".join(temas_ordenados),
                    "total_temas_distintos_no_recorte": len(temas_counter),
                    "temas_no_recorte_com_contagem": formatar_contagens(temas_counter),
                }
            )

    print(f"Arquivo gerado: {OUTPUT_CSV}")
    print(f"Autores processados: {len(autores)}")
    print(f"Autores com macroareas no recorte: {autores_com_macroareas}")
    print(f"Autores sem macroarea no recorte: {sem_macroarea}")
    print(f"Autores com empate na macroarea principal: {empates}")
    print("Macroareas principais mais frequentes:")
    for macroarea, count in macroareas_principais_counter.most_common(20):
        print(f"- {macroarea}: {count}")
    print("Distribuicao de artigos com macroareas por autor:")
    for quantidade, count in distribuicao_artigos_com_macroareas.most_common(10):
        print(f"- {quantidade} artigos com macroareas: {count} autores")


if __name__ == "__main__":
    main()
