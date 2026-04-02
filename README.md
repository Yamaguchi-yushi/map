# Map Visualizer - Web UI

A web-based interactive map visualization tool built with Flask, NetworkX, and Matplotlib. It automatically detects maps from CSV files and provides a clean interface to render and export them with various visual customizations.

## Features

- **Automatic Map Detection**: Automatically detects custom map directories inside the `maps/` folder.
- **Interactive Customization**: Customize node sizes, add goal nodes, highlight stations, adjust edge visibility, and toggle edge weights.
- **High-Quality Export**: Export generated graphs to PNG, PDF, or EPS formats directly from the application.
- **Flexible Styling**: Built-in support for Japanese fonts, transparent backgrounds, and customized node/edge colors.

## Project Structure

```
map/
├── app.py              # Main Flask application and NetworkX rendering logic
├── map.py              # Additional map utility functions
├── maps/               # Data directory for maps. Each sub-folder needs node.csv & edge.csv
│   ├── map_10x10/
│   ├── map_shibuya/
│   └── ...
├── static/             # Frontend static files (app.js, style.css)
└── templates/          # HTML templates (index.html)
```

## Map Data Format

Every map must be placed in a unique directory under `maps/` and contain the following two files:

- **`node.csv`**: Contains node definitions. Must have `ID(ignored)`, `x`, and `y` columns. Optionally, it can have a `station` column to designate special nodes.
- **`edge.csv`**: Contains edges connecting the nodes. Must have `from` and `to` columns.

## Installation

Ensure you have Python 3 installed. Install the required dependencies using pip:

```bash
pip install flask pandas networkx matplotlib
```

## Running the App

1. Run the Flask server:
   ```bash
   python app.py
   ```
2. Open your web browser and navigate to:
   ```
   http://localhost:5051
   ```

## Usage

1. **Select Map**: Choose a map from the available dropdown menu.
2. **Parameters**: Modify rendering settings like node colors, background transparency, or highlight specific goal nodes.
3. **Export**: Click the download button to export the tailored map preview.

---

# Map Visualizer - Web UI (日本語)

Flask、NetworkX、Matplotlib を使用して構築された、ブラウザベースのインタラクティブなマップ可視化ツールです。CSVファイルからマップを自動検出し、多彩な見た目のカスタマイズとエクスポート機能を提供します。

## 機能

- **マップの自動検出**: `maps/` フォルダ内のカスタムマップディレクトリを自動的に読み込みます。
- **インタラクティブなカスタマイズ**: ノードサイズ、ゴールノード指定、ステーションノードのハイライト、エッジの表示切り替え、エッジの重み表示などの各種設定が可能です。
- **高品質エクスポート**: 表示されたグラフをPNG形式やPDF、EPS形式でダウンロードできます。
- **柔軟なスタイリング**: 日本語フォントへの対応、背景の透過設定、ノードやエッジのカラーの柔軟な変更が行えます。

## プロジェクト構成

```
map/
├── app.py              # アプリケーションのメインファイル (Flask / NetworkX のロジック)
├── map.py              # その他のマップユーティリティ処理など
├── maps/               # マップデータが格納されるディレクトリ
│   ├── map_10x10/      # 各マップフォルダ内には node.csv と edge.csv が必要
│   ├── map_shibuya/
│   └── ...
├── static/             # 静的ファイル (app.js, style.css)
└── templates/          # HTMLテンプレート (index.html)
```

## データ形式 (CSV)

各マップは `maps/` 配下に固有のディレクトリを作り、以下の2つのファイルを置く必要があります：

- **`node.csv`**: ノード情報を定義します。`ID(ignored)`, `x`, `y` 列が必須になります。特定のノードを区別するため、任意で `station` 列を追加することもできます。
- **`edge.csv`**: ノード間の繋がり（エッジ）を定義します。`from`, `to` 列が必須です。

## インストール手順

Python 3 がインストールされていることを確認し、pip を使って以下のようにパッケージをインストールしてください：

```bash
pip install flask pandas networkx matplotlib
```

## 起動方法

1. Flask サーバーを起動します：
   ```bash
   python app.py
   ```
2. Webブラウザを開き、以下のURLにアクセスします：
   ```
   http://localhost:5051
   ```

## 使い方

1. **マップの選択**: ドロップダウンメニューから可視化したい対象のマップを選択します。
2. **パラメーター変更**: ノードカラー、背景透過の設定、ゴールノードの指定などをお好みで変更します。
3. **エクスポート**: ダウンロードボタンをクリックして、条件に合わせて描画されたマップ画像を保存・エクスポートします。
