import os
from deepface import DeepFace

# def detect_face(image_path):
#     """Extracts face and checks for anti-spoofing"""
#     try:
#         face_objs = DeepFace.extract_faces(img_path=image_path, anti_spoofing=True)
#         return all(face_obj["is_real"] for face_obj in face_objs)
#     except Exception as e:
#         return str(e)

def verify_faces(img1_path, img2_path):
    """Compares two faces and returns verification status"""
    try:
        result = DeepFace.verify(img1_path=img1_path, img2_path=img2_path, model_name="Facenet512")
        return result["verified"]
    except Exception as e:
        return str(e)
