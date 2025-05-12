import pandas as pd
from datetime import timedelta
import os

# --- ヘルパー関数 ---

def parse_duration_to_seconds(duration_str):
    """
    "HH:MM:SS" 形式の期間文字列を総秒数に変換します。
    例: "0:01:05" -> 65
    """
    parts = list(map(int, str(duration_str).split(':')))
    if len(parts) == 3: # HH:MM:SS
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    elif len(parts) == 2: # MM:SS (もしあれば)
        return parts[0] * 60 + parts[1]
    elif len(parts) == 1: # SS (もしあれば)
        return parts[0]
    return 0

def format_seconds_for_gantt(seconds):
    """
    秒数をMermaidガントチャートで使える期間形式 (例: "65s") に変換します。
    """
    return f"{int(seconds)}s"

def escape_mermaid_text(text):
    """
    Mermaidのテキスト内で問題を起こしうる文字をエスケープします。
    特にダブルクォートをHTMLエンティティに置換します。
    """
    if not isinstance(text, str):
        text = str(text)
    return text.replace('"', '&quot;')


# --- パイチャート生成関数 ---

def generate_pie_chart_mermaid(df, title="アプリケーション別 総利用時間"):
    """
    DataFrameからアプリケーションごとの総利用時間のパイチャート用Mermaidコードを生成します。
    """
    # Durationを秒に変換
    df['Duration_Seconds'] = df['Duration'].apply(parse_duration_to_seconds)

    # Processごとの総利用時間を計算
    process_times = df.groupby('Process')['Duration_Seconds'].sum().sort_values(ascending=False)

    mermaid_code = "pie\n"
    mermaid_code += f'    title "{escape_mermaid_text(title)}"\n'

    for process, total_seconds in process_times.items():
        if total_seconds > 0: # 0秒のものは表示しない
            escaped_process_name = escape_mermaid_text(process)
            mermaid_code += f'    "{escaped_process_name}" : {total_seconds}\n'
    
    return mermaid_code


# --- ガントチャート生成関数 ---

def generate_gantt_chart_mermaid(df, title_date="YYYY-MM-DD", max_entries=None):
    """
    DataFrameから時系列の作業の流れを示すガントチャート用Mermaidコードを生成します。
    max_entries: 表示する最大タスク数 (Noneの場合は全件)
    """
    mermaid_code = "gantt\n"
    mermaid_code += "    dateFormat  YYYY-MM-DDTHH:mm:ss\n" # CSVのStart列の形式に合わせる
    mermaid_code += f'    title "{escape_mermaid_text(title_date)} 作業タイムライン"\n'
    mermaid_code += "    axisFormat %H:%M\n\n"

    # max_entriesが指定されていれば、データ件数を制限
    df_to_process = df.copy()
    if max_entries is not None:
        df_to_process = df_to_process.head(max_entries)

    # 処理対象のデータに含まれるプロセスのみをセクション化
    unique_processes_in_order = df_to_process['Process'].unique()

    for process_name in unique_processes_in_order:
        escaped_section_name = escape_mermaid_text(process_name)
        mermaid_code += f"    section {escaped_section_name}\n"
        
        tasks_in_process = df_to_process[df_to_process['Process'] == process_name]

        for index, row in tasks_in_process.iterrows():
            # タスク名が長すぎる場合、適当な長さに丸めることも検討できます
            task_name = escape_mermaid_text(row['Name']) 
            
            # Start時刻のミリ秒部分を除去
            start_time = str(row['Start']).split('.')[0]
            
            duration_seconds = parse_duration_to_seconds(row['Duration'])
            
            # 期間が0秒以下のタスクはガントチャートで問題を起こす可能性があるためスキップ
            if duration_seconds <= 0:
                continue
                
            gantt_duration = format_seconds_for_gantt(duration_seconds)
            
            # Mermaidのタスク定義
            # タスク名に : が含まれるとMermaidの構文と衝突する可能性があるため注意。
            # ここではタスク名と開始時刻・期間を : で区切る
            mermaid_code += f'    {task_name} :{start_time},{gantt_duration}\n'
        mermaid_code += "\n" # セクションの終わりに見やすく改行
        
    return mermaid_code


