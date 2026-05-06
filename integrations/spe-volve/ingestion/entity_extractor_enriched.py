"""LLMGraphTransformer-based entity extraction from report chunks — enriched version.

Drop-in replacement for src/volve/ingestion/entity_extractor.py in the
spe-2026-challenge project.  Expands the node/relationship vocabulary from
PetroGold NER types (regis-ner-schema.json) to better capture the semantic
content of Volve daily drilling reports.

External API (unchanged):
    extract_entities_from_chunks(documents) -> list[GraphDocument]
    write_graph_documents_to_neo4j(graph_docs)

New public helpers:
    get_entity_schema() -> dict
    DISAMBIGUATION_NOTES  (module-level constant)
    SYSTEM_PROMPT_ENRICHMENT  (module-level constant)
"""

from __future__ import annotations

import logging

from langchain_openai import ChatOpenAI
from langchain_neo4j import Neo4jGraph
from langchain_neo4j.graphs.graph_document import GraphDocument

from src.volve.config import LLM_MODEL_MINI, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Node types
# Original: Well, Formation, Equipment, Issue, Operation, Recommendation
# Added from PetroGold schema and Volve drilling context
# ---------------------------------------------------------------------------
ALLOWED_NODES = [
    # --- original ---
    "Well",
    "Formation",
    "Equipment",
    "Issue",
    "Operation",
    "Recommendation",
    # --- added ---
    "Lithology",              # ROC — petrographic type (sandstone, shale, …)
    "DrillingFluid",          # FLU — OBM/WBM, density, viscosity values
    "PetrophysicalProperty",  # PRP — porosity %, permeability mD, GR API, …
    "DrillingEvent",          # NPT category: stuck pipe, kick, loss circ, …
    "FormationAge",           # IDA — Jurassic, Triassic, Cretaceous, …
    "StratigraphicInterval",  # INT — depth interval 3100-3250 m, zone name
    "Organization",           # ORG — operator, service company, regulator
    "BHAComponentType",       # bit, MWD, stabiliser, motor, jar — generic type
]

# ---------------------------------------------------------------------------
# Relationship types
# Original: MENTIONS, ENCOUNTERED_IN, CAUSED_BY, RESOLVED_BY, RECOMMENDS
# ---------------------------------------------------------------------------
ALLOWED_RELATIONSHIPS = [
    # --- original ---
    "MENTIONS",
    "ENCOUNTERED_IN",
    "CAUSED_BY",
    "RESOLVED_BY",
    "RECOMMENDS",
    # --- added ---
    "HAS_LITHOLOGY",      # Formation/StratigraphicInterval -> Lithology
    "DETECTED_IN",        # DrillingEvent/Issue -> Formation or StratigraphicInterval
    "CORRELATES_WITH",    # Formation <-> Formation or StratigraphicInterval
    "HAS_AGE",            # Formation -> FormationAge
    "HAS_PROPERTY",       # Formation/Lithology -> PetrophysicalProperty
    "OPERATED_BY",        # Well/Operation -> Organization
    "USES_FLUID",         # Operation/Well -> DrillingFluid
    "INDICATES",          # PetrophysicalProperty -> Formation or Lithology
]

