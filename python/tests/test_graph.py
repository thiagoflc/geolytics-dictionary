"""test_graph.py — Tests for KnowledgeGraph."""

import pytest

pytest.importorskip("networkx", reason="networkx required for graph tests")

from geobrain import Entity, KnowledgeGraph


@pytest.fixture(scope="module")
def kg():
    return KnowledgeGraph.from_local()


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


def test_from_local_returns_knowledge_graph(kg):
    assert isinstance(kg, KnowledgeGraph)


def test_node_count_positive(kg):
    assert kg.node_count() > 0


def test_edge_count_positive(kg):
    assert kg.edge_count() > 0


# ---------------------------------------------------------------------------
# entity()
# ---------------------------------------------------------------------------


def test_entity_poco_found(kg):
    e = kg.entity("poco")
    assert e is not None
    assert isinstance(e, Entity)
    assert e.id == "poco"


def test_entity_campo_found(kg):
    e = kg.entity("campo")
    assert e is not None
    assert e.id == "campo"


def test_entity_unknown_returns_none(kg):
    e = kg.entity("zzz_not_a_real_entity_xyz")
    assert e is None


def test_entity_has_label(kg):
    e = kg.entity("poco")
    assert e.label


def test_entity_has_type(kg):
    e = kg.entity("poco")
    assert e.type


# ---------------------------------------------------------------------------
# neighbors()
# ---------------------------------------------------------------------------


def test_neighbors_poco_returns_entities(kg):
    neighbors = kg.neighbors("poco", hops=1)
    assert len(neighbors) >= 1
    assert all(isinstance(n, Entity) for n in neighbors)


def test_neighbors_hops2_more_than_hops1(kg):
    n1 = kg.neighbors("poco", hops=1)
    n2 = kg.neighbors("poco", hops=2)
    assert len(n2) >= len(n1)


def test_neighbors_unknown_node_returns_empty(kg):
    result = kg.neighbors("zzz_not_a_real_entity_xyz", hops=1)
    assert result == []


def test_neighbors_does_not_include_start_node(kg):
    neighbors = kg.neighbors("poco", hops=2)
    ids = [n.id for n in neighbors]
    assert "poco" not in ids


# ---------------------------------------------------------------------------
# shortest_path()
# ---------------------------------------------------------------------------


def test_shortest_path_poco_to_reservatorio(kg):
    path = kg.shortest_path("poco", "reservatorio")
    assert len(path) >= 2
    assert all(isinstance(e, Entity) for e in path)
    assert path[0].id == "poco"
    assert path[-1].id == "reservatorio"


def test_shortest_path_poco_to_bacia_sedimentar(kg):
    path = kg.shortest_path("poco", "bacia-sedimentar")
    assert len(path) >= 2
    assert path[0].id == "poco"
    assert path[-1].id == "bacia-sedimentar"


def test_shortest_path_same_node(kg):
    # Shortest path from node to itself should be just [node] or empty
    path = kg.shortest_path("poco", "poco")
    assert isinstance(path, list)


def test_shortest_path_no_path_returns_empty(kg):
    # Attempt with a nonexistent node — should return empty list
    path = kg.shortest_path("poco", "zzz_not_a_real_entity_xyz")
    assert path == []


# ---------------------------------------------------------------------------
# all_entities()
# ---------------------------------------------------------------------------


def test_all_entities_non_empty(kg):
    entities = kg.all_entities()
    assert len(entities) > 0
    assert all(isinstance(e, Entity) for e in entities)


# ---------------------------------------------------------------------------
# cypher_export()
# ---------------------------------------------------------------------------


def test_cypher_export_returns_string(kg):
    cypher = kg.cypher_export()
    assert isinstance(cypher, str)
    assert "MERGE" in cypher
