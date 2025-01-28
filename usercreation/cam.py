import cv2


name = input("Enter student's first and last name: ")
file_name = name.replace(" ", "_")

# Get default video gamera
camera = cv2.VideoCapture(0)

# Get the proper resolution
res_height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
res_width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))

capturing = True
pic_key = 0

while capturing:
    ret, frame = camera.read()

    # Video if a snapshot hasnt been taken
    if pic_key != ord('c'):
        cv2.imshow('Camera', frame)
        pic_key = cv2.waitKey(1)
    else:
        file_path = file_name + ".jpg"
        cv2.imwrite(file_path, frame)
        redo = cv2.waitKey(0)
        print("captured")
        if redo == ord('y'):
            print("redone")
            pic_key = 0
        else:
            print("pic taken, quiting")
            break
    # Break loop
    if pic_key == ord('q'):
        print("quiting")
        break

# Release the capture and writer objects
camera.release()
cv2.destroyAllWindows()