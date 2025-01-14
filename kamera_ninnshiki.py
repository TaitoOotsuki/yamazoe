import cv2
import pytesseract
import re
from datetime import datetime

def main():
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # インストールパスを確認して変更
    # カメラを開く（PCに接続されているカメラを指定）
    cap = cv2.VideoCapture(0)  # 0は最初のカメラ。別のカメラを使う場合は1や2に変更
    
    if not cap.isOpened():
        print("カメラの接続に失敗しました。")
        return

    # 画像をキャプチャ
    ret, frame = cap.read()
    if not ret:
        print("画像のキャプチャに失敗しました。")
        cap.release()
        return

    # 画像をグレースケールに変換
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 画像を二値化
    _, binary_image = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    # OCRでテキストを抽出
    extracted_text = pytesseract.image_to_string(binary_image)
    print("抽出されたテキスト:")
    print(extracted_text)

    # 賞味期限と思われる日付部分を抽出（正規表現）
    date_pattern = r'(\d{4}[-/.\s]?\d{1,2}[-/.\s]?\d{1,2}|\d{1,2}[-/.\s]?\d{1,2}[-/.\s]?\d{4}|\d{1,2}[-/.\s]?\d{1,2}[-/.\s]?\d{2,4}|\d{2,4}[-/.\s]?\d{1,2}[-/.\s]?\d{1,2}|\d{2}[-/.\s]?\d{1,2}[-/.\s]?\d{1,2})'

    dates = re.findall(date_pattern, extracted_text)

    if dates:
        print("検出された賞味期限:", dates)
        
        # 日付を数字として変換
        for date_str in dates:
            # 日付の形式を統一するため、いくつかのパターンを変換
            try:
                if '/' in date_str:
                    # 例: 12/31/2025 (MM/DD/YYYY) または 31/12/2025 (DD/MM/YYYY)
                    date_obj = datetime.strptime(date_str, "%m/%d/%Y") if len(date_str.split('/')[0]) == 2 else datetime.strptime(date_str, "%d/%m/%Y")
                elif '-' in date_str:
                    # 例: 2025-01-13 (YYYY-MM-DD)
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                else:
                    continue

                # 数字として出力（YYYY-MM-DD形式）
                formatted_date = date_obj.strftime("%Y-%m-%d")
                print(f"賞味期限: {formatted_date}")
            except ValueError:
                print(f"日付の変換エラー: {date_str}")
    else:
        print("賞味期限が見つかりませんでした。")

    # カメラリソースを解放
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
