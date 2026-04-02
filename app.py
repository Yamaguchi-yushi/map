"""
Map Visualizer — Web UI
Flask + NetworkX + Matplotlib によるインタラクティブなマップ描画

機能:
  1. maps/ ディレクトリからマップを自動検出
  2. マップを選択してプレビュー表示
  3. ゴールノード指定、ノードサイズ、フォントサイズ等のカスタマイズ
  4. PNG / PDF エクスポート
"""

import os
import io
import math

from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager, rcParams

# ── Japanese font setup ───────────────────────────────────
_font_found = False
for _name in ["Hiragino Sans", "Hiragino Kaku Gothic Pro",
              "Noto Sans CJK JP", "Yu Gothic", "IPAexGothic", "TakaoPGothic"]:
    if any(_name in f.name for f in font_manager.fontManager.ttflist):
        rcParams["font.family"] = _name
        _font_found = True
        break

if not _font_found:
    jp_fonts = [f for f in font_manager.fontManager.ttflist
                if any(n in f.name for n in
                       ['Gothic', 'Hiragino', 'Noto', 'IPA', 'Takao', 'Meiryo'])]
    if jp_fonts:
        rcParams["font.family"] = jp_fonts[0].name

rcParams["axes.unicode_minus"] = False

# ── Flask App ─────────────────────────────────────────────
app = Flask(__name__)
MAPS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "maps")


def load_map(map_name):
    """指定されたマップ名のCSVを読み込み、NetworkXグラフを作成"""
    base_dir = os.path.join(MAPS_DIR, map_name)
    node_file = os.path.join(base_dir, "node.csv")
    edge_file = os.path.join(base_dir, "edge.csv")

    if not os.path.exists(node_file) or not os.path.exists(edge_file):
        raise FileNotFoundError(f"マップ '{map_name}' のCSVファイルが見つかりません。")

    node_df = pd.read_csv(node_file)
    edge_df = pd.read_csv(edge_file)

    G = nx.Graph()

    for _, row in node_df.iterrows():
        node_id = int(row["ID(ignored)"])
        station = int(row.get("station", 0)) if "station" in row else 0
        G.add_node(node_id, pos=(float(row["x"]), float(row["y"])), station=station)

    for _, row in edge_df.iterrows():
        G.add_edge(int(row["from"]), int(row["to"]))

    return G


def render_map_to_buf(G, map_name, params, fmt="png"):
    """マップをmatplotlibで描画し、BytesIOバッファに出力"""
    node_size = params.get("node_size", 150)
    font_size = params.get("font_size", 10)
    transparent = params.get("transparent", False)
    show_labels = params.get("show_labels", True)
    show_edges = params.get("show_edges", True)
    show_station = params.get("show_station", False)
    goal_nodes = params.get("goal_nodes", [])
    fig_w = params.get("width", 10)
    fig_h = params.get("height", 6)
    dpi = params.get("dpi", 300)
    line_width = params.get("line_width", 1.0)
    node_color = params.get("node_color", "#87CEEB")  # skyblue
    edge_color = params.get("edge_color", "#666666")
    edge_alpha = params.get("edge_alpha", 0.7)
    show_title = params.get("show_title", False)
    show_edge_weights = params.get("show_edge_weights", False)
    edge_weight_font_size = params.get("edge_weight_font_size", 7)

    pos = nx.get_node_attributes(G, "pos")

    fig = plt.figure(figsize=(fig_w, fig_h))
    if transparent:
        fig.patch.set_alpha(0)
    ax = plt.gca()
    if transparent:
        ax.patch.set_alpha(0)

    # ゴールノードと通常ノードを分ける
    valid_goal_nodes = [n for n in goal_nodes if n in G.nodes()]
    regular_nodes = [n for n in G.nodes() if n not in valid_goal_nodes]

    # ステーションノードの検出
    station_nodes = []
    if show_station:
        for n in G.nodes():
            if G.nodes[n].get("station", 0) == 1 and n not in valid_goal_nodes:
                station_nodes.append(n)
        regular_nodes = [n for n in regular_nodes if n not in station_nodes]

    # 1. エッジを描画（最背面）
    if show_edges:
        if show_edge_weights:
            # エッジを2分割して中間にギャップを作り、重みテキストを配置
            gap_ratio = 0.12  # 中間ギャップの比率
            for u, v in G.edges():
                x1, y1 = pos[u]
                x2, y2 = pos[v]
                dist = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                # 前半のセグメント
                ax.plot([x1, x1 + (x2 - x1) * (0.5 - gap_ratio)],
                        [y1, y1 + (y2 - y1) * (0.5 - gap_ratio)],
                        color=edge_color, linewidth=line_width, alpha=edge_alpha, zorder=1)
                # 後半のセグメント
                ax.plot([x1 + (x2 - x1) * (0.5 + gap_ratio), x2],
                        [y1 + (y2 - y1) * (0.5 + gap_ratio), y2],
                        color=edge_color, linewidth=line_width, alpha=edge_alpha, zorder=1)
                # 重みテキスト（四角なし）
                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2
                ax.text(mid_x, mid_y, f"{dist:.1f}",
                        fontsize=edge_weight_font_size,
                        ha="center", va="center",
                        color="#333333", zorder=2)
        else:
            nx.draw_networkx_edges(G, pos, width=line_width, alpha=edge_alpha,
                                   edge_color=edge_color)
            # draw_networkx_edges default zorder=1

    # 2. ノードの背面に白塗りの円を描画（エッジが透けて見えないようにするため）
    all_nodes = list(G.nodes())
    nx.draw_networkx_nodes(G, pos, nodelist=all_nodes, node_size=node_size,
                           node_color="white", edgecolors="none")
    # nx.draw_networkx_nodes default zorder=2

    # 3. 通常のノードを描画
    nx.draw_networkx_nodes(G, pos, nodelist=regular_nodes, node_size=node_size,
                           node_color=node_color, edgecolors="black")

    # 4. ステーションノードを描画
    if station_nodes:
        nx.draw_networkx_nodes(G, pos, nodelist=station_nodes, node_size=node_size,
                               node_color="#FFD700", edgecolors="black")

    # 5. ゴールノードを描画
    goal_colors = ["red", "green", "orange", "#E91E63", "#9C27B0"]
    for i, goal_node in enumerate(valid_goal_nodes):
        color = goal_colors[i % len(goal_colors)]
        nx.draw_networkx_nodes(G, pos, nodelist=[goal_node], node_size=node_size,
                               node_color=color, edgecolors="black")

    if show_labels:
        regular_labels = {n: n for n in regular_nodes}
        if station_nodes:
            regular_labels.update({n: n for n in station_nodes})
        nx.draw_networkx_labels(G, pos, labels=regular_labels,
                                font_size=font_size, font_color="black")

        if valid_goal_nodes:
            goal_labels = {n: "G" for n in valid_goal_nodes}
            nx.draw_networkx_labels(G, pos, labels=goal_labels,
                                    font_size=font_size, font_color="white",
                                    font_weight="bold")

    if show_title:
        plt.title(map_name, fontsize=16, fontweight="bold", pad=10)

    plt.axis("equal")
    plt.axis("off")
    plt.tight_layout()

    buf = io.BytesIO()
    save_kwargs = {"bbox_inches": "tight"}
    if fmt == "png":
        save_kwargs["dpi"] = dpi
    if transparent:
        save_kwargs["transparent"] = True
    fig.savefig(buf, format=fmt, **save_kwargs)
    plt.close(fig)
    buf.seek(0)
    return buf


