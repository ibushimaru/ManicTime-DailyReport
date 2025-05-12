import os
import subprocess
from datetime import datetime
import google.generativeai as genai
from dataclasses import dataclass
from typing import List, Dict
from collections import defaultdict
from dotenv import load_dotenv

# ====== 設定 ======
load_dotenv()
API_KEY = os.getenv("API_KEY")
VAULT_PATH = os.getenv("VAULT_PATH")
MANICTIME_EXE = os.getenv("MANICTIME_EXE")
if not API_KEY or not VAULT_PATH or not MANICTIME_EXE:
    print(".envファイルでAPI_KEY, VAULT_PATH, MANICTIME_EXEを設定してください。")
    exit(1)

# エクスポートファイル名
csv_filename = f"ManicTime_Export_{datetime.now().strftime('%Y-%m-%d')}.csv"
csv_path = os.path.join(VAULT_PATH, csv_filename)

# ====== 1. ManicTimeエクスポート ======
print("ManicTimeからアプリケーション利用履歴をエクスポート中...")
export_cmd = [
    MANICTIME_EXE,
    "export",
    "ManicTime/Applications",
    csv_path,
    f"/fd:{datetime.now().strftime('%Y-%m-%d')}",
    f"/td:{datetime.now().strftime('%Y-%m-%d')}"
]
try:
    subprocess.run(export_cmd, check=True)
    print(f"エクスポート完了: {csv_path}")
except Exception as e:
    print("エクスポートに失敗しました: ", e)
    exit(1)

# ====== 2. 日報生成ロジック（既存処理を流用） ======
@dataclass
class Activity:
    name: str
    start: datetime
    end: datetime
    duration: str
    process: str

def parse_duration(duration_str: str) -> int:
    try:
        h, m, s = map(int, duration_str.split(':'))
        return h * 3600 + m * 60 + s
    except:
        return 0

def csv_to_activities(csv_path: str) -> List[Activity]:
    activities = []
    with open(csv_path, encoding='utf-8-sig') as f:
        import csv
        reader = csv.reader(f)
        header = next(reader)
        name_idx = header.index('Name')
        start_idx = header.index('Start')
        end_idx = header.index('End')
        duration_idx = header.index('Duration')
        process_idx = header.index('Process')
        for row in reader:
            try:
                start_str = row[start_idx].split('.')[0]
                end_str = row[end_idx].split('.')[0]
                activity = Activity(
                    name=row[name_idx],
                    start=datetime.fromisoformat(start_str),
                    end=datetime.fromisoformat(end_str),
                    duration=row[duration_idx],
                    process=row[process_idx]
                )
                activities.append(activity)
            except Exception as e:
                print(f"行の処理中にエラーが発生: {row}")
                print(f"エラー内容: {e}")
                continue
    return activities

def analyze_activities(activities: List[Activity]) -> Dict:
    app_durations = defaultdict(int)
    process_durations = defaultdict(int)
    hourly_activities = defaultdict(list)
    for activity in activities:
        duration_seconds = parse_duration(activity.duration)
        app_durations[activity.name] += duration_seconds
        process_durations[activity.process] += duration_seconds
        hour = activity.start.hour
        hourly_activities[hour].append(activity)
    return {
        'app_durations': dict(app_durations),
        'process_durations': dict(process_durations),
        'hourly_activities': dict(hourly_activities)
    }

def csv_to_prompt(csv_path):
    activities = csv_to_activities(csv_path)
    analysis = analyze_activities(activities)
    top_apps = sorted(
        analysis['app_durations'].items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]
    today_str = datetime.now().strftime('%Y-%m-%d')
    # CSV生データを読み込む
    with open(csv_path, encoding='utf-8-sig') as f:
        csv_raw = f.read()
    prompt = f"""
重要事項:もしデータがない場合は、データなしとだけ報告してください。
以下はPCのアプリケーション利用履歴です。CSVのカラム構造は次の通りです：
{csv_raw}
Name, Start, End, Duration, Process

このデータから、以下の日報テンプレートに従って日本語で日報を作成してください。
日報は、自己の活動を客観的に振り返り、生産性向上や課題発見、翌日以降の計画立案に役立てることを目的とします。
(内は指示内容です。出力データには含めないでください。)

## 1. 本日の活動ハイライト
（ManicTimeのログから、本日特に時間を費やした活動や、特徴的な行動パターンを3-5行程度で要約してください。時間はできるだけ正確に積算してください。単なるアプリ使用時間の報告ではなく、何に取り組んでいたのかが推測できるような記述を心がけてください。「ManicTimeのデータ活用方法の調査とスクリプト作成に注力し、Vivaldiでの情報収集とCursorでの開発作業が中心でした。合間にはXの閲覧も見られました。」のような形式を参考にしてください。）
（一日のPC作業の合計時間を表示し、働き過ぎ等のコメントを残してください。）

## 2. 主要な活動カテゴリと所要時間
（アプリケーション名だけでなく、ウィンドウタイトルや連続使用時間などから、ユーザーが行っていたと思われる主要な活動カテゴリを3～5つ程度に分類し、それぞれの活動に費やされたおおよその合計時間を記載してください。例えば、「ManicTime関連作業（Vivaldi, Cursor, ManicTime本体, Windows Terminalなど）- 約X時間XX分」「情報収集・調査（Vivaldi - 技術ブログ, ドキュメント閲覧など）- 約Y時間YY分」「SNS・休憩（Vivaldi - X, Spotifyなど）- 約Z時間ZZ分」のように、関連アプリをグルーピングして記述してください。）

## 3. アプリケーション利用時間 Top 5
{chr(10).join(f"{i+1}. {app} - {duration//3600}時間{(duration%3600)//60}分" for i, (app, duration) in enumerate(top_apps))}

## 4. 各時間ごとの作業内容
(ManicTimeのログから、各時間ごとの作業内容を記載してください。1:00-2:00,2;00-3;00のように1時間ごとに分けて記載してください。作業が連続して存在しない場合は、その時間は空白としてください。1時間程度なら休憩と記載)

## 5. 振り返りとネクストアクション
(自己の活動を客観的に分析したデータを各項目2~3行程度で記載してください。)
*   **今日の主な成果・達成できたこと:**
    *
*   **課題や反省点、改善したいこと (例: 集中が途切れた要因、非効率だった作業など):**
    *
*   **今日の活動で得た気付きや学び (例: 新しい知識、便利なツール、作業のコツなど):**
    *
*   **明日以降取り組むこと・目標:**
    *
*   **その他特記事項:**
    *

"""
    return prompt

# ====== Gemini APIで日報生成 ======
genai.configure(api_key=API_KEY)
try:
    model = genai.GenerativeModel('gemini-2.0-flash')
    prompt = csv_to_prompt(csv_path)
    response = model.generate_content(prompt)
    report_text = response.text
except Exception as e:
    print("Gemini APIでエラーが発生しました: ", e)
    exit(1)

# ====== ObsidianにMarkdownで保存 ======
md_filename = f"日報_{datetime.now().strftime('%Y-%m-%d')}.md"
md_path = os.path.join(VAULT_PATH, md_filename)
with open(md_path, 'w', encoding='utf-8') as f:
    f.write(report_text)

print(f"日報をObsidianに保存しました: {md_path}") 