# --- テーブル生成関数 ---
def generate_table_mermaid(df, columns, title="アプリ利用ログ", max_rows=20):
    """
    DataFrameから指定カラムのMermaidテーブルコードを生成します。
    columns: 表示したいカラム名リスト
    title: テーブルタイトル
    max_rows: 表示する最大行数
    """
    mermaid_code = "table\n"
    mermaid_code += f'    title {escape_mermaid_text(title)}\n'
    # ヘッダー
    header = ' '.join([f'"{escape_mermaid_text(col)}"' for col in columns])
    mermaid_code += f'    {header}\n'
    # データ行
    for _, row in df.head(max_rows).iterrows():
        line = ' '.join([f'"{escape_mermaid_text(row[col])}"' for col in columns])
        mermaid_code += f'    {line}\n'
    return mermaid_code


# --- メイン処理 ---
if __name__ == "__main__":
    # export_and_report.pyの設定を流用
    VAULT_PATH = r"C:\Users\ibushi maru\Desktop\作業ファイル\Obsidian\Test"
    from datetime import datetime
    csv_filename = f"ManicTime_Export_{datetime.now().strftime('%Y-%m-%d')}.csv"
    csv_file_path = os.path.join(VAULT_PATH, csv_filename)

    try:
        # BOM付きUTF-8ファイルの場合、encoding='utf-8-sig' を試す
        try:
            df = pd.read_csv(csv_file_path)
        except UnicodeDecodeError:
            df = pd.read_csv(csv_file_path, encoding='utf-8-sig')
            
    except FileNotFoundError:
        print(f"エラー: ファイル '{csv_file_path}' が見つかりません。")
        exit()
    except Exception as e:
        print(f"エラー: CSVファイルの読み込み中に問題が発生しました: {e}")
        exit()

    # ファイル名から日付部分を抽出 (簡易的な方法)
    try:
        # 'ManicTime_Export_YYYY-MM-DD.csv' の形式を想定
        date_from_filename = csv_filename.split('_')[-1].split('.')[0]
    except IndexError:
        date_from_filename = "日付不明"

    output_path = "test_output.md"
    with open(output_path, "w", encoding="utf-8") as file:
        # 1. パイチャートのMermaidコードを生成して表示
        file.write(f"--- アプリケーション別 総利用時間 (Mermaid Pie Chart) ---\n")
        pie_mermaid = generate_pie_chart_mermaid(df.copy(), title=f"{date_from_filename} アプリケーション別 総利用時間")
        file.write("```mermaid\n")
        file.write(pie_mermaid + "\n")
        file.write("```\n\n" + "="*50 + "\n\n")

        # 2. ガントチャートのMermaidコードを生成して表示
        num_gantt_entries = 30 
        file.write(f"--- {date_from_filename} 作業タイムライン (Mermaid Gantt Chart - 先頭{num_gantt_entries}件) ---\n")
        gantt_mermaid = generate_gantt_chart_mermaid(df.copy(), title_date=date_from_filename, max_entries=num_gantt_entries)
        file.write("```mermaid\n")
        file.write(gantt_mermaid + "\n")
        file.write("```\n")
        if num_gantt_entries is not None and len(df) > num_gantt_entries:
            file.write(f"\n注意: ガントチャートはデータが多いため、最初の {num_gantt_entries} 件のみ表示しています。\n")
            file.write(f"全件表示するには、コード内の `num_gantt_entries` を `None` に変更してください（非常に長くなる可能性があります）。\n\n")

        # 3. テーブル（表）のMermaidコードを生成して表示
        file.write(f"--- {date_from_filename} アプリ利用ログ (Mermaid Table - 先頭20件) ---\n")
        table_columns = ["Process", "Start", "End", "Duration"]
        table_mermaid = generate_table_mermaid(df.copy(), columns=table_columns, title=f"{date_from_filename} アプリ利用ログ", max_rows=20)
        file.write("```mermaid\n")
        file.write(table_mermaid + "\n")
        file.write("```\n")
        if len(df) > 20:
            file.write(f"\n注意: 表はデータが多いため、最初の 20 件のみ表示しています。全件表示するには、コード内の `max_rows` を変更してください。\n")