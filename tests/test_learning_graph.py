from pathlib import Path

from learning_graph import LearningKnowledgeGraph


GRAPH = LearningKnowledgeGraph(Path(__file__).resolve().parents[1] / "data" / "catalog.json")


def test_learning_path_orders_prerequisites_before_goal():
    path = GRAPH.learning_path("explainable-ai", {"web-basics": 0.9})
    ids = [item["id"] for item in path]

    assert ids.index("rdf") < ids.index("knowledge-graphs")
    assert ids.index("recommendation") < ids.index("explainable-ai")
    assert "web-basics" not in ids


def test_recommendations_explain_high_priority_graph_goal():
    profile = {
        "goals": ["explainable-ai"],
        "preferredFormat": "lab",
        "preferredLevel": "advanced",
        "mastery": {"web-basics": 0.9, "rdf": 0.4, "sparql": 0.2, "knowledge-graphs": 0.1},
    }

    recommendations = GRAPH.recommend(profile)

    assert recommendations
    assert recommendations[0].resource["id"] in {"res-xai", "res-kg", "res-sparql", "res-rec"}
    assert recommendations[0].reasons


def test_overview_counts_semantic_assets():
    overview = GRAPH.overview()

    assert overview["concepts"] == 12
    assert overview["resources"] == 12
    assert overview["relations"] > 20
