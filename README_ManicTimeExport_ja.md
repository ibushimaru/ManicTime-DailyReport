# ManicTime アプリケーション使用状況エクスポート＆AI日報自動化ツール

## 概要
このツールは、ManicTimeのアプリケーション使用状況を自動でCSVエクスポートし、Google Gemini APIを使って日報を自動生成、Obsidian VaultにMarkdown形式で保存する自動化スクリプトです。

---

## 技術仕様
- **言語**: Python 3.7以降
- **主要ライブラリ**: pandas, python-dotenv, google-generativeai
- **対応OS**: Windows 10以降
- **ManicTime**: CLIエクスポート機能必須（Pro/Server推奨）
- **AI要約**: Google Gemini API
- **出力**: Obsidian Vault内にMarkdown日報＋CSV

---

## ユーザーが設定する項目（.envファイル）
1. `.env.example` をコピーし `.env` を作成
2. 以下の3項目を自分の環境に合わせて設定

```
API_KEY=your_gemini_api_key_here
VAULT_PATH=C:/Users/yourname/Desktop/作業ファイル/Obsidian/Test
MANICTIME_EXE=C:/Program Files/ManicTime/Mtc.exe
```
- `API_KEY`: Google Gemini APIキー
- `VAULT_PATH`: Obsidian Vaultのパス
- `MANICTIME_EXE`: ManicTime CLI (Mtc.exe) のフルパス

---

## セットアップ手順
1. 必要なPythonパッケージをインストール
   ```
   pip install -r requirements.txt
   ```
2. `.env`ファイルを作成し、上記3項目を設定
3. ManicTimeが起動していることを確認
4. コマンドプロンプトまたはPowerShellを**管理者として実行**
5. スクリプトを実行
   ```
   python export_and_report.py
   ```
6. Obsidian Vault内に日報MarkdownとCSVが出力されます

---

## 注意事項
- **APIキーやパスは絶対に公開しないでください**（.envは.gitignoreで除外済み）
- ManicTimeの無料版ではCLIエクスポートが制限されている場合があります
- エクスポート先やVaultパスは必ず書き込み権限のある場所を指定してください
- 管理者権限での実行が必要な場合があります
- Google Gemini APIの利用にはGoogleアカウントとAPIキーが必要です

---

## サポート・参考
- ManicTime CLI: https://docs.manictime.com/win-client/cli
- Google Gemini API: https://ai.google.dev/
- Obsidian: https://obsidian.md/

ご不明点はGitHub Issues等でご連絡ください。

---

## AIモデルの切り替えについて

本ツールはデフォルトで **Google Gemini APIの「gemini-2.0-flash」モデル** を利用しています。

他のモデル（例: gemini-2.5-pro など）を利用したい場合は、
`export_and_report.py` 内の下記該当箇所のモデル名を変更してください。

```
model = genai.GenerativeModel('gemini-2.0-flash')
```

例：
```
model = genai.GenerativeModel('gemini-2.5-pro')
```

ご利用のGoogleアカウントやAPIプランによって利用可能なモデルが異なる場合があります。
詳しくは[Google Gemini API公式ドキュメント](https://ai.google.dev/)をご参照ください。 