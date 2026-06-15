import csv
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_CSV = PROJECT_ROOT / "data" / "interim" / "article_topics.csv"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "tables" / "auxiliary"
OUTPUT_CSV = OUTPUT_DIR / "real_authors_research_macroareas.csv"
UNCLASSIFIED_TERMS_CSV = OUTPUT_DIR / "unclassified_research_terms.csv"

MACROAREA_RULES = [
    ("Computer Science", [
        "computer science applications", "computer networks and communications", "software", "artificial intelligence",
        "computer science (all)", "information systems", "computational theory and mathematics", "hardware and architecture",
        "theoretical computer science", "computer graphics and computer-aided design", "computer science (miscellaneous)",
        "human-computer interaction", "computers in earth sciences", "computational mathematics", "computer vision and pattern recognition", "health informatics",
        "signal processing", "health information management", "modeling and simulation", "information systems and management",
        "management information systems", "Computer Science"

    ]),

    ("Mathematics and Statistics", [
        "applied mathematics", "geometry and topology", "computational theory and mathematics", "numerical analysis", "mathematics (all)",
        "statistics and probability", "mathematical physics", "algebra and number theory", "statistics, probability and uncertainty",
        "discrete mathematics and combinatorics", "mathematics (miscellaneous)", "Mathematics and Statistics", 

    ]),

    ("Physics", [
        "biophysics", "physics and astronomy (all)", "condensed matter physics", "mathematical physics", "statistical and nonlinear physics",
        "nuclear and high energy physics", "physics and astronomy (miscellaneous)", "astronomy and astrophysics", 
        "atomic and molecular physics, and optics", "radiation", "space and planetary science", "nuclear energy and engineering",
        "acoustics and ultrasonics", "spectroscopy", "electronic, optical and magnetic materials",

    ]),

    ("Chemistry", [
        "materials chemistry", "chemistry (all)", "biochemistry", "chemistry (miscellaneous)", "analytical chemistry",
        "physical and theoretical chemistry", "chemical engineering (all)", "chemical engineering (miscellaneous)", "inorganic chemistry",
        "organic chemistry", "electrochemistry", "surfaces and interfaces", "process chemistry and technology",
        "environmental chemistry", "food science", "fuel technology", "colloid and surface chemistry", "drug discovery",
        "catalysis", "spectroscopy", "filtration and separation",

    ]),

    ("Engineering", [
        "mechanical engineering", "chemical engineering (all)", "engineering (all)", "control and systems engineering",
        "materials science (all)", "biomaterials", "metals and alloys", "process chemistry and technology",
        "automotive engineering", "electrical and electronic engineering", "mechanics of materials", "polymers and plastics",
        "energy engineering and power technology", "industrial and manufacturing engineering", "bioengineering", "biomedical engineering",
        "chemical engineering (miscellaneous)", "food science", "instrumentation", "civil and structural engineering", "environmental engineering",
        "ocean engineering", "computational mechanics", "aerospace engineering", "geotechnical engineering and engineering geology", 
        "engineering (miscellaneous)", "renewable energy, sustainability and the environment", "electronic, optical and magnetic materials",
        "fuel technology", "building and construction", "materials science (miscellaneous)", "nuclear energy and engineering",
        "safety, risk, reliability and quality", "surfaces, coatings and films", "signal processing", "fluid flow and transfer processes",
        "ceramics and composites", "transportation", "filtration and separation", 

        
    ]),

    ("Medicine and Health", [
        "medicine (all)", "urology", "neurology (clinical)", "infectious diseases", "orthopedics and sports medicine",
        "orthopedics and sports medicine", "dentistry (all)", "oral surgery", "endocrinology, diabetes and metabolism",
        "pharmaceutical science", "neuroscience (all)", "oncology", "cancer research", "ophthalmology", 
        "immunology", "gastroenterology", "endocrinology", "veterinary (all)", "internal medicine", "health professions (all)", 
        "pulmonary and respiratory medicine", "anatomy", "neuroscience (miscellaneous)", "veterinary (miscellaneous)",
        "complementary and alternative medicine", "pharmacy", "chiropractics", "surgery", "obstetrics and gynecology", 
        "biomedical engineering", "medicine (miscellaneous)", "health, toxicology and mutagenesis", "nephrology", "molecular medicine",
        "rheumatology", "pharmacology, toxicology and pharmaceutics (miscellaneous)", "medical and surgical nursing", "pharmacology",
        "hepatology", "otorhinolaryngology", "critical care and intensive care medicine", "gerontology", "radiology, nuclear medicine and imaging",
        "physical therapy, sports therapy and rehabilitation", "public health, environmental and occupational health",
        "physiology (medical)", "pathology and forensic medicine", "hematology", "dermatology", "nutrition and dietetics", "psychiatry and mental health",
        "health informatics", "reproductive medicine", "dentistry (miscellaneous)", "histology", "complementary and manual therapy", "social psychology",
        "medical laboratory technology", "applied psychology", "clinical psychology", "psychology (miscellaneous)", "health policy", 
        "psychology (all)", "neuropsychology and physiological psychology", "cardiology and cardiovascular medicine", "dental hygiene",
        "biological psychiatry", "experimental and cognitive psychology", "transplantation", "podiatry", "toxicology", "epidemiology",
        "rehabilitation", "emergency medicine", "dental assisting", "psychiatric mental health", "pediatrics, perinatology and child health",
        "advanced and specialized nursing", "nursing (all)", "nursing (miscellaneous)", "anesthesiology and pain medicine", "orthodontics",
        "cognitive neuroscience", "periodontics", "speech and hearing", "behavioral neuroscience", "aging", "sensory systems", "health information management",
        "occupational therapy", "maternity and midwifery", "family practice", "lpn and lvn", "community and home care",
        "pharmacology (medical)", "geriatrics and gerontology", "pharmacology, toxicology and pharmaceutics (all)", "neurology",
        "immunology and allergy", "microbiology (medical)", "radiological and ultrasound technology", "clinical biochemistry",
        "genetics (clinical)", "biochemistry (medical)",


    ]),

    ("Biology", [
        "biophysics", "biotechnology", "microbiology", "plant science", "biochemistry", "genetics",
        "agricultural and biological sciences (all)", "biomaterials", "insect science", "cell biology",
        "molecular biology", "molecular biology", "bioengineering", "animal science and zoology", "biomedical engineering", "food science",
        "ecology", "forestry", "molecular medicine", "paleontology", "agricultural and biological sciences (miscellaneous)",
        "structural biology", "cellular and molecular neuroscience", "health professions (miscellaneous)", "virology", "food animals",
        "agronomy and crop science", "physiology", "parasitology", "soil science", "horticulture", "embryology", "cognitive neuroscience", 
        "behavioral neuroscience", "biochemistry, genetics and molecular biology (all)", "ecology, evolution, behavior and systematics",
        "biochemistry, genetics and molecular biology (miscellaneous)", "applied microbiology and biotechnology", "developmental biology",
        "immunology and microbiology (all)", "immunology and microbiology (miscellaneous)", "infectious diseases",

    ]),

    ("Geosciences", [
        "earth-surface processes", "geochemistry and petrology", "environmental science (all)", "computers in earth sciences",
        "earth and planetary sciences (all)", "forestry", "environmental engineering", "ocean engineering", "environmental science (miscellaneous)",
        "geology", "geotechnical engineering and engineering geology", "renewable energy, sustainability and the environment", 
        "geography, planning and development", "pollution", "geophysics", "oceanography", "paleontology", "aquatic science",
        "earth and planetary sciences (miscellaneous)", "global and planetary change", "atmospheric science", "soil science",
        "water science and technology", "waste management and disposal", "nature and landscape conservation", "stratigraphy", 

    ]),

    ("Social Sciences", [
        "social sciences", "health (social science)", "education", "sociology and political science",
        "religious studies", "anthropology", "demography", "public administration", "law",
        "gender studies", "social psychology", "health policy", "social sciences (all)",
        "political science and international relations", "urban studies", "communication",
        "issues, ethics and legal aspects", "tourism, leisure and hospitality management",
        "organizational behavior and human resource management", "life-span and life-course studies",
        "management, monitoring, policy and law", "social sciences (miscellaneous)", 
    ]),

    ("Economics and Business", [
        "economics and econometrics", "economics, econometrics and finance (all)",
        "economics, econometrics and finance (miscellaneous)",
        "business, management and accounting (all)", "business, management and accounting (miscellaneous)",
        "industrial relations", "strategy and management", "marketing", "finance",
        "management of technology and innovation", "business and international management",
        "tourism, leisure and hospitality management", "organizational behavior and human resource management",
        "accounting", "leadership and management", "management science and operations research",
    ]),

    ("Arts", [
        "visual arts and performing arts", "arts and humanities (miscellaneous)", "arts and humanities (all)", "music", "museology", "architecture",

    ]),

    ("Philosophy and Humanities", [
        "history and philosophy of science", "history", "philosophy", "arts and humanities (miscellaneous)", "arts and humanities (all)", "language and linguistics",
        "literature and literary theory", "archeology (arts and humanities)", "archeology", "classics", "linguistics and language", "cultural studies", "logic",

    ]),

    ("Undefined", [
        "library and information sciences", "management science and operations research", "safety research", "multidisciplinary", 
        "energy (all)", "energy (miscellaneous)", "decision sciences (all)", "decision sciences (miscellaneous)", "research and theory",
        "library and information sciences", "conservation"
    ])

]


