import cv2

cap = cv2.VideoCapture('http://192.168.1.157:4747/video')

while(True):
    ret, frame = cap.read()
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break