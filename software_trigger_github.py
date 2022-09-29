from pypylon import pylon
import cv2
import time
import numpy as np

camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
camera.Open()
# Always Selector first!
camera.TriggerSelector = 'FrameStart'
camera.TriggerMode = 'On'
camera.TriggerSource = 'Software'
camera.TriggerActivation = 'RisingEdge'


print("Trigger mode: ", camera.TriggerMode.Value)
camera.StartGrabbing(pylon.GrabStrategy_OneByOne)
converter = pylon.ImageFormatConverter()

# converting to opencv bgr format
converter.OutputPixelFormat = pylon.PixelType_BGR8packed
converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned


def crop_center_square(img, size):
    h, w = img.shape[:2]
    return img[h // 2 - size // 2:h // 2 + size // 2, w // 2 - size // 2:w // 2 + size // 2:]


img = []
i = 0
while camera.IsGrabbing():
    print("trigger")

    camera.TriggerSoftware.Execute()
    grabResult = camera.RetrieveResult(15000, pylon.TimeoutHandling_ThrowException)

    if grabResult.GrabSucceeded():
        print(i, ". image taken")
        image = converter.Convert(grabResult)
        # release early
        grabResult.Release()

        image = image.GetArray()
        file = f"image{i}"

        image = crop_center_square(image, 600)
        img.append(image)
        filename = file + ".jpg"
        cv2.imwrite(filename, image)
        time.sleep(1)
        i += 1
        if i == 3:
            vis = np.concatenate(img, axis=1)
            cv2.imwrite("final_image.jpg", vis)
            break

camera.StopGrabbing()
camera.Close()