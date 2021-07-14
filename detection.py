from deepface import DeepFace
from retinaface import RetinaFace
import matplotlib.pyplot as plt
import cv2
from PIL import Image
import numpy as np
import pandas as pd
from pathlib import Path
import os

THRESHOLD = 0.4


HOME = str(Path.home())
os.system(f"sudo cp ./retinaface.h5 {HOME}/.deepface/weights/")
os.system(f"sudo cp ./facenet_weights.h5 {HOME}/.deepface/weights/")


faces = RetinaFace.detect_faces('./Test/people.jpg', 0.95)
img = plt.imread('./Test/people.jpg')

model = DeepFace.build_model('Facenet')

for face_info in faces.values():
	facial_area = face_info['facial_area']
	landmarks = face_info['landmarks']
	face = Image.fromarray(img).crop((facial_area[0], facial_area[1], facial_area[2], facial_area[3]))
	df = DeepFace.find(np.asarray(face), './DB', 'Facenet', model=model, enforce_detection=False)
	if df.shape[0] > 0:
		df = df.sort_values(by=['Facenet_cosine'])
		if df['Facenet_cosine'][0] < THRESHOLD:
			img = cv2.rectangle(img, (facial_area[2], facial_area[3])
				, (facial_area[0], facial_area[1]), (200, 200, 200), 1)

			cv2.putText(img, df['identity'][0].split('/')[-1].split('.')[0].split('_')[0]
				, (facial_area[0],facial_area[3]), cv2.FONT_HERSHEY_SIMPLEX
				, 0.6, color=(200,200,200))


plt.imshow(img)
plt.imsave('people_output.jpg', img)