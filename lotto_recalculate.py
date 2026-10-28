import json
import os

# 자동 생성할 목데이터
MOCK_DATA = [
    {
        "draw_id": 201,
        "date": "2026-03-01",
        "numbers": [8, 14, 22, 29, 35, 47],
        "bonus": 12
    },
    {
        "draw_id": 202,
        "date": "2026-03-08",
        "numbers": [3, 11, 19, 26, 38, 42],
        "bonus": 7
    },
    {
        "draw_id": 203,
        "date": "2026-03-15",
        "numbers": [5, 16, 21, 30, 41, 49],
        "bonus": 9
    }
]

def create_json_file(file_path):
    """목데이터를 JSON 파일로 생성"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(MOCK_DATA, f, ensure_ascii=False, indent=4)
        print(f"📄 '{file_path}' 파일이 생성되었습니다.")
    except Exception as e:
        print(f"❌ JSON 파일 생성 오류: {e}")

def load_json_file(file_path):
    """JSON 파일을 읽어 리스트 반환"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")
    except Exception as e:
        raise RuntimeError(f"Error reading file: {e}")

    if not isinstance(data, list):
        raise TypeError("Expected JSON content to be a list of draws.")

    return data

def filter_by_date(data, target_date):
    """날짜로 필터"""
    return [draw for draw in data if draw.get("date") == target_date]

def filter_by_number(data, target_number):
    """번호로 필터"""
    return [draw for draw in data if target_number in draw.get("numbers", [])]

def display_results(results, query_type, query_value):
    """검색 결과 출력"""
    if not results:
        print(f"⚠ 검색 결과 없음 — {query_type}: {query_value}\n")
        return
    print(f"🔍 검색 결과 — {query_type}: {query_value}")
    for draw in results:
        print(f"  Draw #{draw['draw_id']} | Date: {draw['date']} | Numbers: {', '.join(map(str, draw['numbers']))} | Bonus: {draw['bonus']}")
    print()

def main():
    file_path = "all_draws.json"

    # JSON 파일이 없으면 자동 생성
    if not os.path.exists(file_path):
        create_json_file(file_path)

    try:
        data = load_json_file(file_path)
        print(f"✅ {len(data)}개의 추첨 기록을 불러왔습니다.\n")

        choice = input("검색 방법 선택 — (1) 날짜 / (2) 번호 : ").strip()
        if choice == "1":
            date_query = input("날짜 입력 (YYYY-MM-DD): ").strip()
            results = filter_by_date(data, date_query)
            display_results(results, "날짜", date_query)
        elif choice == "2":
            try:
                number_query = int(input("번호 입력: ").strip())
            except ValueError:
                print("❌ 잘못된 번호 입력.")
                return
            results = filter_by_number(data, number_query)
            display_results(results, "번호", number_query)
        else:
            print("❌ 잘못된 선택입니다. 1 또는 2를 입력하세요.")

    except Exception as e:
        print(f"❌ 오류: {e}")

if __name__ == "__main__":
    main()
