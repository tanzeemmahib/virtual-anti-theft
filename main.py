import cv2
import time
import yagmail

# CONFIGURE YOUR EMAIL SETTINGS
SENDER_EMAIL = 'your.email@gmail.com'
APP_PASSWORD = 'your_app_password'  # You need to enable 'App Passwords' in Gmail
RECEIVER_EMAIL = 'your.email@gmail.com'  # Or your phone's email-to-text

# Set up email sender
yag = yagmail.SMTP(SENDER_EMAIL, APP_PASSWORD)

# Start webcam
cam = cv2.VideoCapture(0)
time.sleep(2)  # Let camera warm up

first_frame = None

while True:
    # Read frame from camera
    ret, frame = cam.read()
    if not ret:
        break

    # Convert frame to grayscale + blur
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # Save the first frame as reference background
    if first_frame is None:
        first_frame = gray
        continue

    # Compute the difference between current frame and background
    delta_frame = cv2.absdiff(first_frame, gray)
    thresh = cv2.threshold(delta_frame, 25, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)

    # Find movement contours
    contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        if cv2.contourArea(contour) < 1000:
            continue

        print("⚠️ Motion Detected!")
        # Save frame to file
        cv2.imwrite("alert.png", frame)

        # Send alert via email
        yag.send(
            to=RECEIVER_EMAIL,
            subject="Motion Detected!",
            contents="Someone moved near your laptop!",
            attachments="alert.png"
        )

        # Optional: stop after one alert
        cam.release()
        cv2.destroyAllWindows()
        exit()

    # Optional: show feed while testing
    # cv2.imshow("Security Feed", frame)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()
