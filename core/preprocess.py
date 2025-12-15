import cv2

class ImagePreProcessor:
    def __init__(self):
        pass
    
    def preprocess(self, image_path, temp_path='temp_processed_image.png'):
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Despeckling using bilateral filtering to preserve edges
        gray = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)
        # Noise reduction using median filtering
        gray = cv2.medianBlur(gray, 3)
        # Adaptive thresholding for better binarization
        gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                    cv2.THRESH_BINARY, 29, 3)
        # Edge enhancement using unsharp masking
        gaussian = cv2.GaussianBlur(gray, (9, 9), 10.0)
        gray = cv2.addWeighted(gray, 1.5, gaussian, -0.5, 0)

        cv2.imwrite(temp_path, gray)
        return temp_path