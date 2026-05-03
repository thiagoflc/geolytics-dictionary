#!/usr/bin/env python3
"""Generate data/anp-uf.json and data/anp-bacia-sedimentar.json from
Resolução ANP nº 699/2017 Anexos I and II.

Anexo I — 26 Unidades da Federação with 2-digit ANP codes (mostly even,
exception TOCANTINS = 95). Includes IBGE acronym lookup and a `marine_suffix`
field showing how the ambiente marítimo modifies the geographic reference
(e.g. RJ → RJS).

Anexo II — Sedimentary basins with 2- or 3-digit ANP codes. Many basins are
split into MAR (offshore) and TERRA (onshore) sub-codes (e.g. CAMPOS TERRA =
280, CAMPOS MAR = 281). The `ambiente` field is inferred from the suffix.

Idempotent — overwrites the target JSON each run.
Usage: python3 scripts/migrations/2026-05-03/build-anp-codelists.py [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TARGET_UF = ROOT / "data" / "anp-uf.json"
TARGET_BACIA = ROOT / "data" / "anp-bacia-sedimentar.json"

# ---------------------------------------------------------------------------
# ANEXO I — 26 UFs (Resolução ANP 699/2017)
# Tuples: (anp_code, name_pt, ibge_acronym, region)
# ---------------------------------------------------------------------------
UFS = [
    ("04", "Acre", "AC", "Norte"),
    ("08", "Alagoas", "AL", "Nordeste"),
    ("12", "Amapá", "AP", "Norte"),
    ("14", "Amazonas", "AM", "Norte"),
    ("20", "Bahia", "BA", "Nordeste"),
    ("24", "Distrito Federal", "DF", "Centro-Oeste"),
    ("30", "Ceará", "CE", "Nordeste"),
    ("34", "Espírito Santo", "ES", "Sudeste"),
    ("44", "Goiás", "GO", "Centro-Oeste"),
    ("50", "Maranhão", "MA", "Nordeste"),
    ("54", "Mato Grosso", "MT", "Centro-Oeste"),
    ("56", "Mato Grosso do Sul", "MS", "Centro-Oeste"),
    ("58", "Minas Gerais", "MG", "Sudeste"),
    ("60", "Pará", "PA", "Norte"),
    ("62", "Paraíba", "PB", "Nordeste"),
    ("64", "Paraná", "PR", "Sul"),
    ("66", "Pernambuco", "PE", "Nordeste"),
    ("68", "Piauí", "PI", "Nordeste"),
    ("70", "Rio Grande do Sul", "RS", "Sul"),
    ("72", "Rio Grande do Norte", "RN", "Nordeste"),
    ("74", "Rio de Janeiro", "RJ", "Sudeste"),
    ("76", "Rondônia", "RO", "Norte"),
    ("78", "Roraima", "RR", "Norte"),
    ("82", "Santa Catarina", "SC", "Sul"),
    ("86", "São Paulo", "SP", "Sudeste"),
    ("90", "Sergipe", "SE", "Nordeste"),
    ("95", "Tocantins", "TO", "Norte"),
]

# UFs with maritime continental shelf (offshore wells get sigla + 'S')
COASTAL = {"AL", "AP", "BA", "CE", "ES", "MA", "PA", "PB", "PE", "PR", "RJ", "RN", "RS", "SC", "SE", "SP"}

# ---------------------------------------------------------------------------
# ANEXO II — Sedimentary basins (Resolução ANP 699/2017)
# Tuples: (anp_code, name_pt)
# ---------------------------------------------------------------------------
BACIAS = [
    ("10", "Acre"),
    ("15", "Madre de Dios"),
    ("20", "Solimões"),
    ("30", "Amazonas"),
    ("35", "Alto Tapajós"),
    ("40", "Tacutu"),
    ("50", "Marajó"),
    ("51", "Foz do Amazonas"),
    ("55", "Amapá"),
    ("60", "Bragança-Vizeu"),
    ("66", "Rio do Peixe"),
    ("70", "São Luís"),
    ("76", "Pará-Maranhão"),
    ("80", "Barreirinhas Terra"),
    ("81", "Barreirinhas Mar"),
    ("90", "Parnaíba"),
    ("95", "Malhado Vermelho"),
    ("96", "Ceará"),
    ("100", "Potiguar Terra"),
    ("101", "Potiguar Mar"),
    ("105", "Pernambuco-Paraíba Terra"),
    ("106", "Pernambuco-Paraíba Mar"),
    ("110", "Iguatu"),
    ("115", "Alagoas Terra"),
    ("116", "Alagoas Mar"),
    ("120", "Sergipe Terra"),
    ("121", "Sergipe Mar"),
    ("125", "Lima Campos"),
    ("130", "Icó"),
    ("135", "Pombal"),
    ("140", "Souza"),
    ("145", "Triunfo (Serra dos Frades)"),
    ("150", "Araripe"),
    ("155", "Barro"),
    ("160", "Cedro"),
    ("165", "Serra do Inácio"),
    ("170", "São José do Belmonte"),
    ("175", "Bom Nome"),
    ("180", "Mirandiba"),
    ("185", "Tupanaci"),
    ("190", "Betânia"),
    ("195", "Afogados da Ingazeira"),
    ("200", "Irecê"),
    ("205", "Itaberaba"),
    ("210", "Jatobá"),
    ("215", "Tucano Norte"),
    ("220", "Tucano Central"),
    ("230", "Tucano Sul"),
    ("236", "Jacuípe"),
    ("240", "Recôncavo Terra"),
    ("241", "Recôncavo Mar"),
    ("245", "Camamu Terra"),
    ("246", "Camamu Mar"),
    ("250", "Jequitinhonha Terra"),
    ("251", "Jequitinhonha Mar"),
    ("255", "Cumuruxatiba Terra"),
    ("256", "Cumuruxatiba Mar"),
    ("260", "Mucuri Terra"),
    ("261", "Mucuri Mar"),
    ("265", "Almada Terra"),
    ("266", "Almada Mar"),
    ("270", "Espírito Santo Terra"),
    ("271", "Espírito Santo Mar"),
    ("275", "São Francisco"),
    ("280", "Campos Terra"),
    ("281", "Campos Mar"),
    ("285", "Itaboraí"),
    ("290", "Resende"),
    ("295", "Taubaté"),
    ("300", "Paraná"),
    ("305", "São Paulo"),
    ("310", "Curitiba"),
    ("315", "Pantanal"),
    ("316", "Santos"),
    ("320", "Parecis-Alto Xingu"),
    ("325", "Bananal"),
    ("330", "Água Bonita"),
    ("380", "Pelotas Terra"),
    ("381", "Pelotas Mar"),
]


def normalize_id(s: str) -> str:
    """Lowercase, strip accents-light, replace spaces and special chars with hyphens."""
    s = s.lower()
    replacements = {
        "á": "a", "à": "a", "â": "a", "ã": "a",
        "é": "e", "ê": "e",
        "í": "i", "î": "i",
        "ó": "o", "ô": "o", "õ": "o",
        "ú": "u", "ü": "u",
        "ç": "c",
        "(": "", ")": "",
    }
    for k, v in replacements.items():
        s = s.replace(k, v)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def build_uf_payload() -> dict:
    concepts = []
    for code, name, ibge, region in UFS:
        is_coastal = ibge in COASTAL
        concepts.append({
            "id": f"uf-{ibge.lower()}",
            "anp_code": code,
            "ibge_acronym": ibge,
            "label_pt": name,
            "label_en": name,
            "region": region,
            "is_coastal": is_coastal,
            "marine_suffix": f"{ibge}S" if is_coastal else None,
            "definition": (
                f"Unidade da Federação brasileira (sigla IBGE: {ibge}). "
                f"Código ANP {code} para composição do Cadastro do Poço (Anexo I, "
                f"Resolução ANP nº 699/2017). "
                + (f"Quando o poço se localiza no mar, acrescenta-se a letra 'S' à sigla ({ibge}S)."
                   if is_coastal else
                   "Sem litoral marítimo — não admite poços marítimos.")
            ),
            "uri": f"https://geolytics.com.br/ontology/anp/uf/{ibge.lower()}",
            "evidence_refs": ["ANP-699/2017 Anexo I", "IBGE — Códigos de UF"],
        })
    return {
        "meta": {
            "source": "Resolução ANP nº 699/2017 — Anexo I (Códigos das Unidades da Federação)",
            "source_url": "https://atosoficiais.com.br/anp/resolucao-n-699-2017",
            "namespace": "https://geolytics.com.br/ontology/anp/uf/",
            "version": "699/2017",
            "total": len(concepts),
            "description": (
                "Vocabulário controlado dos códigos numéricos ANP das 26 Unidades "
                "da Federação brasileiras (mais o Distrito Federal), conforme "
                "Anexo I da Resolução ANP nº 699/2017. Códigos compõem os 2 "
                "primeiros dígitos do Cadastro do Poço (11 dígitos). Inclui sigla "
                "IBGE e indicador de litoral (UFs com plataforma continental "
                "admitem poços marítimos com sufixo 'S')."
            ),
            "layer": "layer4",
            "related_entities": ["poco", "bacia-sedimentar"],
            "evidence_refs": ["ANP-699/2017"],
        },
        "concepts": concepts,
    }


def build_bacia_payload() -> dict:
    concepts = []
    for code, name in BACIAS:
        # Infer ambiente from name suffix
        ambiente = None
        if name.endswith(" Mar"):
            ambiente = "marítimo"
        elif name.endswith(" Terra"):
            ambiente = "terrestre"
        # else None (basins without TERRA/MAR distinction)

        # Identify paired terra/mar basins
        paired_with = None
        if ambiente == "marítimo":
            base = name[:-4]
            paired_name = f"{base} Terra"
            for c, n in BACIAS:
                if n == paired_name:
                    paired_with = f"bacia-{normalize_id(paired_name)}"
                    break
        elif ambiente == "terrestre":
            base = name[:-6]
            paired_name = f"{base} Mar"
            for c, n in BACIAS:
                if n == paired_name:
                    paired_with = f"bacia-{normalize_id(paired_name)}"
                    break

        concept = {
            "id": f"bacia-{normalize_id(name)}",
            "anp_code": code,
            "label_pt": name,
            "label_en": name,
            "ambiente": ambiente,
            "is_offshore": ambiente == "marítimo",
            "definition": (
                f"Bacia sedimentar brasileira '{name}', código ANP {code} "
                f"(Anexo II, Resolução ANP nº 699/2017). Compõe os 3 dígitos "
                f"intermediários do Cadastro do Poço."
                + (f" Compartilha trend geológico com sua contraparte "
                   f"{'terrestre' if ambiente == 'marítimo' else 'marítima'}."
                   if paired_with else "")
            ),
            "uri": f"https://geolytics.com.br/ontology/anp/bacia/{normalize_id(name)}",
            "evidence_refs": ["ANP-699/2017 Anexo II"],
        }
        if paired_with:
            concept["paired_basin_id"] = paired_with
        concepts.append(concept)

    return {
        "meta": {
            "source": "Resolução ANP nº 699/2017 — Anexo II (Códigos das Bacias Sedimentares)",
            "source_url": "https://atosoficiais.com.br/anp/resolucao-n-699-2017",
            "namespace": "https://geolytics.com.br/ontology/anp/bacia/",
            "version": "699/2017",
            "total": len(concepts),
            "description": (
                "Vocabulário controlado dos códigos numéricos ANP das bacias "
                "sedimentares brasileiras, conforme Anexo II da Resolução ANP nº "
                "699/2017. Códigos compõem os 3 dígitos intermediários do "
                "Cadastro do Poço (11 dígitos). Bacias da margem continental "
                "frequentemente aparecem em pares TERRA/MAR (ex.: 280 Campos "
                "Terra / 281 Campos Mar) — o campo `paired_basin_id` cruza a "
                "contraparte. O campo `ambiente` distingue marítimo/terrestre, "
                "ortogonal ao status de Bloco no PROPEX."
            ),
            "layer": "layer4",
            "related_entities": ["bacia-sedimentar", "poco", "bloco"],
            "evidence_refs": ["ANP-699/2017"],
            "pairs_terra_mar_count": sum(1 for c in concepts if c.get("paired_basin_id")) // 2,
        },
        "concepts": concepts,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    uf_payload = build_uf_payload()
    bacia_payload = build_bacia_payload()

    print(f"UFs: {len(uf_payload['concepts'])}")
    print(f"  Coastal (admite poços marítimos): {sum(1 for c in uf_payload['concepts'] if c['is_coastal'])}")
    print(f"Bacias: {len(bacia_payload['concepts'])}")
    print(f"  Marítimas: {sum(1 for c in bacia_payload['concepts'] if c['is_offshore'])}")
    print(f"  Terrestres: {sum(1 for c in bacia_payload['concepts'] if c['ambiente'] == 'terrestre')}")
    print(f"  Sem distinção MAR/TERRA: {sum(1 for c in bacia_payload['concepts'] if c['ambiente'] is None)}")
    print(f"  Pares MAR↔TERRA: {bacia_payload['meta']['pairs_terra_mar_count']}")

    if args.dry_run:
        print("--dry-run; not writing.")
        return 0

    TARGET_UF.write_text(json.dumps(uf_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    TARGET_BACIA.write_text(json.dumps(bacia_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote {TARGET_UF.relative_to(ROOT)}")
    print(f"Wrote {TARGET_BACIA.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
