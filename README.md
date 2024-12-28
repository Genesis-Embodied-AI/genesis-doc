# Genesis ドキュメント (日本語版)

このリポジトリには、Genesis の日本語ドキュメントが含まれています。Genesis はロボットシミュレーションのための Python ライブラリです。

## クイックスタート

### 1. リポジトリをクローンする

まず、ドキュメントのリポジトリをローカルにクローンします:

```bash
git clone https://github.com/Genesis-Embodied-AI/genesis-doc.git
cd genesis-doc
# 日本語ドキュメントのブランチに切り替え
git checkout ja_version
```

### 2. 環境構築

Python 環境を作成して設定します:

```bash
# 新しい conda 環境を作成
conda create -n genesis python=3.10
conda activate genesis

# ドキュメント構築の依存パッケージをインストール
pip install -r requirements.txt
```

### 3. ドキュメントを構築する

ドキュメントは Sphinx を使用して構築されます。以下のコマンドでドキュメントを構築し、リアルタイムプレビューサーバーを起動できます:

```bash
# ビルドディレクトリをクリーンアップしてドキュメントを構築
rm -rf build/
make html

# リアルタイムプレビューサーバーを起動
sphinx-autobuild -b html -E -a -q ./source ./build/html
```

構築が完了した後、ブラウザで <http://localhost:8000> にアクセスしてドキュメントを確認できます。

### よくある質問

1. 構築エラーが発生した場合:
   - ビルドディレクトリをクリーンアップしてください: `rm -rf build/`
   - 依存パッケージを再インストールしてください: `pip install -e ".[docs]"`

2. リアルタイムプレビューが更新されない場合:
   - sphinx-autobuild が実行中か確認してください
   - ブラウザのキャッシュを手動で更新してみてください

### 貢献ガイドライン

ドキュメントの改善にご協力いただける場合は、ぜひ PR を提出してください:

1. 本リポジトリをフォーク
2. 新しいブランチを作成
3. 修正内容をコミット
4. Pull Request を送信

ご不明点がございましたら、Issue を送信してご相談ください。