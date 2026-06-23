"""Knowledge graph and explainable recommendation logic."""

from __future__ import annotations

import json
from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Recommendation:
    resource: dict
    score: float
    reasons: list[str]
    concepts: list[dict]
    missing_prerequisites: list[dict]

    def as_dict(self) -> dict:
        return {
            "resource": self.resource,
            "score": round(self.score, 3),
            "reasons": self.reasons,
            "concepts": self.concepts,
            "missingPrerequisites": self.missing_prerequisites,
        }


class LearningKnowledgeGraph:
    """Small in-memory graph optimized for an interactive academic demo."""

    def __init__(self, data_path: str | Path):
        self.data_path = Path(data_path)
        self.data = json.loads(self.data_path.read_text(encoding="utf-8"))
        self.concepts = {item["id"]: item for item in self.data["concepts"]}
        self.resources = {item["id"]: item for item in self.data["resources"]}
        self.prerequisites = defaultdict(list)
        for concept in self.data["concepts"]:
            self.prerequisites[concept["id"]].extend(concept.get("prerequisites", []))

    def overview(self) -> dict:
        edge_count = sum(len(c.get("prerequisites", [])) for c in self.data["concepts"])
        edge_count += sum(len(r["concepts"]) for r in self.data["resources"])
        return {
            "concepts": len(self.concepts),
            "resources": len(self.resources),
            "relations": edge_count,
            "domains": sorted({c["domain"] for c in self.concepts.values()}),
        }

    def concept_graph(self) -> dict:
        nodes = [
            {"id": c["id"], "label": c["label"], "domain": c["domain"], "level": c["level"]}
            for c in self.concepts.values()
        ]
        links = [
            {"source": prerequisite, "target": concept["id"], "type": "prerequisite"}
            for concept in self.concepts.values()
            for prerequisite in concept.get("prerequisites", [])
        ]
        return {"nodes": nodes, "links": links}

    def prerequisite_closure(self, concept_ids: list[str]) -> set[str]:
        found: set[str] = set()
        queue = deque(concept_ids)
        while queue:
            current = queue.popleft()
            for prerequisite in self.prerequisites[current]:
                if prerequisite not in found:
                    found.add(prerequisite)
                    queue.append(prerequisite)
        return found

    def learning_path(self, goal: str, mastery: dict[str, float]) -> list[dict]:
        if goal not in self.concepts:
            return []
        ordered: list[str] = []
        visited: set[str] = set()

        def visit(concept_id: str) -> None:
            if concept_id in visited:
                return
            visited.add(concept_id)
            for prerequisite in self.prerequisites[concept_id]:
                visit(prerequisite)
            if mastery.get(concept_id, 0) < 0.7:
                ordered.append(concept_id)

        visit(goal)
        return [
            {
                **self.concepts[concept_id],
                "mastery": round(mastery.get(concept_id, 0), 2),
                "resources": [
                    r["id"] for r in self.resources.values() if concept_id in r["concepts"]
                ],
            }
            for concept_id in ordered
        ]

    def recommend(self, profile: dict, limit: int = 6) -> list[Recommendation]:
        mastery = {key: float(value) for key, value in profile.get("mastery", {}).items()}
        goals = [goal for goal in profile.get("goals", []) if goal in self.concepts]
        preferred_format = profile.get("preferredFormat", "any")
        preferred_level = profile.get("preferredLevel", "intermediate")
        completed = set(profile.get("completedResources", []))

        relevant = set(goals) | self.prerequisite_closure(goals)
        level_rank = {"beginner": 1, "intermediate": 2, "advanced": 3}
        recommendations = []

        for resource in self.resources.values():
            if resource["id"] in completed:
                continue
            taught = set(resource["concepts"])
            overlap = taught & relevant
            if goals and not overlap:
                continue

            score = 0.0
            reasons = []
            direct_goals = taught & set(goals)
            if direct_goals:
                score += 4.0 * len(direct_goals)
                reasons.append("Directly supports your selected goal")
            prerequisite_topics = overlap - set(goals)
            if prerequisite_topics:
                score += 2.4 * len(prerequisite_topics)
                reasons.append("Builds a prerequisite needed for your goal")

            knowledge_gap = sum(1 - mastery.get(concept_id, 0) for concept_id in taught) / len(taught)
            score += knowledge_gap * 2.5
            if knowledge_gap > 0.5:
                reasons.append("Targets a high-priority knowledge gap")

            if preferred_format == "any" or resource["format"] == preferred_format:
                score += 1.0
                if preferred_format != "any":
                    reasons.append(f"Matches your preferred {preferred_format} format")

            distance = abs(level_rank[resource["level"]] - level_rank.get(preferred_level, 2))
            score += max(0, 1.2 - distance * 0.6)
            if distance == 0:
                reasons.append("Matches your preferred difficulty")

            required = self.prerequisite_closure(list(taught))
            missing = [self.concepts[c] for c in required if mastery.get(c, 0) < 0.45]
            score -= len(missing) * 0.8
            if missing:
                reasons.append("Best taken after the listed prerequisite topics")

            recommendations.append(
                Recommendation(
                    resource=resource,
                    score=score,
                    reasons=reasons[:3],
                    concepts=[self.concepts[c] for c in resource["concepts"]],
                    missing_prerequisites=missing,
                )
            )

        return sorted(recommendations, key=lambda item: (-item.score, item.resource["title"]))[:limit]

    def triples(self) -> list[tuple[str, str, str]]:
        triples = []
        for concept in self.concepts.values():
            subject = f"learn:{concept['id']}"
            triples.extend(
                [(subject, "rdf:type", "learn:Concept"), (subject, "rdfs:label", concept["label"])]
            )
            triples.extend((subject, "learn:requires", f"learn:{p}") for p in concept.get("prerequisites", []))
        for resource in self.resources.values():
            subject = f"learn:{resource['id']}"
            triples.append((subject, "rdf:type", "learn:LearningResource"))
            triples.append((subject, "rdfs:label", resource["title"]))
            triples.extend((subject, "learn:teaches", f"learn:{c}") for c in resource["concepts"])
        return triples
