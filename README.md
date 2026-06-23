# Semantic Web-Based Personalized Learning Assistant

An academic-ready web project that uses a knowledge graph to recommend personalized learning resources. The assistant models concepts, prerequisites, resources and learner goals with semantic-web ideas, then explains each recommendation using graph relationships.

## Features

- Knowledge graph of semantic web concepts, prerequisites and learning resources.
- Explainable recommendation engine using goals, mastery, preferred format and difficulty.
- Adaptive learning path generator that orders prerequisites before advanced topics.
- Turtle ontology at `ontology.ttl` with OWL/RDFS vocabulary definitions.
- Optional SPARQL endpoint for querying the ontology when RDFLib is installed.
- Polished Flask dashboard with graph visualization and recommendation cards.
- Tests for learning path ordering, recommendations and graph statistics.

## Tech Stack

- Python 3 and Flask for the web app.
- JSON catalog for demo content and deterministic recommendation logic.
- RDF/Turtle ontology for semantic representation.
- RDFLib for optional live SPARQL querying.
- HTML, CSS and JavaScript for the dashboard.

## Run Locally

```powershell
python -m pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000` in a browser.

If RDFLib is not installed, the main assistant still works; only the SPARQL explorer returns an installation message.

## Run Tests

```powershell
python -m unittest discover -s tests
```

## Project Structure

```text
app.py                    Flask routes and API endpoints
learning_graph.py         Knowledge graph and recommendation engine
data/catalog.json         Concepts and learning resources
ontology.ttl              RDF/OWL ontology and sample triples
templates/index.html      Web dashboard
static/style.css          UI styling
static/app.js             Dashboard interactions
tests/test_learning_graph.py
PROJECT_REPORT.md         Submission-style project explanation
```

## Example SPARQL Query

```sparql
PREFIX learn: <https://example.org/learn#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?resource ?title ?concept WHERE {
  ?resource a learn:LearningResource ;
            rdfs:label ?title ;
            learn:teaches ?concept .
}
```

## Suggested Viva Points

- The graph connects learning resources to concepts and concepts to prerequisites.
- Personalization is based on learner goals, mastery gaps and content preferences.
- Explanations come from graph relations such as `learn:requires` and `learn:teaches`.
- The ontology can be extended with learner history, assessments, Bloom levels and external linked open data.