# ---------------------------------------------------------------------------
# Disambiguation notes derived from regis-ner-schema.json
# ---------------------------------------------------------------------------
DISAMBIGUATION_NOTES: dict[str, str] = {
    "Lithology": (
        "ROC in PetroGold — petrographic type of rock (sandstone, limestone, "
        "shale, dolomite). Do NOT confuse with Formation (FOR), which is the "
        "formal stratigraphic name of a unit (e.g. 'Hugin Fm'). "
        "Example Volve values: 'fine-grained sandstone', 'calcareous shale', "
        "'tight limestone'."
    ),
    "Formation": (
        "FOR in PetroGold — formal lithostratigraphic unit name. "
        "North Sea examples: Hugin, Sleipner, Skagerrak, Statfjord, Brent. "
        "Distinct from Lithology (the rock type within the formation)."
    ),
    "DrillingFluid": (
        "FLU in PetroGold — polysemous: can be reservoir fluid (oil, gas, brine) "
        "or drilling/completion fluid (OBM, WBM, synthetic). In Volve reports "
        "context this type represents drilling mud systems. "
        "Capture density (sg), rheology, and system type when present. "
        "Example: 'OBM 1.85 sg', 'KCl-polymer WBM', 'formate brine'."
    ),
    "PetrophysicalProperty": (
        "PRP in PetroGold — numeric attribute with unit: porosity (%), "
        "permeability (mD), GR (API), resistivity (ohm·m), Sw (%), "
        "ROP (m/hr), WOB (klbf), torque (kN·m). "
        "Link to the relevant Formation or StratigraphicInterval via HAS_PROPERTY."
    ),
    "DrillingEvent": (
        "NPT / stuck-pipe / kick events in drilling reports. "
        "Subtypes visible in text: 'stuck pipe', 'wellbore influx/kick', "
        "'lost circulation', 'washout', 'packoff', 'twist-off'. "
        "Distinct from Issue (which is a general problem node); DrillingEvent "
        "is specifically a non-productive-time event with depth and duration."
    ),
    "FormationAge": (
        "IDA in PetroGold — formal ICS geologic time unit (epoch/period/era). "
        "Volve context: Jurassic (Hugin, Sleipner, Cook), Triassic (Skagerrak), "
        "Permian (Rotliegend). "
        "Distinct from StratigraphicInterval (INT), which is a depth range."
    ),
    "StratigraphicInterval": (
        "INT in PetroGold — a section bounded by two depth markers (top/base) "
        "or named zone markers (e.g. 'BVE-110', 'Top Hugin', '3100-3250 mMD'). "
        "Used for testing, completion, and evaluation intervals. "
        "Distinct from FormationAge (geological time) and Formation (named unit)."
    ),
    "Organization": (
        "ORG in PetroGold — operator company, drilling contractor, service "
        "company, or regulator. Volve context: Statoil (operator), "
        "Schlumberger/SLB, Halliburton, Baker Hughes, NPD (regulator). "
        "Map 'company', 'contractor', 'service provider' mentions to this type."
    ),
    "BHAComponentType": (
        "Generic type of Bottom Hole Assembly component — bit, MWD/LWD tool, "
        "motor (PDM), rotary steerable (RSS), stabiliser, jar, cross-over sub. "
        "Use this when the text describes the type of component rather than a "
        "specific serial-numbered item (which would be Equipment)."
    ),
    "Well": (
        "POC in PetroGold — well identifier. Volve format: 15/9-F-XX. "
        "Includes directional variants (e.g. 15/9-F-1 A, 15/9-F-5). "
        "Distinguish well name from wellbore name when both appear."
    ),
    "Operation": (
        "Drilling or completion activity with a start/end context: 'tripping in', "
        "'reaming', 'cementing', 'perforating', 'running casing'. "
        "Capture depth, duration, and associated equipment when mentioned."
    ),
}

# ---------------------------------------------------------------------------
# System prompt enrichment for LLMGraphTransformer
# ---------------------------------------------------------------------------
SYSTEM_PROMPT_ENRICHMENT = """
You are extracting a knowledge graph from daily drilling reports (DDRs) for
the Volve oil field, North Sea, Norway (block 15/9, Ekofisk area).

CONTEXT
- Operator: Statoil (now Equinor); wells drilled roughly 1994-2008.
- Principal reservoir: Jurassic Hugin Formation (sandstone), supported by
  Sleipner, Cook, and Statfjord formations. Overburden: Cretaceous and Tertiary
  shales. Basement: Permian/Triassic Skagerrak / Zechstein.
- Typical drilling hazards: overpressure in Heimdal sands, lost circulation in
  Palaeocene, stuck pipe in clay-rich shales, shallow gas in overburden.
- Fluid system: oil-based mud (OBM) is dominant in reservoir sections; KCl-
  polymer WBM used in upper sections.

NODE EXTRACTION RULES
1. Formation: extract formal unit names (Hugin Fm, Sleipner Fm, Brent Gp, etc.)
   even if written informally ("Hugin sand", "top Hugin").
2. Lithology: extract rock descriptions ("fine-grained sandstone", "tight
   limestone", "black shale") separately from the formation name.
3. DrillingFluid: extract fluid-system descriptions together with density and
   system type ("OBM 1.85 sg", "12.5 ppg KCl-polymer").
4. PetrophysicalProperty: extract measured or estimated numeric values with
   units ("porosity 18%", "k ~50 mD", "GR 45 API", "ROP 8 m/hr").
5. DrillingEvent: extract NPT events with depth and duration if stated
   ("stuck pipe at 3 200 m for 6 hrs", "kick 1.2 m³ influx at 2 850 m").
6. FormationAge: extract era/epoch labels attached to formations or lithologies
   ("Jurassic reservoir", "Triassic red-beds").
7. StratigraphicInterval: extract depth-defined or zone-named sections
   ("interval 3 050-3 150 mMD", "Top Hugin to Base Hugin", "Zone 2B").
8. Organization: extract company names (operator, drilling contractor, service
   company) when explicitly mentioned.
9. BHAComponentType: extract BHA component types listed in the daily BHA
   description ("8.5\" PDC bit", "MWD/LWD string", "6¾\" PDM motor").

RELATIONSHIP EXTRACTION RULES
- HAS_LITHOLOGY: link Formation → Lithology when the report states the
  rock type inside a formation ("Hugin consists of fine sandstone").
- DETECTED_IN: link DrillingEvent or Issue → Formation or StratigraphicInterval
  when a depth or zone is given for the event.
- HAS_AGE: link Formation → FormationAge ("Hugin (Jurassic)").
- HAS_PROPERTY: link Formation or Lithology → PetrophysicalProperty.
- USES_FLUID: link Operation or Well → DrillingFluid.
- OPERATED_BY: link Well or Operation → Organization when the operator or
  contractor is mentioned in context.
- CORRELATES_WITH: link two Formation nodes when the text states they are
  equivalent or correlatable ("Hugin correlates with Sleipner in this area").

DISAMBIGUATION
- Do NOT create a Formation node for generic depth references; use
  StratigraphicInterval instead ("from 3 050 to 3 200 m").
- Do NOT tag a PetrophysicalProperty node for every number in the text;
  only extract values that are described as rock or fluid properties.
- DrillingEvent is for NPT events; use Issue for equipment or operational
  problems that are not specifically NPT-categorised.
- Prefer specific node types over generic ones (Lithology over Formation
  for rock-type descriptions; DrillingEvent over Issue for stuck-pipe events).
"""


