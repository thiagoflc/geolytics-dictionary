# Provenance — Petrobras 3W Dataset v2.0.0

## Identificação

| Campo | Valor |
|---|---|
| Nome | 3W Dataset |
| Versão | 2.0.0 |
| Repositório | https://github.com/petrobras/3W |
| DOI | 10.1016/j.petrol.2019.106223 |
| Licença | Creative Commons Attribution 4.0 (CC-BY 4.0) |
| Data de captura | 2026-05-03 |

## Autores / Referência

> Vargas, R.E.V., Munaro, C.J., Ciarelli, P.M., Medeiros, A.G., Bruno, B.G., Depoliti, E.C.,  
> de Souza Hochleitner, E., Amaro, V.P., & Fonseca, T.C. (2019).  
> A realistic and public dataset with rare undesirable real events in oil wells.  
> *Journal of Petroleum Science and Engineering*, 181, 106223.  
> https://doi.org/10.1016/j.petrol.2019.106223

## Arquivos versionados

| Arquivo | Origem | SHA-256 |
|---|---|---|
| `dataset.ini` | `dataset/dataset.ini` (raiz do repositório) | `c5ffad72bc1c46bccffa1e18412f2ddb87ca0e96eb7d2dfba92a4bc38a45bba2` |
| `enums.py` | `toolkit/ThreeWToolkit/core/enums.py` | `fef829488c82f5c28b150d2bb9cf5c85fb06a7bcc2aa5316208aba758b2dccac` |

## Conteúdo absorvido pelo GeoBrain

O GeoBrain absorve apenas o **schema** e os metadados semânticos do 3W — nenhuma instância
`.parquet` de séries temporais é incluída neste repositório.

Itens derivados:

- **27 variáveis de sensores** → 27 nós `type: "instrument"` em `data/entity-graph.json`
- **10 classes de evento** → 10 nós `type: "operational", subtype: "event"`
- **13 equipamentos do Xmas-tree / ANM** → 13 nós `type: "equipment"` (+ enriquecimento do nó `dhsv` existente)
- **4 taxonomias** → adicionadas em `data/taxonomies.json`
- **1 entry de dataset** → adicionada em `data/datasets.json`

Todos os nós derivados carregam `legal_source: "Petrobras 3W v2.0.0"` e `datasets: ["dataset-3w"]`.

## Atribuição obrigatória (CC-BY 4.0)

Qualquer redistribuição ou obra derivada deve incluir a referência acima e o link para a licença:  
https://creativecommons.org/licenses/by/4.0/

## URLs canônicas

```
https://raw.githubusercontent.com/petrobras/3W/main/dataset/dataset.ini
https://raw.githubusercontent.com/petrobras/3W/main/toolkit/ThreeWToolkit/core/enums.py
```
