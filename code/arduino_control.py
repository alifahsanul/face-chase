import cv2
import serial
import time
import numpy as np
import function_library as myfunc

# Initialize serial communication
arduino = serial.Serial('COM7', 9600)  # Replace 'COM3' with your Arduino's port
time.sleep(2)  # Wait for connection to establish

# Load pre-trained DNN model
prototxt_path = "code/assets/deploy.prototxt"  # Path to prototxt file
model_path = "code/assets/res10_300x300_ssd_iter_140000.caffemodel"  # Path to caffemodel file
net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)

# Open webcam
cap = cv2.VideoCapture(0)

# Initial servo angles
angle_pan, angle_tilt = 90, 90
prev_angle_pan, prev_angle_tilt = angle_pan, angle_tilt
error_pan, error_tilt = 0, 0

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break
        h, w = frame.shape[:2]

        blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104.0, 177.0, 123.0))
        net.setInput(blob)
        detections = net.forward()

        # If a face is detected, calculate the position
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]  # Confidence score

            # Filter out weak detections by confidence threshold
            if confidence > 0.4:
                # Extract bounding box coordinates
                box = detections[0, 0, i, 3:7] * [w, h, w, h]
                (x, y, x2, y2) = box.astype("int")

                # Draw rectangle around the face
                cv2.rectangle(frame, (x, y), (x2, y2), (255, 0, 0), 2)

                # Calculate the center of the face
                face_center_x = (x + x2) // 2
                face_center_y = (y + y2) // 2

                # Adjust servo angles based on face position
                frame_center_x  = frame.shape[1] // 2
                frame_center_y = frame.shape[0] // 2

                delta_x = frame_center_x - face_center_x
                if abs(delta_x) < 30:
                    target_angle_pan = prev_angle_pan
                else:
                    target_angle_pan = 90 + delta_x
                angle_pan, error_pan = myfunc.pid_controller(target_angle_pan, prev_angle_pan, error_pan)

                delta_y = face_center_y - frame_center_y
                if abs(delta_y) < 30:
                    target_angle_tilt = prev_angle_tilt
                else:
                    target_angle_tilt = 90 + delta_y
                angle_tilt, error_tilt = myfunc.pid_controller(target_angle_tilt, prev_angle_tilt, error_tilt)

                adj_angle_pan = int(min(max(0, angle_pan), 180))
                adj_angle_tilt = int(min(max(0, angle_tilt), 180))

                text_color = (0, 0, 0) #bgr
                cv2.putText(frame, f'confidence: {confidence * 100:.0f}%',
                            (x, (y+y2)//2), cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)
                cv2.putText(frame, f'target pan: {target_angle_pan:.1f}, angle_pan: {angle_pan:.1f}',
                            (x-70, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)
                cv2.putText(frame, f'delta_x: {delta_x:.1f}, prev_angle_pan: {prev_angle_pan:.1f}',
                            (x-70, y-20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)


                cv2.putText(frame, f'target tilt: {target_angle_tilt:.1f}, angle_tilt: {angle_tilt:.1f}',
                            (x-70, y2+5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)
                cv2.putText(frame, f'delta_y: {delta_y:.1f}, prev_angle_tilt: {prev_angle_tilt:.1f}',
                            (x-70, y2+20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)

                prev_angle_pan, prev_angle_tilt = adj_angle_pan, adj_angle_tilt
                # Send the new angles to Arduino
                command = f"{adj_angle_pan},{adj_angle_tilt}\n"
                arduino.write(command.encode('utf-8'))
                break  # Process only the first detected face

        # Display the frame
        cv2.imshow('Face Tracking', frame)

        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
except Exception as e:
    print("Error:", e)
finally:
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    arduino.close()
