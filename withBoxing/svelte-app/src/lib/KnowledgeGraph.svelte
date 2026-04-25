<script>
  import { onMount } from 'svelte';
  import * as d3 from 'd3';

  export let url = '/graph.json';

  let svgEl;
  let graphPanelEl;
  let graphWidth = 0;
  let graphHeight = 0;
  let graph = { nodes: [], edges: [] };
  let selected = null;
  let query = '';
  let view = { x: 0, y: 0, scale: 1, angle: 0 };

  $: visibleNodes = graph.nodes.filter(n => !query || JSON.stringify(n).toLowerCase().includes(query.toLowerCase()));
  $: visibleIds = new Set(visibleNodes.map(n => n.id));
  $: visibleEdges = graph.edges.filter(e => visibleIds.has(e.source?.id ?? e.source) && visibleIds.has(e.target?.id ?? e.target));
  $: width = Math.max(320, graphWidth || 0);
  $: height = Math.max(320, graphHeight || 0);
  $: if (svgEl) applyViewTransform();

  onMount(async () => {
    graph = await fetch(url).then(r => r.json());
    draw();
  });

  $: if (svgEl && graph.nodes.length && width && height && visibleNodes && visibleEdges) draw();

  function viewTransform() {
    return `translate(${width / 2 + view.x},${height / 2 + view.y}) scale(${view.scale}) rotate(${view.angle}) translate(${-width / 2},${-height / 2})`;
  }

  function applyViewTransform() {
    d3.select(svgEl).select('.viewport').attr('transform', viewTransform());
  }

  function screenToWorld(screenX, screenY, nextScale = view.scale) {
    const cx = width / 2 + view.x;
    const cy = height / 2 + view.y;
    const angle = -view.angle * Math.PI / 180;
    const dx = (screenX - cx) / view.scale;
    const dy = (screenY - cy) / view.scale;
    return {
      x: Math.cos(angle) * dx - Math.sin(angle) * dy + width / 2,
      y: Math.sin(angle) * dx + Math.cos(angle) * dy + height / 2,
      nextScale
    };
  }

  function handleWheel(event) {
    event.preventDefault();
    const rect = svgEl.getBoundingClientRect();
    const px = event.clientX - rect.left;
    const py = event.clientY - rect.top;
    const before = screenToWorld(px, py);
    const nextScale = Math.max(0.18, Math.min(6, view.scale * Math.exp(-event.deltaY * 0.0014)));
    const angle = view.angle * Math.PI / 180;
    const worldDx = before.x - width / 2;
    const worldDy = before.y - height / 2;
    const rotatedX = Math.cos(angle) * worldDx - Math.sin(angle) * worldDy;
    const rotatedY = Math.sin(angle) * worldDx + Math.cos(angle) * worldDy;

    view = {
      ...view,
      scale: nextScale,
      x: px - width / 2 - rotatedX * nextScale,
      y: py - height / 2 - rotatedY * nextScale
    };
  }

  function startViewDrag(event) {
    if (event.button !== 0 && event.button !== 2) return;
    if (event.target.closest('.node-hit')) return;

    event.preventDefault();
    const mode = event.button === 2 ? 'pan' : 'rotate';
    const start = { x: event.clientX, y: event.clientY, view: { ...view } };

    const move = (moveEvent) => {
      const dx = moveEvent.clientX - start.x;
      const dy = moveEvent.clientY - start.y;

      if (mode === 'pan') {
        view = { ...start.view, x: start.view.x + dx, y: start.view.y + dy };
      } else {
        view = { ...start.view, angle: start.view.angle + dx * 0.28 + dy * 0.08 };
      }
    };

    const stop = () => {
      window.removeEventListener('pointermove', move);
      window.removeEventListener('pointerup', stop);
    };

    window.addEventListener('pointermove', move);
    window.addEventListener('pointerup', stop);
  }

  function nodeLabel(d) {
    const label = d.label ?? d.id;
    if (d.kind === 'Class' && label.length > 24) return `${label.slice(0, 23)}...`;
    if (d.kind === 'Synonym' && label.length > 16) return `${label.slice(0, 15)}...`;
    return label;
  }

  function edgeClass(d) {
    if (d.layer === 'TBox') return 'edge-tbox';
    if (d.layer === 'ABox_to_TBox') return 'edge-classification';
    return 'edge-abox';
  }

  function draw() {
    const svg = d3.select(svgEl);
    svg.selectAll('*').remove();

    const nodes = visibleNodes.map(d => ({ ...d }));
    const edges = visibleEdges.map(d => ({ ...d }));

    const sim = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(edges).id(d => d.id).distance(d => d.layer === 'TBox' ? 78 : d.layer === 'ABox_to_TBox' ? 120 : 105))
      .force('charge', d3.forceManyBody().strength(-320))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collide', d3.forceCollide(34));

    const viewport = svg.append('g').attr('class', 'viewport').attr('transform', viewTransform());

    const edge = viewport.append('g').attr('stroke-opacity', 0.55)
      .selectAll('line').data(edges).join('line')
      .attr('stroke-width', d => d.layer === 'TBox' ? 2 : 1.4)
      .attr('class', edgeClass);

    const edgeLabel = viewport.append('g').selectAll('text').data(edges).join('text')
      .attr('font-size', 9).attr('opacity', 0.7).text(d => d.type);

    const node = viewport.append('g').selectAll('g').data(nodes).join('g')
      .attr('class', 'node-hit')
      .attr('cursor', 'pointer');

    node.filter(d => d.kind === 'Class')
      .append('rect')
      .attr('x', -75)
      .attr('y', -17)
      .attr('width', 150)
      .attr('height', 34)
      .attr('rx', 6)
      .attr('class', 'node node-class');

    node.filter(d => d.kind === 'Synonym')
      .append('rect')
      .attr('x', -48)
      .attr('y', -13)
      .attr('width', 96)
      .attr('height', 26)
      .attr('rx', 4)
      .attr('class', 'node node-synonym');

    node.filter(d => d.kind !== 'Class' && d.kind !== 'Synonym')
      .append('circle')
      .attr('r', d => d.kind === 'Document' ? 18 : d.kind === 'Excerpt' ? 13 : 10)
      .attr('class', d => `node node-${String(d.kind).toLowerCase()}`);

    node.append('text')
      .attr('text-anchor', d => d.kind === 'Class' || d.kind === 'Synonym' ? 'middle' : 'start')
      .attr('x', d => d.kind === 'Class' || d.kind === 'Synonym' ? 0 : 13)
      .attr('y', 4)
      .attr('font-size', d => d.kind === 'Class' ? 10 : 11)
      .text(nodeLabel);
    node.on('click', (_, d) => selected = d);

    sim.on('tick', () => {
      viewport.attr('transform', viewTransform());
      edge.attr('x1', d => d.source.x).attr('y1', d => d.source.y).attr('x2', d => d.target.x).attr('y2', d => d.target.y);
      edgeLabel.attr('x', d => (d.source.x + d.target.x) / 2).attr('y', d => (d.source.y + d.target.y) / 2);
      node.attr('transform', d => `translate(${d.x},${d.y})`);
    });
  }
