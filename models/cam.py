import cv2


name = input("Enter student's first and last name: ")
file_name = name.replace(" ", "_")

# Get default video gamera
camera = cv2.VideoCapture(0)

# Get the proper resolution
res_height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
res_width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))

capturing = True
pic_taken = False

while capturing:

    # key = cv2.waitKey()

    ret, frame = camera.read()

    # Video if a snapshot hasnt been taken
    if not pic_taken:
        cv2.imshow('Camera', frame)

    if cv2.waitKey(1) == ord('c'):
        pic_taken = True
        file_path = file_name + ".jpg"
        cv2.imwrite(file_path, frame)
        # redo = cv2.waitKey(500)
        # if redo == ord('y'):
        #     pic_taken == False
        # else:
        #     break
            
        

    # Break loop
    if cv2.waitKey(1) == ord('q'):
        break

# Release the capture and writer objects
camera.release()
cv2.destroyAllWindows()