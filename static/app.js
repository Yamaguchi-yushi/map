/* ═══════════════════════════════════════════════════════════
   Map Visualizer — Frontend Logic
   ═══════════════════════════════════════════════════════════ */

// ── State ────────────────────────────────────────────────
let state = {
  maps: [],           // [{name, nodes, edges}]
  selectedMap: null,   // currently selected map name
  mapInfo: null,       // {name, nodes:[{id,x,y,station}], edges:[{from,to}]}
};

// Preset colors for quick selection (matching make_graph)
const PRESET_COLORS = [
  "#87CEEB", "#FF6B6B", "#4ECDC4", "#45B7D1", "#F9CA24",
  "#6C5CE7", "#A8E6CF", "#FD79A8", "#00B894", "#E17055",
  "#666666", "#333333", "#999999", "#CCCCCC", "#F1F5F9"
];

// ── Helpers ──────────────────────────────────────────────
function toast(msg, type = "info") {
  const el = document.createElement("div");
  el.className = `toast ${type}`;
  el.textContent = msg;
  document.getElementById("toast-container").appendChild(el);
  setTimeout(() => { el.style.opacity = "0"; setTimeout(() => el.remove(), 300); }, 3000);
}

function togglePanel(id) {
  const el = document.getElementById(id);
  const chevron = document.getElementById(id + "-chevron");
  el.classList.toggle("collapsed");
  if (chevron) chevron.classList.toggle("collapsed");
}

function getParams() {
  const goalStr = document.getElementById("param-goal-nodes").value.trim();
  let goalNodes = [];
  if (goalStr) {
    goalNodes = goalStr.split(",").map(s => parseInt(s.trim())).filter(n => !isNaN(n));
  }

  return {
    node_size: parseInt(document.getElementById("param-node-size").value) || 150,
    font_size: parseInt(document.getElementById("param-font-size").value) || 10,
    width: parseFloat(document.getElementById("param-width").value) || 10,
    height: parseFloat(document.getElementById("param-height").value) || 6,
    line_width: parseFloat(document.getElementById("param-line-width").value) || 1.0,
    edge_alpha: parseFloat(document.getElementById("param-edge-alpha").value) || 0.7,
    node_color: document.getElementById("param-node-color").value,
    edge_color: document.getElementById("param-edge-color").value,
    dpi: parseInt(document.getElementById("param-dpi").value) || 300,
    show_labels: document.getElementById("param-labels").checked,
    show_edges: document.getElementById("param-edges").checked,
    transparent: document.getElementById("param-transparent").checked,
    show_station: document.getElementById("param-station").checked,
    show_title: document.getElementById("param-title").checked,
    show_edge_weights: document.getElementById("param-edge-weights").checked,
    edge_weight_font_size: parseInt(document.getElementById("param-edge-weight-font").value) || 7,
    goal_nodes: goalNodes,
  };
}

// ── Fetch available maps ─────────────────────────────────
async function fetchMaps() {
  try {
    const res = await fetch("/api/maps");
    const data = await res.json();
    state.maps = data.maps;
    renderMapSelect();
  } catch (e) {
    toast(`マップ一覧の取得に失敗しました: ${e.message}`, "error");
  }
}

function renderMapSelect() {
  const select = document.getElementById("map-select");
  select.innerHTML = '<option value="">-- マップを選択 --</option>';
  state.maps.forEach(m => {
    const opt = document.createElement("option");
    opt.value = m.name;
    opt.textContent = `${m.name}  (${m.nodes} nodes, ${m.edges} edges)`;
    select.appendChild(opt);
  });
}

// ── Map Selection ────────────────────────────────────────
async function onMapSelected(mapName) {
  if (!mapName) {
    state.selectedMap = null;
    state.mapInfo = null;
    document.getElementById("map-info").style.display = "none";
    document.getElementById("current-map-name").textContent = "マップ未選択";
    renderNodeList();
    showPlaceholder();
    return;
  }

  state.selectedMap = mapName;
  document.getElementById("current-map-name").textContent = mapName;

  // Fetch map info
  try {
    const res = await fetch(`/api/map-info/${mapName}`);
    const data = await res.json();
    state.mapInfo = data;

    // Update badges
    document.getElementById("badge-nodes").textContent = `${data.nodes.length} nodes`;
    document.getElementById("badge-edges").textContent = `${data.edges.length} edges`;
    document.getElementById("map-info").style.display = "block";

    renderNodeList();
  } catch (e) {
    toast(`マップ情報の取得に失敗: ${e.message}`, "error");
  }

  // Render map
  await renderMap();
}

// ── Render Node List ─────────────────────────────────────
function renderNodeList() {
  const list = document.getElementById("node-list");
  list.innerHTML = "";

  if (!state.mapInfo || !state.mapInfo.nodes) {
    list.innerHTML = '<div class="empty-state"><p>マップを選択するとノード一覧が表示されます</p></div>';
    return;
  }

  const goalStr = document.getElementById("param-goal-nodes").value.trim();
  const goalNodes = goalStr ? goalStr.split(",").map(s => parseInt(s.trim())).filter(n => !isNaN(n)) : [];

  state.mapInfo.nodes.forEach(node => {
    const item = document.createElement("div");
    const isGoal = goalNodes.includes(node.id);
    const isStation = node.station === 1;
    item.className = `node-item ${isGoal ? "goal" : ""} ${isStation && !isGoal ? "station" : ""}`;

    const idBadge = document.createElement("span");
    idBadge.className = `node-id ${isGoal ? "goal-node" : isStation ? "station-node" : ""}`;
    idBadge.textContent = node.id;

    const coords = document.createElement("span");
    coords.className = "node-coords";
    coords.textContent = `(${node.x}, ${node.y})`;

    item.appendChild(idBadge);
    item.appendChild(coords);

    if (isGoal) {
      const tag = document.createElement("span");
      tag.className = "node-tag goal-tag";
      tag.textContent = "GOAL";
      item.appendChild(tag);
    } else if (isStation) {
      const tag = document.createElement("span");
      tag.className = "node-tag station-tag";
      tag.textContent = "STATION";
      item.appendChild(tag);
    }

    // Click to toggle goal node
    item.onclick = () => {
      toggleGoalNode(node.id);
    };

    list.appendChild(item);
  });
}

