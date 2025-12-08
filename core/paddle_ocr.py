from paddleocr import PaddleOCR

class PaddleOCRWrapper:
    def __init__(self):
        self.ocr = PaddleOCR(
            lang="en",
            use_doc_orientation_classify=False, 
            use_doc_unwarping=False,
            use_textline_orientation=False,
        )
    
    def get_sort_key_robust(self, item, y_tolerance=30):
        # item is the tuple: (line, rec_score, rec_polys)
        polys = item[2]
        
        try:
            # Calculate the average Y-coordinate (centroid Y) for better stability
            # Sum of all 4 Y-coordinates divided by 4
            avg_y = sum(p[1] for p in polys) / len(polys)
            
            # Use Y-tolerance to create a "virtual row index"
            # Text within 'y_tolerance' will get the same row_index
            row_index = int(avg_y // y_tolerance) 
            
            # Use the Top-Left X-coordinate for Left-to-Right order
            x_coord = polys[0][0]
            
            # Primary sort: row_index (top-to-bottom)
            # Secondary sort: x_coord (left-to-right)
            return (row_index, x_coord)
            
        except (IndexError, TypeError, ZeroDivisionError):
            # Fallback for malformed box data
            return (float('inf'), float('inf'))
        
    def sort_ocr_tuples(self, ocr_data):
        """
        Sorts OCR result tuples (line, score, polys) using Y-axis tolerance
        to group text into logical rows before sorting by X.
        
        Args:
            ocr_data (list): List of (text, score, polys) tuples.
            y_tolerance (int): Maximum vertical distance (in pixels) for two
                            lines to be considered part of the same row.
        """
        sorted_data = sorted(ocr_data, key=lambda item: self.get_sort_key_robust(item, y_tolerance=30))
        ocr_text_lines = []
        
        for item in sorted_data:
            text = item[0]
            ocr_text_lines.append(text + ' ') 
            
        # Join the final list into the output string
        ocr_text = "".join(ocr_text_lines).strip()
        
        return ocr_text

    def predict(self, img_path):
        result = self.ocr.predict(
            img_path
        )

        document = []
        # Visualize the results and save the JSON results
        for res in result:
            for i, line in enumerate(res['rec_texts']):
                if(res['rec_scores'][i] < 0.5):
                    continue
                document.append((line, res['rec_scores'][i], res['rec_polys'][i]))

        return self.sort_ocr_tuples(document)
