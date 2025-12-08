import torch 
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
import os

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

class DoctrOCRWrapper:
    def __init__(self):
        """Initializes the Doctr OCR model."""
        self.predictor = ocr_predictor(
            'db_resnet50', 
            'crnn_vgg16_bn', 
            pretrained=True, 
            assume_straight_pages=False, 
            preserve_aspect_ratio=True,
            det_bs=4, reco_bs=1024
        )

    def predict(self, path, type='image'):
        """Performs OCR on the given image and returns the corrected text."""
        # Re-run prediction on the original image and print bounding boxes for each word
        if type == 'image':
            doc_for_boxes = DocumentFile.from_images(path)
        elif type == 'pdf':
            doc_for_boxes = DocumentFile.from_pdf(path)
        result_for_boxes = self.predictor(doc_for_boxes)
        
        words = []
        boxes = []

        TRESHOLD = 0.55
        # 'result_for_boxes' is a Document object
        output_dict = result_for_boxes.export()
        # Now 'output_dict' is a dictionary, and you can access it
        page_dims = output_dict['pages'][0]['dimensions']
        h, w = page_dims
        # Iterate through blocks, lines, and words to get their bboxes
        for block in output_dict['pages'][0]['blocks']:
            for line in block['lines']:
                for word in line['words']:
                    if word['confidence'] < TRESHOLD:
                        continue
                    # 'geometry' holds the relative coordinates
                    rel_bbox = word['geometry']
                    value = word['value']
                    
                    # Text correction
                    if len(value.strip()) == 0:
                        continue
                    # value = spell.sympspell_correction(value)
                    # Unpack relative coordinates

                    # rel_bbox is a tuple of points, e.g., ((x1, y1), (x2, y2), ...)
                    if len(rel_bbox) == 2:
                        # Standard 2-point case: ((xmin, ymin), (xmax, ymax))
                        (xmin, ymin), (xmax, ymax) = rel_bbox
                    else:
                        # Rotated 4-point case: ((x1, y1), (x2, y2), (x3, y3), (x4, y4))
                        # We find the min/max of all x and y coords to get the upright box
                        
                        # Get all x coordinates: [x1, x2, x3, x4]
                        x_coords = [point[0] for point in rel_bbox]
                        # Get all y coordinates: [y1, y2, y3, y4]
                        y_coords = [point[1] for point in rel_bbox]
                        
                        xmin = min(x_coords)
                        ymin = min(y_coords)
                        xmax = max(x_coords)
                        ymax = max(y_coords)

                    # Calculate absolute pixel coordinates
                    abs_xmin = int(xmin * w)
                    abs_ymin = int(ymin * h)
                    abs_xmax = int(xmax * w)
                    abs_ymax = int(ymax * h)
                    
                    # Normalize to 0-1000 scale
                    norm_x_top_left = int((abs_xmin / w) * 1000)
                    norm_y_top_left = int((abs_ymin / h) * 1000)
                    norm_x_bottom_right = int((abs_xmax / w) * 1000)
                    norm_y_bottom_right = int((abs_ymax / h) * 1000)
                    
                    # os.system('cls' if os.name == 'nt' else 'clear')

                    words.append(value)
                    boxes.append([norm_x_top_left, norm_y_top_left, norm_x_bottom_right, norm_y_bottom_right])
        return " ".join(words), words, boxes
