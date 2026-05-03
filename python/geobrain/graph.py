"""graph.py — KnowledgeGraph: NetworkX wrapper over entity-graph.json."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .data import fetch_json, load_json


@dataclass(frozen=True)
class Entity:
    """A node in the knowledge graph."""

    id: str
    label: str
    label_en: str
    type: str
    definition: str
    geocoverage: list[str] = field(default_factory=list)
    osdu_kind: str | None = None
    petrokgraph_uri: str | None = None
    owl_uri: str | None = None
    synonyms_pt: list[str] = field(default_factory=list)
    synonyms_en: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict, compare=False, repr=False)


def _entity_from_dict(d: dict[str, Any]) -> Entity:
    return Entity(
        id=d.get("id", ""),
        label=d.get("label", d.get("id", "")),
        label_en=d.get("label_en", ""),
        type=d.get("type", ""),
        definition=d.get("definition", d.get("definicao", "")),
        geocoverage=d.get("geocoverage", []),
        osdu_kind=d.get("osdu_kind"),
        petrokgraph_uri=d.get("petrokgraph_uri"),
        owl_uri=d.get("owl_uri"),
        synonyms_pt=d.get("synonyms_pt", []),
        synonyms_en=d.get("synonyms_en", []),
        raw=d,
    )


class KnowledgeGraph:
    """NetworkX-backed knowledge graph over the Geolytics entity graph.

    Requires the ``networkx`` optional dependency:

        pip install geobrain[graph]

    Usage::

        kg = KnowledgeGraph.from_local()
        kg.entity("poco")
        kg.neighbors("poco", hops=2)
        kg.shortest_path("poco", "anp")
        kg.cypher_export()
    """

    def __init__(self, graph_data: dict[str, Any]) -> None:
        try:
            import networkx as nx  # type: ignore[import]
        except ImportError as exc:
            raise ImportError(
                "networkx is required for KnowledgeGraph. "
                "Install it with: pip install geobrain[graph]"
            ) from exc

        self._nx = nx
        self._G: Any = nx.DiGraph()
        self._entities: dict[str, Entity] = {}

        nodes = graph_data.get("nodes", [])
        edges = graph_data.get("edges", [])

        for node_dict in nodes:
            entity = _entity_from_dict(node_dict)
            self._entities[entity.id] = entity
            self._G.add_node(
                entity.id,
                entity=entity,
                **{
                    "label": entity.label,
                    "label_en": entity.label_en,
                    "type": entity.type,
                },
            )

        for edge_dict in edges:
            src = edge_dict.get("source", edge_dict.get("from", ""))
            tgt = edge_dict.get("target", edge_dict.get("to", ""))
            if not src or not tgt:
                continue
            self._G.add_edge(
                src,
                tgt,
                **{
                    "relation": edge_dict.get("relation", ""),
                    "relation_label_pt": edge_dict.get("relation_label_pt", ""),
                    "relation_label_en": edge_dict.get("relation_label_en", ""),
                },
            )

    @classmethod
    def from_local(cls) -> KnowledgeGraph:
        """Build a KnowledgeGraph from the bundled entity-graph.json."""
        data = load_json("entity-graph.json")
        return cls(data)

    @classmethod
    def from_remote(cls) -> KnowledgeGraph:
        """Build a KnowledgeGraph by fetching entity-graph.json from GitHub.

        Requires ``requests``.
        """
        data = fetch_json("entity-graph.json")
        return cls(data)

    def entity(self, entity_id: str) -> Entity | None:
        """Return an Entity by ID, or None if not found."""
        return self._entities.get(entity_id)

    def neighbors(self, entity_id: str, hops: int = 1) -> list[Entity]:
        """Return all entities reachable from entity_id within ``hops`` steps.

        Uses an undirected BFS (ignores edge direction) to find related entities.
        Does not include the start entity itself.
        """
        if entity_id not in self._G:
            return []
        G_undirected = self._G.to_undirected()
        reachable = set(
            self._nx.single_source_shortest_path_length(G_undirected, entity_id, cutoff=hops).keys()
        )
        reachable.discard(entity_id)
        return [self._entities[nid] for nid in reachable if nid in self._entities]

    def shortest_path(self, source: str, target: str) -> list[Entity]:
        """Return the shortest path between two entities as a list of Entity objects.

        Returns an empty list if no path exists.
        """
        G_undirected = self._G.to_undirected()
        try:
            path_ids = self._nx.shortest_path(G_undirected, source, target)
        except (self._nx.NetworkXNoPath, self._nx.NodeNotFound):
            return []
        return [self._entities[nid] for nid in path_ids if nid in self._entities]

    def cypher_export(self) -> str:
        """Generate a Cypher LOAD script for Neo4j.

        Returns a string with MERGE statements for all nodes and relationships.
        """
        lines = ["// Geolytics Knowledge Graph — Cypher load script", ""]

        # Nodes
        lines.append("// --- Nodes ---")
        for node_id, data in self._G.nodes(data=True):
            entity: Entity | None = data.get("entity")
            if entity is None:
                continue
            label_safe = entity.label.replace("'", "\\'")
            label_en_safe = entity.label_en.replace("'", "\\'")
            lines.append(
                f"MERGE (n:Entity {{id: '{node_id}'}}) "
                f"SET n.label = '{label_safe}', "
                f"n.label_en = '{label_en_safe}', "
                f"n.type = '{entity.type}';"
            )

        lines.append("")
        lines.append("// --- Relationships ---")
        for src, tgt, edata in self._G.edges(data=True):
            rel = (
                (edata.get("relation") or "RELATED_TO").upper().replace(" ", "_").replace("-", "_")
            )
            rel_label_pt = edata.get("relation_label_pt", "").replace("'", "\\'")
            lines.append(
                f"MATCH (a:Entity {{id: '{src}'}}), (b:Entity {{id: '{tgt}'}}) "
                f"MERGE (a)-[r:{rel} {{label_pt: '{rel_label_pt}'}}]->(b);"
            )

        return "\n".join(lines)

    def node_count(self) -> int:
        """Return the number of nodes."""
        return self._G.number_of_nodes()

    def edge_count(self) -> int:
        """Return the number of edges."""
        return self._G.number_of_edges()

    def all_entities(self) -> list[Entity]:
        """Return all entities in the graph."""
        return list(self._entities.values())
