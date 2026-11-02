from ultralytics import YOLO


model = YOLO(r'C:\cookie\runs\detect\cookie_detector-12\weights\best.pt')


model.export(format='onnx')

print(" Модель конвертирована!")