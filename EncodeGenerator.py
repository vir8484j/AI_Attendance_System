import cv2
import face_recognition
import pickle
import os
from supabase import create_client, Client
import json

with open("serviceAccountKey.json", "r") as f:
    config = json.load(f)

SUPABASE_URL = config["SUPABASE_URL"]
SUPABASE_KEY = config["SUPABASE_KEY"]
STORAGE_BUCKET = "images"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


#Importing the student images
folderPath='Images'
PathList=os.listdir(folderPath)
imgList=[]
studentIds=[]
for path in PathList:
    imgList.append(cv2.imread(os.path.join(folderPath,path)))
    studentIds.append(os.path.splitext(path)[0])

    #Prepare the upload file path for Supabase
    fileName = f"{folderPath}/{path}"  # Local file path
    destination_path = f"images/{path}"  # Path in Supabase Storage

    try:
        # Upload the image
        with open(fileName, "rb") as f:
            response = supabase.storage.from_(STORAGE_BUCKET).upload(destination_path, f)

        # ✅ Get the public URL
        public_url = supabase.storage.from_(STORAGE_BUCKET).get_public_url(destination_path)
        print(f"✅ Uploaded: {path} → {public_url}")

    except Exception as e:
        print(f"❌ Error uploading {path}: {e}")
else:
    print(f"⚠️ Skipping invalid image: {path}")
print(studentIds)


def findEncodings(imagesList):
    encodeList = []
    for idx, img in enumerate(imagesList):
        try:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            faces = face_recognition.face_locations(img_rgb)

            if len(faces) == 0:
                print(f"❌ No face detected in image {idx} (skipped)")
                continue

            encodes = face_recognition.face_encodings(img_rgb, faces)
            if encodes:
                encodeList.append(encodes[0])
                print(f"✅ Encoding successful for image {idx}")
            else:
                print(f"⚠️ Encoding failed for image {idx}")
        except Exception as e:
            print(f"⚠️ Error processing image {idx}: {e}")

    return encodeList


encodeListKnown=findEncodings(imgList)
encodeListKnownWithIds=[encodeListKnown,studentIds]

file=open("EncodeFile.p",'wb')
pickle.dump(encodeListKnownWithIds,file)
file.close()
print("File saved")