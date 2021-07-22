from typing import final
import psycopg2
from PIL import Image
from deepface import DeepFace
from retinaface import RetinaFace
import os
import requests
from scipy.spatial.distance import cosine
import pickle
import matplotlib.pyplot as plt
import numpy as np
import cv2

def connect(password, host='localhost', database='Image describe pipe DB', user='postgres'):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(
            host = host,
            database = database,
            user = user,
            password = password)
        print('Connection has established successfully.')

        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def disconnect(conn):
    conn.close()
    print('Database connection closed.')


def add_defining_image(conn, user_email, image_url, who_is_in, model=DeepFace.build_model('Facenet512')):
    os.system('mkdir ./tmp/')
    # os.system(f'touch ./tmp/{who_is_in.split()[0]}.jpg')

    # urllib.urlretrieve(
    #     image_url
    #     ,f'./tmp/{who_is_in.split()[0]}.jpg'
    #     )
    try:
        with open(f'./tmp/{who_is_in.split()[0]}.jpg', 'wb') as f:
            f.write(requests.get(image_url).content)

        img = plt.imread(f'./tmp/{who_is_in.split()[0]}.jpg')
        data = DeepFace.represent(img, 'Facenet512', model)

        cur = conn.cursor()
        cur.execute(
            f'''
            INSERT INTO public.images(user_email, image_url, representation, who_is_in)
            VALUES(
                '{user_email}',
                '{image_url}',
                '{data}',
                '{who_is_in}'
            )
            ON CONFLICT (image_url, user_email) DO UPDATE SET who_is_in = EXCLUDED.who_is_in, representation = EXCLUDED.representation;

            INSERT INTO public.logs(user_email, action, date)
            VALUES(
                '{user_email}',
                'Added/updated a defining image with url ({image_url})',
                NOW()
            )
            '''
        )
        conn.commit()
        cur.close()
        print('Image has been added to database successfully.')
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        os.system(f'rm -rf ./tmp/')


def remove_defining_image(conn, user_email, image_url):
    try:
        cur = conn.cursor()
        cur.execute(
            f'''
            DELETE FROM public.images
            WHERE user_email = '{user_email}' and image_url = '{image_url}'
            RETURNING *
            '''
        )
        images_count = len(cur.fetchall())
        if images_count == 1:
            cur.execute(
                f'''
                INSERT INTO public.logs(user_email, action, date)
                VALUES(
                    '{user_email}',
                    'Removed a defining image with url ({image_url})',
                    NOW()
                )
                '''
            )
            print('The intended image has been removed from database successfully.')
        else:
            cur.execute(
                f'''
                INSERT INTO public.logs(user_email, action, date)
                VALUES(
                    '{user_email}',
                    'Tried to remove a unexisting defining-image with url ({image_url})',
                    NOW()
                )
                '''
            )
            print('There is no image with the input information in the database.')
        
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def add_user(conn, full_name, age, email, password):
    try:
        cur = conn.cursor()
        cur.execute(
            f'''
            INSERT INTO public.users(full_name, age, email, password)
            VALUES(
                '{full_name}',
                {age},
                '{email}',
                '{password}'
            )
            ON CONFLICT (email) DO UPDATE SET full_name = EXCLUDED.full_name, age = EXCLUDED.age, password = EXCLUDED.password;

            INSERT INTO public.logs(user_email, action, date)
            SELECT
                '{email}',
                'User "' ||
                (
                    SELECT full_name
                    FROM public.users
                    WHERE email = '{email}'
                ) || '" updated/added',
                NOW()
            '''
        )
        conn.commit()
        cur.close()
        print('User has been added to database successfully.')
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def remove_user(conn, email):
    try:
        cur = conn.cursor()
        cur.execute(
            f'''
            DELETE FROM public.users
            WHERE email = '{email}'
            RETURNING *
            '''
        )
        users_count = len(cur.fetchall())
        if users_count == 1:
            # cur.execute(
            #     f'''
            #     INSERT INTO public.logs(user_email, action, date)
            #     VALUES(
            #         '{email}',
            #         'Removed the user account',
            #         NOW()
            #     )
            #     '''
            # )
            print('The intended user has been removed from database successfully.')
        else:
            # cur.execute(
            #     f'''
            #     INSERT INTO public.logs(user_email, action, date)
            #     VALUES(
            #         '{email}',
            #         'Tried to remove a nonexisting user',
            #         NOW()
            #     )
            #     '''
            # )
            print('There is no user with the input information in the database.')
        
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def evaluate_image(conn, user_email, image_url, model=DeepFace.build_model('Facenet512')):
    THRESHOLD = 0.6
    os.system('mkdir ./tmp/ ./tmp/DB ./output/')

    try:
        with open('./tmp/img.jpg', 'wb') as f:
            f.write(requests.get(image_url).content)

        img = plt.imread('./tmp/img.jpg')
        faces = RetinaFace.detect_faces(img, 0.95)

        cur = conn.cursor()
        cur.execute(
            f'''
            SELECT who_is_in, representation 
            FROM public.images
            WHERE user_email = '{user_email}'
            '''
        )
        representations_facenet = {}
        fetched_data = cur.fetchall()
        for indx, (who_is_in, representation) in enumerate(fetched_data):
            rep = representation.replace(' ', '')
            rep = rep.replace('[', '')
            rep = rep.replace(']', '')
            rep = list(map(float, rep.split(',')))
            representations_facenet[f'{who_is_in}_{indx}'] = rep
        
        for indx, face_info in enumerate(faces.values()):
            facial_area = face_info['facial_area']
            y1 = max(facial_area[1]-200, 0)
            y2 = min(facial_area[3]+200, img.shape[0]-1)
            x1 = max(facial_area[0]-50, 0)
            x2 = min(facial_area[2]+50, img.shape[1]-1)
            face = img[y1:y2, x1:x2]
            plt.imsave(f'./output/face{indx}.jpg', face)
            
            img_rep = DeepFace.represent(np.asarray(face), 'Facenet512', model, False)
            for person in representations_facenet.keys():
                distance = cosine(representations_facenet[person], img_rep)
                print(person, distance)
                if distance <= THRESHOLD:
                    img = cv2.rectangle(img, (facial_area[2], facial_area[3])
                        , (facial_area[0], facial_area[1]), (200, 200, 200), 1)

                    cv2.putText(img, person.split('_')[0]
                        , (facial_area[0],facial_area[3]), cv2.FONT_HERSHEY_SIMPLEX
                        , 1, color=(200,200,200), thickness=2)

                    break
        
        plt.imsave('./output/output.jpg', img)

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        os.system(f'rm -rf ./tmp/')