function toggleGoalNode(nodeId) {
  const input = document.getElementById("param-goal-nodes");
  const goalStr = input.value.trim();
  let goalNodes = goalStr ? goalStr.split(",").map(s => parseInt(s.trim())).filter(n => !isNaN(n)) : [];

  if (goalNodes.includes(nodeId)) {
    goalNodes = goalNodes.filter(n => n !== nodeId);
  } else {
    goalNodes.push(nodeId);
  }

  input.value = goalNodes.join(", ");
  renderNodeList();
  renderMap();
}

// ── Render Map Preview ───────────────────────────────────
let currentPreviewUrl = null;
let renderTimeout = null;

async function renderMap() {
  if (!state.selectedMap) return;

  const wrapper = document.getElementById("preview-wrapper");
  const placeholder = document.getElementById("graph-placeholder");
  const loading = document.getElementById("loading-overlay");
  const params = getParams();

  placeholder.style.display = "none";
  wrapper.style.display = "none";
  loading.style.display = "flex";

  try {
    const res = await fetch("/api/render", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        map_name: state.selectedMap,
        params: params,
      }),
    });

    if (!res.ok) {
      const err = await res.json();
      toast(`描画エラー: ${err.error}`, "error");
      loading.style.display = "none";
      placeholder.style.display = "flex";
      return;
    }

    const blob = await res.blob();
    if (currentPreviewUrl) {
      URL.revokeObjectURL(currentPreviewUrl);
    }
    currentPreviewUrl = URL.createObjectURL(blob);
    document.getElementById("map-preview").src = currentPreviewUrl;

    loading.style.display = "none";
    wrapper.style.display = "flex";
  } catch (e) {
    toast(`描画失敗: ${e.message}`, "error");
    loading.style.display = "none";
    placeholder.style.display = "flex";
  }
}

function showPlaceholder() {
  document.getElementById("preview-wrapper").style.display = "none";
  document.getElementById("loading-overlay").style.display = "none";
  document.getElementById("graph-placeholder").style.display = "flex";
}

// Debounced render for input changes
function debouncedRender() {
  if (renderTimeout) clearTimeout(renderTimeout);
  renderTimeout = setTimeout(() => {
    if (state.selectedMap) renderMap();
  }, 300);
}

// ── Export ────────────────────────────────────────────────
async function exportMap(format) {
  if (!state.selectedMap) {
    toast("マップが選択されていません", "error");
    return;
  }

  const params = getParams();
  toast(`${format.toUpperCase()} エクスポート中...`, "info");

  try {
    const res = await fetch("/api/export", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        map_name: state.selectedMap,
        format: format,
        params: params,
      }),
    });

    if (!res.ok) {
      const err = await res.json();
      toast(`エクスポートエラー: ${err.error}`, "error");
      return;
    }

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    const parts = [state.selectedMap];
    const goalNodes = params.goal_nodes;
    if (goalNodes.length > 0) {
      parts.push("goal_" + goalNodes.join("_"));
    }
    parts.push(`${Math.round(params.width)}x${Math.round(params.height)}`);
    a.download = parts.join("_") + `.${format}`;
    a.click();
    URL.revokeObjectURL(url);
    toast(`${format.toUpperCase()} をダウンロードしました`, "success");
  } catch (e) {
    toast(`エクスポート失敗: ${e.message}`, "error");
  }
}

// ── Init Color Presets ───────────────────────────────────
function initColorPresets() {
  const createSwatches = (containerId, inputId) => {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    PRESET_COLORS.forEach(color => {
      const swatch = document.createElement("div");
      swatch.className = "color-preset-swatch";
      swatch.style.backgroundColor = color;
      swatch.title = color;
      swatch.onclick = () => {
        document.getElementById(inputId).value = color;
        debouncedRender();
      };
      container.appendChild(swatch);
    });
  };

  createSwatches("node-color-presets", "param-node-color");
  createSwatches("edge-color-presets", "param-edge-color");
}

// ── Event Listeners ──────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  // Init color presets
  initColorPresets();

  // Load maps
  fetchMaps();

  // Map selection
  document.getElementById("map-select").addEventListener("change", (e) => {
    onMapSelected(e.target.value);
  });

  // Settings changes → re-render
  const settingsInputs = document.querySelectorAll("#settings-content input");
  settingsInputs.forEach(el => {
    const evts = el.type === "checkbox" ? ["change"] : ["change", "input"];
    evts.forEach(evt => el.addEventListener(evt, () => {
      // Update node list for goal node highlighting
      renderNodeList();
      debouncedRender();
    }));
  });

  // Show/hide edge weight font size row
  document.getElementById("param-edge-weights").addEventListener("change", (e) => {
    document.getElementById("edge-weight-font-row").style.display = e.target.checked ? "flex" : "none";
  });
  document.getElementById("param-edge-weight-font").addEventListener("input", () => {
    debouncedRender();
  });

  // Goal node input change → update node list and re-render
  document.getElementById("param-goal-nodes").addEventListener("input", () => {
    renderNodeList();
    debouncedRender();
  });
});
