# ManicTime アプリケーション使用状況エクスポート＆AI日報自動化ツール

## 概要
このツールは、ManicTimeのアプリケーション使用状況を自動でCSVエクスポートし、Google Gemini APIを使って日報を自動生成しMarkdown形式で保存する自動化スクリプトです。

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
VAULT_PATH=C:/Users/username/Desktop
MANICTIME_EXE=C:/Program Files/ManicTime/Mtc.exe
```
- `API_KEY`: Google Gemini APIキー(https://aistudio.google.com/app/apikey)
- `VAULT_PATH`: ManicTimeから出力するcsvの保存先、及び日報の出力ファイル
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
6. Vault_Path内にManicTimeで記録したアプリケーション利用履歴と(CSV形式)日報(Markdown形式)が出力されます。

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
model = genai.GenerativeModel('gemini-2.5-pro-preview-05-06')
```

ご利用のGoogleアカウントやAPIプランによって利用可能なモデルが異なる場合があります。
詳しくは[Google Gemini API公式ドキュメント](https://ai.google.dev/)をご参照ください。

---

## 定期実行（自動日報生成）の設定例

### Windowsタスクスケジューラを使う場合
1. 「タスクスケジューラ」を起動
2. 「基本タスクの作成」→ 名前を入力（例：ManicTime日報自動生成）
3. 「トリガー」で「毎日」や「毎週」などを選択（例：毎日9:00）
4. 「操作」で「プログラムの開始」を選択し、
   - プログラム/スクリプト：`python`
   - 引数の追加：`C:\Users\username\export_and_report.py`
   - 開始（作業）フォルダー：スクリプトのあるディレクトリ
5. 「完了」で保存

- Pythonやスクリプトのパスはご自身の環境に合わせて修正してください。
- 管理者権限が必要な場合は「タスクのプロパティ」→「最上位の特権で実行する」にチェック

### その他の自動化方法
- バッチファイルやPowerShellスクリプトでラップし、ショートカットや他の自動化ツールから呼び出すことも可能です。 
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

ご不明点は Twitter(現X) @ibushi_maru までご連絡ください。
