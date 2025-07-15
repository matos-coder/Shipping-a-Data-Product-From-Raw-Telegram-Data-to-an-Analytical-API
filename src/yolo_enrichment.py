# src/yolo_enrichment.py
import csv
import os
from pathlib import Path
from ultralytics import YOLO

def enrich_images_with_yolo():
    """
    Scans for images in the data lake, runs YOLOv8 object detection,
    and saves the structured results to a CSV file for dbt to process.
    """
    # Define project paths using os.path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    image_data_path = os.path.join(project_root, "data", "raw", "images")
    seeds_path = os.path.join(project_root, "telegram_analytics", "seeds")
    output_csv_path = os.path.join(seeds_path, "image_detections.csv")

    # Ensure the output directory for the seed file exists
    os.makedirs(seeds_path, exist_ok=True)

    # Load the pre-trained YOLOv8 model.
    try:
        model = YOLO('yolov8n.pt')
        print("YOLOv8 model loaded successfully.")
    except Exception as e:
        print(f"Failed to load YOLOv8 model. Have you run 'pip install ultralytics'? Error: {e}")
        return

    # Prepare the CSV file to store detection results
    try:
        with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            # Write the header row for the CSV (message_id is now included)
            writer.writerow(['image_path', 'message_id', 'channel_id', 'detected_object_class_id', 'detected_object_name', 'confidence_score', 'bounding_box_xyxy'])

            print(f"Processing images from: {image_data_path}")
            
            image_files = []
            for root, _, files in os.walk(image_data_path):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        image_files.append(os.path.join(root, file))

            if not image_files:
                print("Warning: No images found to process. Make sure your scraping task is saving images with message IDs.")
                return

            # Run detection on all images
            results = model(image_files, stream=True)

            # Process results for each image
            for result in results:
                if result.boxes is None:
                    continue

                current_image_path = result.path
                
                # --- THIS IS THE MODIFIED PART ---
                # Extract message_id and channel_id from the file path
                # Assumes path format: .../data/raw/images/YYYY-MM-DD/channel_id/message_id.jpg
                try:
                    p = Path(current_image_path)
                    message_id = p.stem  # e.g., '18523' from '18523.jpg'
                    channel_id = p.parent.name # e.g., 'lobelia4cosmetics'
                except Exception as e:
                    print(f"Warning: Could not parse message_id/channel_id from path: {current_image_path}. Error: {e}")
                    continue
                # --- END OF MODIFIED PART ---

                # Iterate through each detected object in the image
                for box in result.boxes:
                    class_id = int(box.cls[0])
                    class_name = model.names[class_id]
                    confidence = float(box.conf[0])
                    bounding_box = box.xyxy[0].tolist() # [x1, y1, x2, y2]

                    # Write the detection details as a new row in the CSV
                    writer.writerow([
                        current_image_path,
                        message_id,
                        channel_id,
                        class_id,
                        class_name,
                        confidence,
                        str(bounding_box) # Store bounding box as a string
                    ])
            
            print(f"Successfully processed {len(image_files)} images.")
            print(f"Detection results saved to: {output_csv_path}")

    except Exception as e:
        print(f"An error occurred during the enrichment process: {e}")

if __name__ == "__main__":
    enrich_images_with_yolo()