# ---------------------------------------------------------------------------
# Public API — unchanged signatures
# ---------------------------------------------------------------------------

def extract_entities_from_chunks(documents: list) -> list[GraphDocument]:
    """Extract graph entities from LangChain Documents using LLMGraphTransformer.

    Drop-in replacement for the original function.  Uses the enriched node/
    relationship vocabulary and injects a domain-specific system prompt when
    the LLMGraphTransformer supports it.

    Args:
        documents: List of LangChain Document objects (typically ReportChunks
                   converted to Document format by the upstream pipeline).

    Returns:
        List of GraphDocument objects ready for ingestion into Neo4j.
    """
    from langchain_experimental.graph_transformers import LLMGraphTransformer

    llm = ChatOpenAI(model=LLM_MODEL_MINI, temperature=0)

    transformer = LLMGraphTransformer(
        llm=llm,
        allowed_nodes=ALLOWED_NODES,
        allowed_relationships=ALLOWED_RELATIONSHIPS,
    )

    # Inject domain context if the transformer exposes a prompt attribute.
    # LLMGraphTransformer stores the prompt internally; we append enrichment
    # to the system message if the attribute is writable.
    _inject_system_prompt(transformer)

    log.info("Extracting entities from %d documents...", len(documents))
    graph_docs = transformer.convert_to_graph_documents(documents)
    log.info("Extracted %d graph documents", len(graph_docs))

    return graph_docs


def write_graph_documents_to_neo4j(graph_docs: list[GraphDocument]) -> None:
    """Write extracted graph documents to Neo4j.

    Drop-in replacement for the original function.  Signature and behaviour
    are identical.

    Args:
        graph_docs: List of GraphDocument objects returned by
                    extract_entities_from_chunks().
    """
    graph = Neo4jGraph(url=NEO4J_URI, username=NEO4J_USER, password=NEO4J_PASSWORD)
    graph.add_graph_documents(graph_docs, include_source=True)
    log.info("Wrote %d graph documents to Neo4j", len(graph_docs))


# ---------------------------------------------------------------------------
# New public helper
# ---------------------------------------------------------------------------