def split_areas(areas_pesquisa):
    return [area.strip() for area in areas_pesquisa.split("|") if area.strip()]


def normalizar_termo(texto):
    return " ".join(texto.lower().split()).strip()


def classificar_area(area):
    area_normalizada = normalizar_termo(area)
    macroareas = []

    for macroarea, keywords in MACROAREA_RULES:
        if any(normalizar_termo(keyword) == area_normalizada for keyword in keywords):
            macroareas.append(macroarea)

    return macroareas or ["Other/Unclassified"]


def classificar_autor(areas_pesquisa):
    areas = split_areas(areas_pesquisa)
    counter = Counter()
    unclassified_terms = []

    for area in areas:
        macroareas = classificar_area(area)
        if macroareas == ["Other/Unclassified"]:
            unclassified_terms.append(area)
        for macroarea in macroareas:
            counter[macroarea] += 1

    if not counter:
        return {
            "macro_area_principal": "",
            "macro_areas": "",
            "num_macro_areas": 0,
            "total_areas_scopus": 0,
            "macroarea_scores": "",
            "unclassified_terms": [],
        }

    macro_areas = [macroarea for macroarea, _ in counter.most_common()]
    macro_area_principal = macro_areas[0]
    macroarea_scores = "; ".join(f"{macroarea}:{count}" for macroarea, count in counter.most_common())

    return {
        "macro_area_principal": macro_area_principal,
        "macro_areas": " | ".join(macro_areas),
        "num_macro_areas": len(macro_areas),
        "total_areas_scopus": len(areas),
        "macroarea_scores": macroarea_scores,
        "unclassified_terms": unclassified_terms,
    }


