"""test_data.py — Tests for the data module (load_json, load_jsonl, data_dir)."""

import json
from pathlib import Path

import pytest
from geobrain.data import data_dir, load_json, load_jsonl


# ---------------------------------------------------------------------------
# data_dir()
# ---------------------------------------------------------------------------


def test_data_dir_returns_path():
    assert isinstance(data_dir(), Path)


def test_data_dir_exists():
    assert data_dir().is_dir()


# ---------------------------------------------------------------------------
# load_json() — well-known bundled files
# ---------------------------------------------------------------------------


def test_load_json_glossary_returns_dict_or_list():
    result = load_json("glossary.json")
    assert isinstance(result, (dict, list))


def test_load_json_glossary_nonempty():
    result = load_json("glossary.json")
    assert len(result) > 0


def test_load_json_entity_graph_returns_dict_or_list():
    result = load_json("entity-graph.json")
    assert isinstance(result, (dict, list))


def test_load_json_entity_graph_nonempty():
    result = load_json("entity-graph.json")
    assert len(result) > 0


def test_load_json_acronyms_returns_list_or_dict():
    result = load_json("acronyms.json")
    assert isinstance(result, (dict, list))


def test_load_json_missing_file_raises_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_json("nonexistent_file_that_does_not_exist.json")


def test_load_json_returns_valid_python_object():
    # Verify deserialization is consistent with stdlib json
    p = data_dir() / "glossary.json"
    expected = json.loads(p.read_text(encoding="utf-8"))
    assert load_json("glossary.json") == expected


# ---------------------------------------------------------------------------
# load_jsonl() — rag-corpus
# ---------------------------------------------------------------------------


def test_load_jsonl_rag_corpus_returns_list():
    result = load_jsonl("rag-corpus.jsonl")
    assert isinstance(result, list)


def test_load_jsonl_rag_corpus_nonempty():
    result = load_jsonl("rag-corpus.jsonl")
    assert len(result) > 0


def test_load_jsonl_rag_corpus_records_are_dicts():
    result = load_jsonl("rag-corpus.jsonl")
    assert all(isinstance(row, dict) for row in result)


def test_load_jsonl_missing_file_raises_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_jsonl("nonexistent_corpus.jsonl")
