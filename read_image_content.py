#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
from pyzbar import pyzbar
from PIL import Image
import numpy as np

def read_qr_code(image_path):
    """
    Đọc QR code từ ảnh PNG
    
    Args:
        image_path (str): Đường dẫn đến file ảnh
        
    Returns:
        list: Danh sách các QR code được tìm thấy
    """
    try:
        # Đọc ảnh bằng OpenCV
        image = cv2.imread(image_path)
        
        if image is None:
            raise ValueError(f"Không thể đọc ảnh từ: {image_path}")
        
        # Thử decode trực tiếp trước
        print("🔍 Bước 1: Thử đọc QR code từ ảnh gốc...")
        qr_codes = pyzbar.decode(image)
        
        # Nếu không tìm thấy QR code, thử preprocessing
        if not qr_codes:
            print("❌ Ảnh gốc: Không tìm thấy QR code")
            
            # Chuyển sang grayscale
            print("🔍 Bước 2: Chuyển sang grayscale...")
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            qr_codes = pyzbar.decode(gray)
            
            # Nếu vẫn không tìm thấy, thử với các kỹ thuật khác
            if not qr_codes:
                print("❌ Grayscale: Không tìm thấy QR code")
                
                # Thử với gaussian blur để giảm noise
                print("🔍 Bước 3: Áp dụng Gaussian Blur...")
                blurred = cv2.GaussianBlur(gray, (5, 5), 0)
                qr_codes = pyzbar.decode(blurred)
                
                # Thử với adaptive threshold
                if not qr_codes:
                    print("❌ Gaussian Blur: Không tìm thấy QR code")
                    
                    print("🔍 Bước 4: Áp dụng Adaptive Threshold...")
                    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
                    qr_codes = pyzbar.decode(thresh)
                
                    # Thử với OTSU threshold
                    if not qr_codes:
                        print("❌ Adaptive Threshold: Không tìm thấy QR code")
                        
                        print("🔍 Bước 5: Áp dụng OTSU Threshold...")
                        _, thresh_otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                        qr_codes = pyzbar.decode(thresh_otsu)
                        
                        if not qr_codes:
                            print("❌ OTSU Threshold: Không tìm thấy QR code")
                        else:
                            print("✅ THÀNH CÔNG với OTSU Threshold!")
                    else:
                        print("✅ THÀNH CÔNG với Adaptive Threshold!")
                else:
                    print("✅ THÀNH CÔNG với Gaussian Blur!")
            else:
                print("✅ THÀNH CÔNG với Grayscale!")
        else:
            print("✅ THÀNH CÔNG với ảnh gốc!")
        
        results = []
        for qr_code in qr_codes:
            try:
                # Lấy dữ liệu và loại của QR code
                qr_data = qr_code.data.decode('utf-8')
                qr_type = qr_code.type
                
                # Lấy tọa độ của QR code
                points = qr_code.polygon
                if len(points) >= 3:  # Có thể là 3 hoặc 4 điểm
                    # Tạo bounding box
                    x_coords = [point.x for point in points]
                    y_coords = [point.y for point in points]
                    x_min, x_max = min(x_coords), max(x_coords)
                    y_min, y_max = min(y_coords), max(y_coords)
                    
                    results.append({
                        'data': qr_data,
                        'type': qr_type,
                        'bbox': (x_min, y_min, x_max, y_max),
                        'points': [(point.x, point.y) for point in points]
                    })
            except UnicodeDecodeError:
                # Nếu không decode được UTF-8, thử với các encoding khác
                try:
                    qr_data = qr_code.data.decode('latin-1')
                    results.append({
                        'data': qr_data,
                        'type': qr_code.type,
                        'raw_data': qr_code.data
                    })
                except:
                    # Nếu vẫn không decode được, lưu raw data
                    results.append({
                        'data': str(qr_code.data),
                        'type': qr_code.type,
                        'raw_data': qr_code.data
                    })
        
        return results
        
    except Exception as e:
        print(f"Lỗi khi đọc QR code: {e}")
        import traceback
        traceback.print_exc()
        return []

def main():
    """
    Hàm chính để test script
    """
    image_path = "image (2).png"
    
    print(f"Đang đọc QR code từ ảnh: {image_path}")
    print("-" * 50)
    
    qr_results = read_qr_code(image_path)
    
    if qr_results:
        print(f"Tìm thấy {len(qr_results)} QR code(s):")
        for i, qr in enumerate(qr_results, 1):
            print(f"\nQR Code #{i}:")
            print(f"  Loại: {qr['type']}")
            print(f"  Nội dung: {qr['data']}")
            print(f"  Vị trí: {qr['bbox']}")
    else:
        print("Không tìm thấy QR code trong ảnh hoặc có lỗi xảy ra")

if __name__ == "__main__":
    main()