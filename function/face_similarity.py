import dlib
from skimage import io
import numpy as np


def compute_face_similarity(img1, img2):
    # 初始化dlib的人臉識別器
    face_detector = dlib.get_frontal_face_detector()
    shape_predictor = dlib.shape_predictor("../models/shape_predictor_68_face_landmarks.dat")
    face_recognizer = dlib.face_recognition_model_v1("../models/dlib_face_recognition_resnet_model_v1.dat")

    # 讀取圖像並檢測人臉
    image1 = io.imread(img1)
    image2 = io.imread(img2)

    face1 = face_detector(image1, 1)[0]
    face2 = face_detector(image2, 1)[0]

    # 提取人臉特徵
    face1_shape = shape_predictor(image1, face1)
    face2_shape = shape_predictor(image2, face2)
    face1_descriptor = face_recognizer.compute_face_descriptor(image1, face1_shape)
    face2_descriptor = face_recognizer.compute_face_descriptor(image2, face2_shape)

    # 計算人臉相似度
    face_distance = np.linalg.norm(np.array(face1_descriptor) - np.array(face2_descriptor))

    # 轉換為相似度得分（0-1之間的值，越大表示越相似）
    score = 1 - face_distance

    return score


if __name__ == "__main__":
    # 測試
    image1_path = "~/Pictures/origin.png"
    image2_path = "~/Pictures/test3.png"
    similarity_score = compute_face_similarity(image1_path, image2_path)
    print("相似度：", similarity_score)