</script>

<div class="app-shell">
  <div class="toolbar">
    <input placeholder="Suche in Knoten..." bind:value={query} />
    <span>{visibleNodes.length} Knoten / {visibleEdges.length} Kanten</span>
  </div>

  <div class="wrap">
    <div class="graph-panel" bind:this={graphPanelEl} bind:clientWidth={graphWidth} bind:clientHeight={graphHeight}>
      <svg
        bind:this={svgEl}
        {width}
        {height}
        role="application"
        aria-label="Interaktiver Knowledge Graph"
        on:pointerdown={startViewDrag}
        on:wheel={handleWheel}
        on:contextmenu|preventDefault
      ></svg>
    </div>
    {#if selected}
      <aside>
        <h3>{selected.label}</h3>
        <code>{selected.kind}</code>
        <pre>{JSON.stringify(selected, null, 2)}</pre>
      </aside>
    {/if}
  </div>
</div>

<style>
  :global(html), :global(body), :global(#app) { height:100%; margin:0; }
  :global(body) { overflow:hidden; }
  :global(*) { box-sizing:border-box; }
  .app-shell { height:100%; display:flex; flex-direction:column; padding:.5rem; font-family:system-ui; }
  .toolbar { display:flex; gap:1rem; align-items:center; margin-bottom:.5rem; flex:0 0 auto; }
  input { padding:.55rem .7rem; border:1px solid #ccc; border-radius:8px; min-width:280px; }
  .wrap { display:flex; gap:.75rem; flex:1 1 auto; min-height:0; }
  .graph-panel { flex:1 1 auto; min-width:0; min-height:0; }
  svg { width:100%; height:100%; display:block; border:1px solid #ddd; border-radius:8px; background:#fff; touch-action:none; user-select:none; }
  :global(.node) { fill: #f8f8f8; stroke:#222; stroke-width:1.4; }
  :global(.node-document) { stroke-width:2.5; }
  :global(.node-excerpt) { stroke-dasharray:3 2; }
  :global(.node-class) { fill:#e8f3ef; stroke:#116149; stroke-width:1.8; }
  :global(.node-synonym) { fill:#fff4d8; stroke:#9a6b00; stroke-width:1.4; stroke-dasharray:4 2; }
  :global(line) { stroke:#555; }
  :global(.edge-tbox) { stroke:#116149; }
  :global(.edge-classification) { stroke:#7aa897; stroke-dasharray:3 3; }
  :global(.edge-abox) { stroke:#555; }
  aside { flex:0 0 clamp(320px, 26vw, 460px); border:1px solid #ddd; border-radius:8px; padding:1rem; overflow:auto; min-height:0; }
  pre { white-space:pre-wrap; font-size:12px; }
</style>
