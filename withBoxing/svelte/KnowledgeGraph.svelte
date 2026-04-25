<script>
  import { onMount } from 'svelte';
  import * as d3 from 'd3';

  export let url = '/graph.json';
  export let width = 1100;
  export let height = 720;

  let svgEl;
  let graph = { nodes: [], edges: [] };
  let selected = null;
  let query = '';

  $: visibleNodes = graph.nodes.filter(n => !query || JSON.stringify(n).toLowerCase().includes(query.toLowerCase()));
  $: visibleIds = new Set(visibleNodes.map(n => n.id));
  $: visibleEdges = graph.edges.filter(e => visibleIds.has(e.source?.id ?? e.source) && visibleIds.has(e.target?.id ?? e.target));

  onMount(async () => {
    graph = await fetch(url).then(r => r.json());
    draw();
  });

  $: if (svgEl && graph.nodes.length) draw();

  function draw() {
    const svg = d3.select(svgEl);
    svg.selectAll('*').remove();

    const nodes = visibleNodes.map(d => ({ ...d }));
    const edges = visibleEdges.map(d => ({ ...d }));

    const sim = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(edges).id(d => d.id).distance(95))
      .force('charge', d3.forceManyBody().strength(-320))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collide', d3.forceCollide(34));

    const edge = svg.append('g').attr('stroke-opacity', 0.55)
      .selectAll('line').data(edges).join('line').attr('stroke-width', 1.4);

    const edgeLabel = svg.append('g').selectAll('text').data(edges).join('text')
      .attr('font-size', 9).attr('opacity', 0.7).text(d => d.type);

    const node = svg.append('g').selectAll('g').data(nodes).join('g')
      .attr('cursor', 'pointer')
      .call(d3.drag()
        .on('start', (event, d) => { if (!event.active) sim.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
        .on('drag', (event, d) => { d.fx = event.x; d.fy = event.y; })
        .on('end', (event, d) => { if (!event.active) sim.alphaTarget(0); d.fx = null; d.fy = null; }));

    node.append('circle').attr('r', d => d.kind === 'Document' ? 18 : d.kind === 'Excerpt' ? 13 : 10)
      .attr('class', d => `node node-${String(d.kind).toLowerCase()}`);
    node.append('text').attr('x', 13).attr('y', 4).attr('font-size', 11).text(d => d.label ?? d.id);
    node.on('click', (_, d) => selected = d);

    sim.on('tick', () => {
      edge.attr('x1', d => d.source.x).attr('y1', d => d.source.y).attr('x2', d => d.target.x).attr('y2', d => d.target.y);
      edgeLabel.attr('x', d => (d.source.x + d.target.x) / 2).attr('y', d => (d.source.y + d.target.y) / 2);
      node.attr('transform', d => `translate(${d.x},${d.y})`);
    });
  }
</script>

<div class="toolbar">
  <input placeholder="Suche in Knoten..." bind:value={query} />
  <span>{visibleNodes.length} Knoten / {visibleEdges.length} Kanten</span>
</div>

<div class="wrap">
  <svg bind:this={svgEl} {width} {height}></svg>
  {#if selected}
    <aside>
      <h3>{selected.label}</h3>
      <code>{selected.kind}</code>
      <pre>{JSON.stringify(selected, null, 2)}</pre>
    </aside>
  {/if}
</div>

<style>
  .toolbar { display:flex; gap:1rem; align-items:center; margin-bottom:.75rem; font-family:system-ui; }
  input { padding:.55rem .7rem; border:1px solid #ccc; border-radius:8px; min-width:280px; }
  .wrap { display:flex; gap:1rem; }
  svg { border:1px solid #ddd; border-radius:12px; background:#fff; }
  :global(.node) { fill: #f8f8f8; stroke:#222; stroke-width:1.4; }
  :global(.node-document) { stroke-width:2.5; }
  :global(.node-excerpt) { stroke-dasharray:3 2; }
  line { stroke:#555; }
  aside { width:360px; font-family:system-ui; border:1px solid #ddd; border-radius:12px; padding:1rem; overflow:auto; max-height:720px; }
  pre { white-space:pre-wrap; font-size:12px; }
</style>
