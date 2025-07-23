import cv2
import os
import pickle
import numpy as np
import face_recognition
import cvzone
import json
from supabase import create_client, Client
from datetime import datetime
import urllib.request

# Load config and connect to Supabase
with open("serviceAccountKey.json", "r") as f:
    config = json.load(f)
SUPABASE_URL = config["SUPABASE_URL"]
SUPABASE_KEY = config["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Camera setup
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

# Load background and mode images
imgBackground = cv2.imread('Resources/Background.jpg')
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = [cv2.resize(cv2.imread(os.path.join(folderModePath, path)), (505, 658)) for path in modePathList]

# Load encodings
with open('EncodeFile.p', 'rb') as file:
    encodeListKnown, studentIds = pickle.load(file)

# Initial variables
modeType = 0
counter = 0
id = -1
student_img = []
student_info = {}

while True:
    success, img = cap.read()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBackground[186:186 + 480, 32:32 + 640] = img
    imgBackground[29:29 + 658, 745:745 + 505] = imgModeList[modeType]

    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 32 + x1, 186 + y1, x2 - x1, y2 - y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                id = studentIds[matchIndex]

                if counter == 0:
                    response = supabase.table("students").select("*").eq("id", id).execute()
                    if response.data:
                        student_info = response.data[0]
                        image_filename = f"{id}.jpg"
                        image_url = supabase.storage.from_("images").get_public_url(f"images/{image_filename}")
                        try:
                            resp = urllib.request.urlopen(image_url)
                            image_np = np.asarray(bytearray(resp.read()), dtype=np.uint8)
                            student_img = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
                        except:
                            student_img = np.zeros((185, 322, 3), dtype=np.uint8)

                    datetimeObject = datetime.strptime(student_info['last_attendance_time'], "%Y-%m-%dT%H:%M:%S")
                    secondElapsed = (datetime.now() - datetimeObject).total_seconds()

                    if secondElapsed > 45:
                        modeType = 1  # show detail page
                    else:
                        modeType = 3  # already marked
                    counter = 1

        if 1 <= counter < 6 and modeType == 1:
            imgBackground[29:29 + 658, 745:745 + 505] = imgModeList[1]
            if student_info:
                cv2.putText(imgBackground, str(student_info['total_attendance']), (835, 118), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 1)
                cv2.putText(imgBackground, str(student_info['course']), (1013, 514), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 1)
                cv2.putText(imgBackground, str(student_info['major']), (1020, 575), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 1)
                cv2.putText(imgBackground, str(id), (1013, 447), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 1)
                cv2.putText(imgBackground, str(student_info['year']), (1172, 648), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 1)
                cv2.putText(imgBackground, str(student_info['starting_year']), (908, 648), cv2.FONT_HERSHEY_COMPLEX, 0.8, (255, 255, 255), 1)
                (w, h), _ = cv2.getTextSize(student_info['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                offset = (505 - w) // 2
                cv2.putText(imgBackground, str(student_info['name']), (750 + offset, 390), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 1)
                student_img = cv2.resize(student_img, (322, 185))
                imgBackground[170:170 + 185, 840:840 + 322] = student_img

        if counter == 6 and modeType == 1:
            # Time to update attendance
            new_attendance = student_info['total_attendance'] + 1
            now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            supabase.table("students").update({
                "total_attendance": new_attendance,
                "last_attendance_time": now_time
            }).eq("id", id).execute()

            updated_data = supabase.table("students").select("*").eq("id", id).execute()
            if updated_data.data:
                student_info = updated_data.data[0]

            modeType = 2  # marked

        if modeType in [2, 3] and 6 < counter <= 15:
            imgBackground[29:29 + 658, 745:745 + 505] = imgModeList[modeType]
            # ❌ Don't show data on modes 2 or 3

        counter += 1
        if counter >= 20:
            counter = 0
            modeType = 0
            id = -1
            student_info = {}
            student_img = []
    else:
        modeType = 0
        counter = 0

    cv2.imshow("Webcam", img)
    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)
