"""Flask entry point for the Semantic Learning Assistant."""

from __future__ import annotations

import re
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file

from learning_graph import LearningKnowledgeGraph

BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__)
graph = LearningKnowledgeGraph(BASE_DIR / "data" / "catalog.json")


@app.get("/")
def index():
    return render_template("index.html", concepts=list(graph.concepts.values()), overview=graph.overview())


@app.get("/api/graph")
def get_graph():
    return jsonify(graph.concept_graph())


@app.get("/api/overview")
def get_overview():
    return jsonify(graph.overview())


@app.post("/api/recommendations")
def recommendations():
    profile = request.get_json(silent=True) or {}
    return jsonify([item.as_dict() for item in graph.recommend(profile)])


@app.post("/api/learning-path")
def learning_path():
    profile = request.get_json(silent=True) or {}
    return jsonify(graph.learning_path(profile.get("goal", ""), profile.get("mastery", {})))


@app.get("/api/search")
def search():
    query = request.args.get("q", "").strip().lower()
    if not query:
        return jsonify([])
    results = []
    for concept in graph.concepts.values():
        haystack = " ".join([concept["label"], concept["description"], concept["domain"]]).lower()
        if query in haystack:
            results.append({"type": "concept", **concept})
    for resource in graph.resources.values():
        haystack = " ".join([resource["title"], resource["description"], resource["format"]]).lower()
        if query in haystack:
            results.append({"type": "resource", **resource})
    return jsonify(results[:12])


@app.post("/api/sparql")
def sparql():
    """Run read-only SPARQL when RDFLib is installed.

    The endpoint intentionally permits SELECT and ASK only; it is an educational
    graph explorer, not a general update endpoint.
    """
    query = (request.get_json(silent=True) or {}).get("query", "").strip()
    if not re.match(r"^(PREFIX\s+[^\n]+\s*)*(SELECT|ASK)\b", query, re.IGNORECASE):
        return jsonify({"error": "Only SELECT and ASK queries are allowed."}), 400
    try:
        from rdflib import Graph
    except ImportError:
        return jsonify({"error": "Install RDFLib from requirements.txt to enable SPARQL."}), 503

    rdf_graph = Graph()
    rdf_graph.parse(BASE_DIR / "ontology.ttl", format="turtle")
    try:
        result = rdf_graph.query(query)
    except Exception as exc:
        return jsonify({"error": f"Invalid query: {exc}"}), 400
    if result.type == "ASK":
        return jsonify({"boolean": bool(result.askAnswer)})
    variables = [str(item) for item in result.vars]
    rows = [{variables[i]: str(value) if value is not None else None for i, value in enumerate(row)} for row in result]
    return jsonify({"variables": variables, "rows": rows, "count": len(rows)})


@app.get("/ontology")
def ontology():
    return send_file(BASE_DIR / "ontology.ttl", mimetype="text/turtle", download_name="learning-ontology.ttl")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
