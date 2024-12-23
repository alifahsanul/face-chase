import cv2
import serial
import time

# Initialize serial communication
arduino = serial.Serial('COM7', 9600)  # Replace 'COM3' with your Arduino's port
time.sleep(2)  # Wait for connection to establish

# Load Haar Cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Open webcam
cap = cv2.VideoCapture(0)

# Initial servo angles
angle_pan, angle_tilt = 90, 90
prev_angle_pan, prev_angle_tilt = angle_pan, angle_tilt

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
        if len(faces) > 0:
            face = sorted(faces, key=lambda x: x[2] * x[3], reverse=True)
        else:
            face = faces

        # If a face is detected, calculate the position
        for (x, y, w, h) in face:
            # Draw rectangle around the face
            
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            # Calculate the center of the face
            face_center_x = x + w // 2
            face_center_y = y + h // 2

            # Adjust servo angles based on face position
            frame_center_x  = frame.shape[1] // 2
            frame_center_y = frame.shape[0] // 2

            delta_x = frame_center_x - face_center_x
            angle_pan = int(90 + delta_x * 0.5)

            delta_y = frame_center_y - face_center_y
            angle_tilt = int(90 + delta_y * 0.4)

            adj_angle_pan = min(max(0, angle_pan), 180)
            
            adj_angle_tilt = min(max(0, angle_tilt), 180)

            text_color = (0, 100, 130) #bgr
            cv2.putText(frame, f'fa_x: {face_center_x}, fa_y:{face_center_y}, fr_x: {frame_center_x}, fr_y:{frame_center_y}', (x, y - 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)
            cv2.putText(frame, f'x: {x}, y :{y}, w:{w}, h:{h}', (x, y - 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)

            cv2.putText(frame, f'pan:{angle_pan}, adj:{adj_angle_pan}, tilt:{angle_tilt}, adj: {adj_angle_tilt}', (x, y + h + 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)
            cv2.putText(frame, f'delta_x: {delta_x}, delta_y:{delta_y}', (x, y + h + 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)

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
