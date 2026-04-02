import os
import sys
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

def load_map(map_name):
    """指定されたマップ名のCSVを読み込み、NetworkXグラフを作成"""
    base_dir = os.path.join("maps", map_name)
    node_file = os.path.join(base_dir, "node.csv")
    edge_file = os.path.join(base_dir, "edge.csv")

    if not os.path.exists(node_file) or not os.path.exists(edge_file):
        raise FileNotFoundError(f"指定されたマップ '{map_name}' のCSVファイルが見つかりません。")

    node_df = pd.read_csv(node_file)
    edge_df = pd.read_csv(edge_file)

    G = nx.Graph()

    for _, row in node_df.iterrows():
        node_id = int(row["ID(ignored)"])
        G.add_node(node_id, pos=(float(row["x"]), float(row["y"])))

    for _, row in edge_df.iterrows():
        G.add_edge(int(row["from"]), int(row["to"]))

    return G


def draw_map(G, map_name, node_size=150, font_size=10, transparent=False, save=False, goal_nodes=None, show_labels=True):
    """グラフを描画(タイトルなし・透明背景や保存も対応)"""
    pos = nx.get_node_attributes(G, "pos")

    fig = plt.figure(figsize=(10, 6), facecolor="none")  # 背景透明
    ax = plt.gca()
    ax.set_facecolor("none")  # 背景透明

    # ゴールノードと通常ノードを分ける
    if goal_nodes is None:
        goal_nodes = []
    
    # グラフに存在しないゴールノードを除外
    valid_goal_nodes = [n for n in goal_nodes if n in G.nodes()]
    invalid_goal_nodes = [n for n in goal_nodes if n not in G.nodes()]
    
    if invalid_goal_nodes:
        print(f"⚠️  警告: 以下のノードはグラフに存在しません: {invalid_goal_nodes}")
        print(f"グラフに存在するノード: {sorted(G.nodes())}")
    
    regular_nodes = [n for n in G.nodes() if n not in valid_goal_nodes]
    
    # 通常のノードを描画
    nx.draw_networkx_nodes(G, pos, nodelist=regular_nodes, node_size=node_size, 
                          node_color="skyblue", edgecolors="black")
    
    # ゴールノードを異なる色で描画
    goal_colors = ["red", "green", "orange"]  # 3つの異なる色
    for i, goal_node in enumerate(valid_goal_nodes):
        color = goal_colors[i % len(goal_colors)]  # 3つ以上の場合は繰り返し
        nx.draw_networkx_nodes(G, pos, nodelist=[goal_node], node_size=node_size, 
                              node_color=color, edgecolors="black")
    
    nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.7)
    
    if show_labels:
        # 通常のラベルを描画
        regular_labels = {n: n for n in regular_nodes}
        nx.draw_networkx_labels(G, pos, labels=regular_labels, font_size=font_size, font_color="black")
        
        # ゴールノードには "G" を表示
        if valid_goal_nodes:
            goal_labels = {n: "G" for n in valid_goal_nodes}
            nx.draw_networkx_labels(G, pos, labels=goal_labels, font_size=font_size, font_color="white")

    plt.axis("equal")
    plt.axis("off")
    plt.tight_layout()

    if save:
        # outフォルダに保存
        out_dir = "out"
        os.makedirs(out_dir, exist_ok=True)  # outフォルダがなければ作成
        out_path = os.path.join(out_dir, f"{map_name}.png")
        plt.savefig(out_path, transparent=transparent, dpi=300)
        print(f"✅ 保存しました: {out_path}")

    plt.show()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python map.py <map_name> [--save] [--transparent] [--goal <node_ids>] [--no-label]")
        print("例: python map.py map01 --save --transparent --goal 3,7,9 --no-label")
        sys.exit(1)

    map_name = sys.argv[1]
    save = "--save" in sys.argv
    transparent = "--transparent" in sys.argv
    show_labels = "--no-label" not in sys.argv
    
    # ゴールノードの指定
    goal_nodes = []
    if "--goal" in sys.argv:
        goal_idx = sys.argv.index("--goal")
        if goal_idx + 1 < len(sys.argv):
            goal_str = sys.argv[goal_idx + 1]
            goal_nodes = [int(x.strip()) for x in goal_str.split(",")]

    print(f"マップ '{map_name}' を読み込み中...")
    if goal_nodes:
        print(f"ゴールノード: {goal_nodes}")

    G = load_map(map_name)
    draw_map(G, map_name, save=save, transparent=transparent, goal_nodes=goal_nodes, show_labels=show_labels)
