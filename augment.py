import pyautogui
import cv2
import numpy as np
import time
import random
import keyboard  # для остановки по пробелу
from ultralytics import YOLO

# ================= НАСТРОЙКИ =================
MODEL_PATH = r'C:\cookie\best.onnx'  # ONNX модель!
CONFIDENCE_THRESHOLD = 0.4           # порог уверенности (меняйте по вкусу)

# Колдауны (задержки в секундах) — рандомные, чтобы бот выглядел как человек
COOLDOWN_CLICK_COOKIE = (0.5, 1.5)      # после клика по печеньке
COOLDOWN_CLICK_UPGRADE = (1.0, 3.0)     # после покупки улучшения
COOLDOWN_CLICK_BONUS = (0.3, 0.8)       # после сбора бонуса
COOLDOWN_CLICK_AD = (0.5, 1.5)          # после закрытия рекламы
COOLDOWN_NOTHING = (0.3, 0.7)           # если ничего не найдено
# =============================================

# Загрузка ONNX модели
print(" Загрузка ONNX модели...")
model = YOLO(MODEL_PATH, task='detect')
print(" Модель загружена!\n")

pyautogui.FAILSAFE = False

# Флаг остановки
running = True

def on_space_pressed():
    global running
    running = False
    print("\n Получен сигнал остановки (пробел)")

keyboard.on_press_key('space', lambda _: on_space_pressed())


def random_sleep(cooldown_range):
    """Случайная задержка из диапазона (колдаун)"""
    time.sleep(random.uniform(*cooldown_range))


def find_and_click():
    """Находит объекты на экране и кликает по ним по приоритету"""
    
    # 1. Скриншот
    screenshot = pyautogui.screenshot()
    screenshot_np = np.array(screenshot)
    screenshot_np = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
    
    # 2. Детекция через ONNX модель
    results = model(screenshot_np, conf=CONFIDENCE_THRESHOLD, verbose=False)
    
    detected = {
        'close_ad': [],
        'bonus': [],
        'game': [],
        'upgrade': []
    }
    
    for result in results:
        boxes = result.boxes
        if boxes is not None:
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                class_name = model.names[class_id]
                
                if class_name in detected:
                    center_x = int((x1 + x2) / 2)
                    center_y = int((y1 + y2) / 2)
                    detected[class_name].append({
                        'x': center_x,
                        'y': center_y,
                        'conf': confidence
                    })
    
    # ПРИОРИТЕТ 1: Закрываем рекламу
    if detected['close_ad']:
        for ad in detected['close_ad']:
            print(f" Закрываю рекламу: ({ad['x']}, {ad['y']}) уверенность: {ad['conf']:.2f}")
            pyautogui.click(ad['x'], ad['y'])
            random_sleep(COOLDOWN_CLICK_AD)
        return True
    
    # ПРИОРИТЕТ 2: Собираем бонусы
    if detected['bonus']:
        for bonus in detected['bonus']:
            print(f" Собираю бонус: ({bonus['x']}, {bonus['y']}) уверенность: {bonus['conf']:.2f}")
            pyautogui.click(bonus['x'], bonus['y'])
            random_sleep(COOLDOWN_CLICK_BONUS)
        return True
    
    # ПРИОРИТЕТ 3: Кликаем по печеньке
    if detected['game']:
        game = detected['game'][0]
        clicks = random.randint(3, 7)  # случайное количество кликов (колдаун)
        print(f" Кликаю по печеньке ({clicks} раз): ({game['x']}, {game['y']}) уверенность: {game['conf']:.2f}")
        for i in range(clicks):
            pyautogui.click(game['x'], game['y'])
            time.sleep(random.uniform(0.05, 0.15))
        random_sleep(COOLDOWN_CLICK_COOKIE)
        return True
    
    # ПРИОРИТЕТ 4: Покупаем улучшения
    if detected['upgrade']:
        upgrade = detected['upgrade'][0]
        print(f" Покупаю улучшение: ({upgrade['x']}, {upgrade['y']}) уверенность: {upgrade['conf']:.2f}")
        pyautogui.click(upgrade['x'], upgrade['y'])
        random_sleep(COOLDOWN_CLICK_UPGRADE)
        return True
    
    return False


# ================= ГЛАВНЫЙ ЦИКЛ =================
print("=" * 50)
print(" Cookie Clicker Bot (ONNX)")
print("=" * 50)
print(f"  Порог уверенности: {CONFIDENCE_THRESHOLD}")
print(f"  Остановка: ПРОБЕЛ")
print(f"  Колдауны: рандомные задержки")
print("=" * 50)
print("\nПриоритет действий:")
print("  1.  Закрыть рекламу (close_ad)")
print("  2.  Собрать бонус (bonus)")
print("  3.  Кликнуть по печеньке (game)")
print("  4.  Купить улучшение (upgrade)")
print("\n Бот запущен...\n")

try:
    while running:
        if find_and_click():
            pass  # колдаун уже внутри find_and_click
        else:
            random_sleep(COOLDOWN_NOTHING)
            
except KeyboardInterrupt:
    print("\n\n Бот остановлен пользователем (Ctrl+C).")
finally:
    print("\n Бот завершил работу.")