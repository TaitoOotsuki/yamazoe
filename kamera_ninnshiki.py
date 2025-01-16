import cv2
import pytesseract
import re
from datetime import datetime
import csv
import time

def monitor_expiry_dates():
    pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'  # Tesseractのパス
    
    cv2.setUseOptimized(True)
    
    # カメラを開く
    cap = cv2.VideoCapture(0)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # 幅
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # 高さ
    
    if not cap.isOpened():
        print("カメラの接続に失敗しました。")
        return

    print("賞味期限を監視中...（終了するには 'q' キーを押してください）")

    custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789'
    ocr_frequency = 5
    frame_counter = 0

    while True:
        # 画像をキャプチャ
        ret, frame = cap.read()
        if not ret:
            print("画像のキャプチャに失敗しました。")
            break
        if frame_counter % ocr_frequency == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            extracted_text = pytesseract.image_to_string(gray, config=custom_config)
            dates = re.findall(date_pattern, extracted_text)
        # 画像をグレースケールに変換


        # OCRでテキストを抽出
        extracted_text = pytesseract.image_to_string(gray, config=custom_config)

        # 賞味期限と思われる日付部分を抽出（正規表現）
        date_pattern = r'(\d{4}[./-]\d{1,2}[./-]?\d{0,2}|\d{1,2}[./-]\d{1,2}[./-]\d{2,4}|\d{4}[./-]\d{1,2})'
        dates = re.findall(date_pattern, extracted_text)

        if dates:
            results = []
            for date_str in dates:
                try:
                    date_obj = None
                    if '/' in date_str:
                        if len(date_str.split('/')[0]) == 2:
                            date_obj = datetime.strptime(date_str, "%m/%d/%Y")
                        else:
                            date_obj = datetime.strptime(date_str, "%d/%m/%Y")
                    elif '-' in date_str:
                        if len(date_str.split('-')) == 2:
                            date_obj = datetime.strptime(date_str, "%Y-%m")
                        else:
                            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    elif '.' in date_str:
                        if len(date_str.split('.')) == 2:
                            date_obj = datetime.strptime(date_str, "%Y.%m")
                        else:
                            date_obj = datetime.strptime(date_str, "%Y.%m.%d")

                    if date_obj:
                        formatted_date = date_obj.strftime("%Y-%m-%d") if date_obj.day != 1 else date_obj.strftime("%Y-%m")
                        results.append([formatted_date])
                except ValueError:
                    continue

            if results:
                # CSVに保存
                with open('expiry_dates.csv', 'a', newline='', encoding='utf-8') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    csvwriter.writerow(["賞味期限"])
                    csvwriter.writerows(results)
                print("賞味期限を検出しました。データを保存しました。")
                break  # 賞味期限が見つかったら終了
                    # 画像ウィンドウを表示
        frame_counter += 1
        cv2.imshow("image", frame)

        # 'q' キーで終了
        key = cv2.waitKey(50)
        if key != -1:
            break


        # 処理負荷軽減のため待機
        time.sleep(1)

    # カメラリソースを解放
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    monitor_expiry_dates()
