import csv
from collections import Counter
from pathlib import Path

from classify_research_macroareas import classificar_autor


INPUT_CSV = Path("checkpoints/article_topics_progress.csv")
OUTPUT_DIR = Path("article_macroareas_output")
OUTPUT_CSV = OUTPUT_DIR / "articles_research_macroareas.csv"
UNCLASSIFIED_TERMS_CSV = OUTPUT_DIR / "unclassified_article_terms.csv"


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    unclassified_counter = Counter()

    with INPUT_CSV.open("r", newline="", encoding="utf-8") as entrada, OUTPUT_CSV.open(
        "w", newline="", encoding="utf-8"
    ) as saida:
        reader = csv.DictReader(entrada)
        fieldnames = [
            "eid",
            "titulo",
            "ano",
            "source",
            "macro_area_principal",
            "macro_areas",
            "num_macro_areas",
            "total_areas_scopus",
            "macroarea_scores",
            "temas_pesquisa",
        ]
        writer = csv.DictWriter(saida, fieldnames=fieldnames)
        writer.writeheader()

        total = 0
        classificados = 0
        principais = Counter()

        for row in reader:
            total += 1
            classificacao = classificar_autor(row.get("temas_pesquisa", ""))

            for term in classificacao.pop("unclassified_terms", []):
                unclassified_counter[term.lower()] += 1

            if classificacao["macro_area_principal"]:
                classificados += 1
                principais[classificacao["macro_area_principal"]] += 1

            writer.writerow(
                {
                    "eid": row.get("eid", ""),
                    "titulo": row.get("titulo", ""),
                    "ano": row.get("ano", ""),
                    "source": row.get("source", ""),
                    **classificacao,
                    "temas_pesquisa": row.get("temas_pesquisa", ""),
                }
            )

    with UNCLASSIFIED_TERMS_CSV.open("w", newline="", encoding="utf-8") as arquivo:
        writer = csv.writer(arquivo)
        writer.writerow(["termo_scopus", "frequencia"])
        for term, count in unclassified_counter.most_common():
            writer.writerow([term, count])

    print(f"Artigos lidos: {total}")
    print(f"Artigos classificados: {classificados}")
    print(f"Arquivo gerado: {OUTPUT_CSV}")
    print(f"Termos nao classificados salvos em: {UNCLASSIFIED_TERMS_CSV}")
    print("Macroareas principais mais frequentes:")
    for macroarea, count in principais.most_common(20):
        print(f"- {macroarea}: {count}")


if __name__ == "__main__":
    main()
