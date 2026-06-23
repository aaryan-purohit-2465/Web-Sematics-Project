const $ = (selector) => document.querySelector(selector);

function profileFromForm() {
  const mastery = {};
  document.querySelectorAll('[data-concept]').forEach((slider) => {
    mastery[slider.dataset.concept] = Number(slider.value);
  });
  return {
    goals: [$('#goal').value],
    goal: $('#goal').value,
    preferredFormat: $('#format').value,
    preferredLevel: $('#level').value,
    mastery,
    completedResources: []
  };
}

function resourceCard(item) {
  const missing = item.missingPrerequisites.length
    ? `<p><strong>Prerequisite warning:</strong> ${item.missingPrerequisites.map((c) => c.label).join(', ')}</p>`
    : '';
  return `
    <article class="resource-card">
      <header>
        <div>
          <h3>${item.resource.title}</h3>
          <p>${item.resource.description}</p>
        </div>
        <span class="pill">Score ${item.score}</span>
      </header>
      <div class="tags">
        <span class="tag">${item.resource.format}</span>
        <span class="tag">${item.resource.level}</span>
        <span class="tag">${item.resource.duration} min</span>
        ${item.concepts.map((c) => `<span class="tag">${c.label}</span>`).join('')}
      </div>
      ${missing}
      <ul class="reasons">${item.reasons.map((reason) => `<li>${reason}</li>`).join('')}</ul>
    </article>`;
}

async function refreshRecommendations() {
  const profile = profileFromForm();
  const [recommendations, path] = await Promise.all([
    fetch('/api/recommendations', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(profile)
    }).then((res) => res.json()),
    fetch('/api/learning-path', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(profile)
    }).then((res) => res.json())
  ]);

  $('#recommendations').innerHTML = recommendations.length
    ? recommendations.map(resourceCard).join('')
    : '<p>No recommendation found. Try choosing a broader goal.</p>';

  $('#path').innerHTML = path.length
    ? path.map((concept) => `<li><strong>${concept.label}</strong><p>${concept.description} Mastery: ${Math.round(concept.mastery * 100)}%</p></li>`).join('')
    : '<li>The chosen goal already appears mastered.</li>';
}

function drawGraph(data) {
  const canvas = $('#graph-canvas');
  const rect = canvas.getBoundingClientRect();
  const width = Math.max(rect.width, 700);
  const height = Math.max(rect.height, 420);
  const levels = { beginner: 0.18, intermediate: 0.5, advanced: 0.82 };
  const byLevel = data.nodes.reduce((acc, node) => {
    acc[node.level] = acc[node.level] || [];
    acc[node.level].push(node);
    return acc;
  }, {});
  const positions = {};
  Object.entries(byLevel).forEach(([level, nodes]) => {
    nodes.forEach((node, index) => {
      positions[node.id] = {
        x: width * levels[level],
        y: height * ((index + 1) / (nodes.length + 1))
      };
    });
  });
  canvas.innerHTML = data.links.map((link) => {
    const a = positions[link.source];
    const b = positions[link.target];
    const length = Math.hypot(b.x - a.x, b.y - a.y);
    const angle = Math.atan2(b.y - a.y, b.x - a.x) * 180 / Math.PI;
    return `<div class="edge" style="left:${a.x}px;top:${a.y}px;width:${length}px;transform:rotate(${angle}deg)"></div>`;
  }).join('') + data.nodes.map((node) => {
    const pos = positions[node.id];
    return `<div class="node" title="${node.domain}" style="left:${pos.x}px;top:${pos.y}px">${node.label}</div>`;
  }).join('');
}

async function loadGraph() {
  const data = await fetch('/api/graph').then((res) => res.json());
  drawGraph(data);
}

async function runSparql() {
  const output = $('#sparql-output');
  output.textContent = 'Running query...';
  const response = await fetch('/api/sparql', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: $('#sparql-query').value })
  });
  const payload = await response.json();
  output.textContent = JSON.stringify(payload, null, 2);
}

$('#profile-form').addEventListener('submit', (event) => {
  event.preventDefault();
  refreshRecommendations();
});
$('#run-sparql').addEventListener('click', runSparql);
window.addEventListener('resize', loadGraph);

refreshRecommendations();
loadGraph();