def get_entity_schema() -> dict:
    """Return a structured description of every node type and relationship type.

    Useful for inspection, documentation generation, and debugging extraction
    quality.  The returned dict has two keys: 'nodes' and 'relationships', each
    mapping a type name to its description and (for nodes) a disambiguation note.

    Returns:
        Dict with keys 'nodes' (dict[str, dict]) and 'relationships' (dict[str, str]).

    Example::

        schema = get_entity_schema()
        print(schema['nodes']['Lithology']['disambiguation'])
        for rel, desc in schema['relationships'].items():
            print(rel, '->', desc)
    """
    node_descriptions: dict[str, str] = {
        "Well": "A wellbore identifier in the Volve field (e.g. 15/9-F-5).",
        "Formation": (
            "A formal lithostratigraphic unit (e.g. Hugin Fm, Sleipner Fm). "
            "Structural nodes for named geological units."
        ),
        "Equipment": "A physical tool or piece of hardware (BHA item, pump, sensor …).",
        "Issue": (
            "A general operational or equipment problem mentioned in the report "
            "that is not classified as a specific DrillingEvent."
        ),
        "Operation": (
            "A drilling or completion activity (tripping, reaming, cementing, "
            "perforation …) with associated depth and time context."
        ),
        "Recommendation": (
            "An action item or engineering recommendation stated in the report."
        ),
        "Lithology": (
            "Petrographic rock type (sandstone, shale, limestone …). "
            "Linked to Formation via HAS_LITHOLOGY."
        ),
        "DrillingFluid": (
            "Mud system description with type and density (OBM 1.85 sg, "
            "KCl-polymer WBM …)."
        ),
        "PetrophysicalProperty": (
            "Numeric rock or fluid attribute with unit (porosity 18%, "
            "permeability 50 mD, GR 45 API …)."
        ),
        "DrillingEvent": (
            "An NPT-category drilling event (stuck pipe, kick, lost circulation "
            "…) with depth and duration context."
        ),
        "FormationAge": (
            "ICS geologic time unit associated with a formation or lithology "
            "(Jurassic, Triassic, Cretaceous …)."
        ),
        "StratigraphicInterval": (
            "A depth-delimited section or named zone (3 050-3 150 mMD, "
            "Top Hugin to Base Hugin, Zone 2B …)."
        ),
        "Organization": (
            "Company or regulatory body (operator, drilling contractor, "
            "service company, NPD …)."
        ),
        "BHAComponentType": (
            "Generic category of a BHA element (PDC bit, MWD, PDM motor, "
            "stabiliser, jar …)."
        ),
    }

    relationship_descriptions: dict[str, str] = {
        "MENTIONS": "Generic mention link between a chunk source and any entity.",
        "ENCOUNTERED_IN": "An issue or event was encountered inside a formation or interval.",
        "CAUSED_BY": "An issue or event was caused by a specific entity.",
        "RESOLVED_BY": "An issue was resolved by a specific operation or equipment action.",
        "RECOMMENDS": "A report section recommends a specific action or entity.",
        "HAS_LITHOLOGY": "A formation or interval is composed of a specific lithology.",
        "DETECTED_IN": "A drilling event or issue was detected in a specific formation or interval.",
        "CORRELATES_WITH": "Two formations or intervals are stratigraphically equivalent.",
        "HAS_AGE": "A formation or lithology belongs to a given geologic age.",
        "HAS_PROPERTY": "A formation or lithology has a measured petrophysical property.",
        "OPERATED_BY": "A well or operation is performed by or under a given organization.",
        "USES_FLUID": "An operation or well section uses a specific drilling fluid.",
        "INDICATES": "A petrophysical property or observation indicates a formation or lithology.",
    }

    return {
        "nodes": {
            name: {
                "description": node_descriptions[name],
                "disambiguation": DISAMBIGUATION_NOTES.get(name, ""),
            }
            for name in ALLOWED_NODES
        },
        "relationships": {
            name: relationship_descriptions[name]
            for name in ALLOWED_RELATIONSHIPS
        },
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _inject_system_prompt(transformer: object) -> None:
    """Append SYSTEM_PROMPT_ENRICHMENT to transformer.prompt if possible.

    LLMGraphTransformer in langchain-experimental exposes a ChatPromptTemplate
    via the ``prompt`` attribute.  We attempt a best-effort injection that
    leaves the transformer unchanged if the attribute is absent or read-only.

    This is intentionally silent on failure so callers always get a working
    transformer even when the library version does not support prompt injection.
    """
    try:
        prompt = getattr(transformer, "prompt", None)
        if prompt is None:
            return

        # ChatPromptTemplate stores messages in prompt.messages.
        # The first HumanMessage or SystemMessage is the extraction template.
        # We append the enrichment to the system context by replacing the
        # first SystemMessage content, or by prepending a new system message.
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.messages import SystemMessage

        if not isinstance(prompt, ChatPromptTemplate):
            return

        messages = list(prompt.messages)
        for i, msg in enumerate(messages):
            if isinstance(msg, SystemMessage):
                # Append enrichment to existing system message.
                original_content = msg.content if isinstance(msg.content, str) else ""
                messages[i] = SystemMessage(
                    content=original_content + "\n\n" + SYSTEM_PROMPT_ENRICHMENT.strip()
                )
                transformer.prompt = ChatPromptTemplate.from_messages(messages)
                log.debug("Injected domain enrichment into existing SystemMessage.")
                return

        # No SystemMessage found — prepend one.
        messages.insert(0, SystemMessage(content=SYSTEM_PROMPT_ENRICHMENT.strip()))
        transformer.prompt = ChatPromptTemplate.from_messages(messages)
        log.debug("Prepended new SystemMessage with domain enrichment.")

    except Exception as exc:  # noqa: BLE001
        log.debug(
            "System prompt injection skipped (library may not support it): %s", exc
        )
