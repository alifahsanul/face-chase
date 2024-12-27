import cv2

# Load pre-trained DNN model
prototxt_path = "code/assets/deploy.prototxt"  # Path to prototxt file
model_path = "code/assets/res10_300x300_ssd_iter_140000.caffemodel"  # Path to caffemodel file

net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)

# Open the webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Get frame height and width
    h, w = frame.shape[:2]

    # Prepare the frame for DNN
    blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104.0, 177.0, 123.0))

    # Set the blob as input to the network
    net.setInput(blob)

    # Perform forward pass to detect faces
    detections = net.forward()

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]  # Confidence score

        # Filter out weak detections by confidence threshold
        if confidence > 0.7:
            # Extract bounding box coordinates
            box = detections[0, 0, i, 3:7] * [w, h, w, h]
            (x1, y1, x2, y2) = box.astype("int")

            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Display confidence score
            text = f"{confidence * 100:.2f}%"
            cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Display the frame
    cv2.imshow("Face Detection (DNN)", frame)

    # Exit if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