# ── Routes ────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/maps", methods=["GET"])
def list_maps():
    """利用可能なマップを一覧表示"""
    maps = []
    if os.path.exists(MAPS_DIR):
        for name in sorted(os.listdir(MAPS_DIR)):
            map_dir = os.path.join(MAPS_DIR, name)
            if os.path.isdir(map_dir):
                node_file = os.path.join(map_dir, "node.csv")
                edge_file = os.path.join(map_dir, "edge.csv")
                if os.path.exists(node_file) and os.path.exists(edge_file):
                    # ノード数とエッジ数を取得
                    try:
                        node_df = pd.read_csv(node_file)
                        edge_df = pd.read_csv(edge_file)
                        maps.append({
                            "name": name,
                            "nodes": len(node_df),
                            "edges": len(edge_df),
                        })
                    except Exception:
                        maps.append({"name": name, "nodes": 0, "edges": 0})
    return jsonify({"maps": maps})


@app.route("/api/map-info/<map_name>", methods=["GET"])
def get_map_info(map_name):
    """マップの詳細情報（ノード一覧）を返す"""
    try:
        G = load_map(map_name)
        nodes = []
        for n in sorted(G.nodes()):
            data = G.nodes[n]
            nodes.append({
                "id": n,
                "x": round(data["pos"][0], 2),
                "y": round(data["pos"][1], 2),
                "station": data.get("station", 0),
            })
        edges = [{"from": u, "to": v} for u, v in G.edges()]
        return jsonify({
            "name": map_name,
            "nodes": nodes,
            "edges": edges,
        })
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404


@app.route("/api/render", methods=["POST"])
def render_map():
    """マップをレンダリングしてPNG画像を返す"""
    data = request.get_json(force=True)
    map_name = data.get("map_name", "")
    params = data.get("params", {})

    if not map_name:
        return jsonify({"error": "マップ名が指定されていません"}), 400

    try:
        G = load_map(map_name)
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404

    buf = render_map_to_buf(G, map_name, params, fmt="png")

    return send_file(
        buf,
        mimetype="image/png",
        as_attachment=False,
        download_name=f"{map_name}.png",
    )


@app.route("/api/export", methods=["POST"])
def export_map():
    """マップを高品質画像としてエクスポート"""
    data = request.get_json(force=True)
    map_name = data.get("map_name", "")
    fmt = data.get("format", "png")
    params = data.get("params", {})

    if not map_name:
        return jsonify({"error": "マップ名が指定されていません"}), 400

    try:
        G = load_map(map_name)
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404

    buf = render_map_to_buf(G, map_name, params, fmt=fmt)

    mime = {
        "png": "image/png",
        "pdf": "application/pdf",
        "eps": "application/postscript",
    }

    # ファイル名を構築
    parts = [map_name]
    goal_nodes = params.get("goal_nodes", [])
    if goal_nodes:
        parts.append(f"goal_{'_'.join(str(g) for g in goal_nodes)}")
    fig_w = params.get("width", 10)
    fig_h = params.get("height", 6)
    parts.append(f"{int(fig_w)}x{int(fig_h)}")
    download_name = "_".join(parts) + f".{fmt}"

    return send_file(
        buf,
        mimetype=mime.get(fmt, "application/octet-stream"),
        as_attachment=True,
        download_name=download_name,
    )


if __name__ == "__main__":
    app.run(debug=True, port=5051)
