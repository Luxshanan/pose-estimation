import cv2
import mediapipe as mp
import numpy as np
import uuid

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


def process_video(video_path, is_left_handed):
    cap = cv2.VideoCapture(video_path)

    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    frame_rate = cap.get(5)
    size = (frame_width, frame_height)

    result_video_file_path = "result_videos/" + uuid.uuid4().hex + 'result.mp4'
    # result video is stored in given path
    result = cv2.VideoWriter(result_video_file_path,
                             cv2.VideoWriter_fourcc(*'mp4v'),
                             frame_rate, size)
    ## Setup mediapipe instance
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if ret == False: break;

            # Recolor image to RGB
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False

            # Make detection
            results = pose.process(image)

            # Recolor back to BGR
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            # Extract landmarks
            try:
                landmarks = results.pose_landmarks.landmark

                # Get coordinates
                elbow, shoulder, wrist = get_coordinates_for_elbow_shoulder_wrist(is_left_handed, landmarks)

                # Calculate angle
                angle = calculate_angle(shoulder, elbow, wrist)

                # Visualize angle
                cv2.putText(image, str(angle),
                            tuple(np.multiply(elbow, [640, 480]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                            )

                is_legal_delivery = "Legal Ball" if 165 <= angle <= 180 else "No Ball"
                put_legal_delivery_result(is_legal_delivery, image)

            except:
                pass

            # Render detections
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                      mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                                      mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
                                      )

            #cv2.imshow('Mediapipe Feed', image)    #uncomment to view processing in real time
            result.write(image)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

        cap.release()
        result.release()
        cv2.destroyAllWindows()
        return result_video_file_path


def get_coordinates_for_elbow_shoulder_wrist(is_left_handed, landmarks):
    if is_left_handed:
        shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                    landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                 landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                 landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
    else:
        shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                    landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                 landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
        wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                 landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
    return elbow, shoulder, wrist


def calculate_angle(a, b, c):
    a = np.array(a)  # First
    b = np.array(b)  # Mid
    c = np.array(c)  # End

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle


def put_legal_delivery_result(label, img):

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    thickness = 2

    (text_width, text_height), _ = cv2.getTextSize(label, font, font_scale, thickness)
    x = 10
    y = text_height + 10

    text_color = (0, 255, 0) if label == "Legal Ball"  else (0, 0, 255)
    # Draw the text on the image
    cv2.putText(img, label, (x, y), font, font_scale, text_color, thickness)