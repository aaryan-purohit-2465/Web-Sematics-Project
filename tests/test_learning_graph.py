from pathlib import Path
import unittest

from learning_graph import LearningKnowledgeGraph


GRAPH = LearningKnowledgeGraph(Path(__file__).resolve().parents[1] / "data" / "catalog.json")


class LearningGraphTests(unittest.TestCase):
    def test_learning_path_orders_prerequisites_before_goal(self):
        path = GRAPH.learning_path("explainable-ai", {"web-basics": 0.9})
        ids = [item["id"] for item in path]

        self.assertLess(ids.index("rdf"), ids.index("knowledge-graphs"))
        self.assertLess(ids.index("recommendation"), ids.index("explainable-ai"))
        self.assertNotIn("web-basics", ids)

    def test_recommendations_explain_high_priority_graph_goal(self):
        profile = {
            "goals": ["explainable-ai"],
            "preferredFormat": "lab",
            "preferredLevel": "advanced",
            "mastery": {"web-basics": 0.9, "rdf": 0.4, "sparql": 0.2, "knowledge-graphs": 0.1},
        }

        recommendations = GRAPH.recommend(profile)

        self.assertTrue(recommendations)
        self.assertIn(recommendations[0].resource["id"], {"res-turtle", "res-xai", "res-kg", "res-sparql", "res-rec"})
        self.assertTrue(recommendations[0].reasons)
        self.assertTrue(any("prerequisite" in reason.lower() or "goal" in reason.lower() for reason in recommendations[0].reasons))

    def test_overview_counts_semantic_assets(self):
        overview = GRAPH.overview()

        self.assertEqual(overview["concepts"], 12)
        self.assertEqual(overview["resources"], 12)
        self.assertGreater(overview["relations"], 20)


if __name__ == "__main__":
    unittest.main()
