import os
import shutil
import random
import json

# ================= НАСТРОЙКИ =================
source_dir = r"C:\cookie\screenshots"
target_dir = r"C:\itog"
# =============================================

# 1. Создаем структуру папок
folders = [
    os.path.join(target_dir, "images", "train"),
    os.path.join(target_dir, "images", "val"),
    os.path.join(target_dir, "labels", "train"),
    os.path.join(target_dir, "labels", "val")
]
for folder in folders:
    os.makedirs(folder, exist_ok=True)

# 2. Находим все изображения
image_extensions = ('.png', '.jpg', '.jpeg')
all_images = [f for f in os.listdir(source_dir) if f.lower().endswith(image_extensions)]
random.shuffle(all_images)

# 3. Разделяем 80/20
split_idx = int(len(all_images) * 0.8)
train_images = all_images[:split_idx]
val_images = all_images[split_idx:]

print(f" Всего изображений: {len(all_images)}")
print(f" Train: {len(train_images)}, Val: {len(val_images)}\n")

# 4. Функция конвертации JSON → YOLO TXT
def convert_json_to_yolo(json_path, txt_path):
    if not os.path.exists(json_path):
        return False
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Получаем размеры изображения
    image_width = data.get('imageWidth', 1)
    image_height = data.get('imageHeight', 1)
    
    # Получаем список форм (разметка)
    shapes = data.get('shapes', [])
    
    if not shapes:
        return False
    
    # Словарь классов (порядок должен совпадать с class.txt!)
    # Проверьте порядок в вашем JSON файле!
    class_mapping = {
        'game': 0,
        'close_ad': 1,
        'upgrade': 2,
        'bonus': 3
    }
    
    with open(txt_path, 'w') as out:
        for shape in shapes:
            label = shape.get('label', '')
            points = shape.get('points', [])
            
            if label not in class_mapping:
                continue
            
            class_id = class_mapping[label]
            
            # X-AnyLabeling сохраняет прямоугольники как 4 точки
            # Берем min/max координаты
            x_coords = [p[0] for p in points]
            y_coords = [p[1] for p in points]
            
            x_min = min(x_coords)
            x_max = max(x_coords)
            y_min = min(y_coords)
            y_max = max(y_coords)
            
            # Конвертируем в формат YOLO: class_id x_center y_center width height (нормализованные)
            x_center = ((x_min + x_max) / 2) / image_width
            y_center = ((y_min + y_max) / 2) / image_height
            width = (x_max - x_min) / image_width
            height = (y_max - y_min) / image_height
            
            out.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
    
    return True

# 5. Копируем и конвертируем
def process_image(image_name, split_type):
    # Копируем картинку
    src_img = os.path.join(source_dir, image_name)
    dst_img = os.path.join(target_dir, "images", split_type, image_name)
    shutil.copy2(src_img, dst_img)
    
    # Ищем соответствующий JSON файл
    base_name = os.path.splitext(image_name)[0]
    json_name = base_name + ".json"
    json_path = os.path.join(source_dir, json_name)
    
    # Создаем TXT файл
    txt_name = base_name + ".txt"
    txt_path = os.path.join(target_dir, "labels", split_type, txt_name)
    
    if convert_json_to_yolo(json_path, txt_path):
        print(f" {image_name} → конвертирован")
    else:
        print(f" {image_name} → нет разметки")

# 6. Запускаем обработку
for img in train_images:
    process_image(img, "train")

for img in val_images:
    process_image(img, "val")

print("\n Готово! Данные распределены и конвертированы в формат YOLO.")