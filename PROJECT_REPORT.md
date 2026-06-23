# Semantic Web-Based Personalized Learning Assistant Using Knowledge Graphs

## Abstract

This project presents a personalized learning assistant that uses semantic web principles and a knowledge graph to recommend learning resources. Traditional e-learning systems often show the same content list to every learner. This project improves that experience by representing concepts, prerequisite relationships, learning resources and learner goals as connected knowledge. The assistant generates an adaptive learning path and explains why each resource is recommended.

## Problem Statement

Learners studying technical subjects often struggle to decide what to learn next. A beginner may jump into advanced content without the necessary prerequisites, while an advanced learner may waste time revisiting topics they already know. The problem is to design a system that can understand the structure of a subject domain and personalize learning recommendations based on each learner's current knowledge and goals.

## Objectives

- Build a knowledge graph for semantic web topics and learning resources.
- Represent concepts, prerequisites and resources using RDF/OWL-style semantics.
- Accept a learner profile containing goals, mastery and preferences.
- Recommend suitable learning resources with clear explanations.
- Generate a prerequisite-aware learning path.
- Provide a web interface suitable for demonstration and evaluation.

## System Architecture

The system has four main layers:

1. Knowledge layer: `ontology.ttl` defines classes such as `Concept`, `LearningResource` and `Learner`, with properties such as `requires`, `teaches` and `hasGoal`.
2. Data layer: `data/catalog.json` stores the demo concept map and resources used by the application.
3. Recommendation layer: `learning_graph.py` computes prerequisite closure, learning paths and explainable resource scores.
4. Presentation layer: Flask routes serve the dashboard and JSON APIs consumed by the browser.

## Knowledge Graph Design

The graph contains concepts including Web Fundamentals, RDF, Turtle, RDFS, OWL, SPARQL, Knowledge Graph Design and Explainable Recommendations. Prerequisite edges encode the learning dependency structure. Resource edges connect articles, labs, videos and interactive lessons to the concepts they teach.

Important relations include:

- `learn:requires`: a concept requires another concept.
- `learn:teaches`: a learning resource teaches a concept.
- `learn:hasGoal`: a learner wants to master a concept.
- `learn:hasMastery`: a learner's current mastery level.

## Recommendation Method

The recommendation engine ranks resources using:

- Direct relevance to the selected learning goal.
- Relevance to missing prerequisites of the goal.
- Learner mastery gaps for the taught concepts.
- Match with preferred content format.
- Match with preferred difficulty level.
- Penalty when important prerequisites are weak.

Each recommendation includes reasons such as "Directly supports your selected goal" or "Builds a prerequisite needed for your goal". This makes the system explainable and aligns with the semantic web goal of transparent machine-understandable knowledge.

## Modules

- `app.py`: Defines the Flask web server, API endpoints, ontology download route and optional SPARQL endpoint.
- `learning_graph.py`: Loads the catalog, computes prerequisite closure and generates recommendations.
- `ontology.ttl`: Provides semantic classes, properties and example individuals.
- `templates/index.html`: Contains the dashboard layout.
- `static/app.js`: Calls APIs and renders recommendations, paths and graph nodes.
- `static/style.css`: Provides responsive styling for the demo.

## Sample User Flow

1. The learner selects "Explainable Recommendations" as the learning goal.
2. The learner sets low mastery for SPARQL and Knowledge Graph Design.
3. The assistant finds prerequisite concepts such as RDF, RDFS and SPARQL.
4. The assistant recommends resources such as SPARQL Query Playground and Knowledge Graph Architecture.
5. The interface explains which resources fill prerequisite gaps and which directly support the goal.

## Advantages

- Better personalization than a static course list.
- Transparent recommendations through semantic graph explanations.
- Extensible ontology that can support more subjects and learner attributes.
- Lightweight implementation suitable for classroom demonstration.

## Limitations

- The sample dataset is intentionally small for clarity.
- Learner mastery is manually entered instead of inferred from quizzes.
- Advanced OWL reasoning is not required for the core demo, though the ontology can support future reasoning extensions.

## Future Enhancements

- Add login-based learner profiles and persistent progress history.
- Include quiz results to update mastery automatically.
- Integrate a full RDF triple store such as Apache Jena Fuseki.
- Add reasoning rules for detecting equivalent concepts and inferred prerequisites.
- Connect resources to external linked open data using DBpedia or Wikidata identifiers.

## Conclusion

The project demonstrates how semantic web technologies and knowledge graphs can make personalized learning more structured, adaptive and explainable. By modeling both subject knowledge and learner needs, the assistant can recommend meaningful next steps instead of simply listing popular content.