def main():
    unclassified_counter = Counter()

    with INPUT_CSV.open("r", newline="", encoding="utf-8") as entrada, OUTPUT_CSV.open(
        "w", newline="", encoding="utf-8"
    ) as saida:
        reader = csv.DictReader(entrada)
        fieldnames = [
            "author_id",
            "nome",
            "universidade",
            "cidade",
            "macro_area_principal",
            "macro_areas",
            "num_macro_areas",
            "total_areas_scopus",
            "macroarea_scores",
            "areas_pesquisa",
        ]
        writer = csv.DictWriter(saida, fieldnames=fieldnames)
        writer.writeheader()

        total = 0
        classificados = 0
        principais = Counter()

        for row in reader:
            total += 1
            classificacao = classificar_autor(row.get("areas_pesquisa", ""))
            for term in classificacao.pop("unclassified_terms"):
                unclassified_counter[term] += 1

            if classificacao["macro_area_principal"]:
                classificados += 1
                principais[classificacao["macro_area_principal"]] += 1

            writer.writerow(
                {
                    "author_id": row.get("author_id", ""),
                    "nome": row.get("nome", ""),
                    "universidade": row.get("universidade", ""),
                    "cidade": row.get("cidade", ""),
                    **classificacao,
                    "areas_pesquisa": row.get("areas_pesquisa", ""),
                }
            )

    with UNCLASSIFIED_TERMS_CSV.open("w", newline="", encoding="utf-8") as arquivo:
        writer = csv.writer(arquivo)
        writer.writerow(["termo_scopus", "frequencia"])
        for term, count in unclassified_counter.most_common():
            writer.writerow([term, count])

    print(f"Autores lidos: {total}")
    print(f"Autores classificados: {classificados}")
    print(f"Arquivo gerado: {OUTPUT_CSV}")
    print(f"Termos nao classificados salvos em: {UNCLASSIFIED_TERMS_CSV}")
    print("Macroareas principais mais frequentes:")
    for macroarea, count in principais.most_common(20):
        print(f"- {macroarea}: {count}")


if __name__ == "__main__":
    main()
