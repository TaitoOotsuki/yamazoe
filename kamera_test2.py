import cv2
import pytesseract
import re
from datetime import datetime
import csv

def preprocess_image(image):
    """画像を簡易的に前処理"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # グレースケール化
    _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)  # 簡易な二値化
    return binary

def extract_expiry_dates(image):
    """OCRで賞味期限の日付を抽出"""
    custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789./-'  # Tesseract設定
    extracted_text = pytesseract.image_to_string(image, config=custom_config)
    
    # 日付の正規表現パターン
    date_pattern = r'(\d{4}[./-]\d{1,2}[./-]?\d{0,2}|\d{1,2}[./-]\d{1,2}[./-]\d{2,4}|\d{4}[./-]\d{1,2})'
    dates = re.findall(date_pattern, extracted_text)
    
    return dates

def save_to_csv(dates):
    """抽出した日付をCSVに保存"""
    with open('expiry_dates.csv', 'a', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["賞味期限"])
        for date in dates:
            csvwriter.writerow([date])
    print(f"賞味期限を検出し、保存しました: {dates}")

def monitor_expiry_dates():
    pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'  # Tesseractのパス

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # 幅
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # 高さ

    if not cap.isOpened():
        print("カメラの接続に失敗しました。")
        return

    print("賞味期限を監視中...（終了するには 'q' キーを押してください）")

    frame_counter = 0
    ocr_frequency = 10  # OCRを10フレームに1回実行

    while True:
        ret, frame = cap.read()
        if not ret:
            print("画像のキャプチャに失敗しました。")
            break

        # 必要なエリアをクロップ（例: 画像の中央部分）
        height, width = frame.shape[:2]
        cropped_frame = frame[height // 4 : 3 * height // 4, width // 4 : 3 * width // 4]

        # 前処理を実行
        processed_frame = preprocess_image(cropped_frame)

        # 一定間隔でOCRを実行
        if frame_counter % ocr_frequency == 0:
            dates = extract_expiry_dates(processed_frame)
            if dates:
                formatted_dates = []
                for date_str in dates:
                    try:
                        # 日付を統一フォーマットに変換
                        if '/' in date_str:
                            if len(date_str.split('/')) == 2:  # YYYY/MM
                                date_obj = datetime.strptime(date_str, "%Y/%m")
                                formatted_dates.append(date_obj.strftime("%Y-%m"))
                            elif len(date_str.split('/')) == 3:  # YYYY/MM/DD
                                date_obj = datetime.strptime(date_str, "%Y/%m/%d")
                                formatted_dates.append(date_obj.strftime("%Y-%m-%d"))
                        elif '-' in date_str:
                            if len(date_str.split('-')) == 2:  # YYYY-MM
                                date_obj = datetime.strptime(date_str, "%Y-%m")
                                formatted_dates.append(date_obj.strftime("%Y-%m"))
                            elif len(date_str.split('-')) == 3:  # YYYY-MM-DD
                                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                                formatted_dates.append(date_obj.strftime("%Y-%m-%d"))
                        elif '.' in date_str:
                            if len(date_str.split('.')) == 2:  # YYYY.MM
                                date_obj = datetime.strptime(date_str, "%Y.%m")
                                formatted_dates.append(date_obj.strftime("%Y-%m"))
                            elif len(date_str.split('.')) == 3:  # YYYY.MM.DD
                                date_obj = datetime.strptime(date_str, "%Y.%m.%d")
                                formatted_dates.append(date_obj.strftime("%Y-%m-%d"))
                    except ValueError:
                        continue
                
                if formatted_dates:
                    save_to_csv(formatted_dates)
                    break  # データを保存したらループを終了

        # フレームを表示
        cv2.imshow("Monitoring", cropped_frame)

        frame_counter += 1

        # 'q' キーで終了
        key = cv2.waitKey(1)
        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    monitor_expiry_dates()
