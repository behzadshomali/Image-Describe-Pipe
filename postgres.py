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
    """ Disconnect the PostgreSQL database server connection """

    conn.close()
    print('Database connection closed.')


def add_defining_image(conn, user_email, image_url, who_is_in, model=DeepFace.build_model('Facenet512')):
    ''' Add image to database which is used for evaluting the further images '''

    # Making a temp directory which is used for 
    # storing the downloaded images
    os.system('mkdir ./tmp/')
    try:
        # Download the "defining_image" from its 
        # corresponding URL
        with open(f'./tmp/{who_is_in.split()[0]}.jpg', 'wb') as f:
            f.write(requests.get(image_url).content)

        # Read the downloaded into array of numbers
        img = plt.imread(f'./tmp/{who_is_in.split()[0]}.jpg')

        # Get the corresponding embeding (vector of
        # 512 numbers) of the image using a 
        # pretrained model
        data = DeepFace.represent(img, 'Facenet512', model)

        cur = conn.cursor()

        # Run the query which insert a new image
        # to table "images" of the database and 
        # also records its corresponding logs
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

        # Permanently store the applied changes
        # in the database 
        conn.commit()
        cur.close()
        print('Image has been added to database successfully.')
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        # Remove the made temp directory
        # which is unused anymore
        os.system(f'rm -rf ./tmp/')


def remove_defining_image(conn, user_email, image_url):
    ''' Remove an image from the database which was used for evaluating images '''

    try:
        cur = conn.cursor()

        # Remove the intended image from the
        # table "images" 
        cur.execute(
            f'''
            DELETE FROM public.images
            WHERE user_email = '{user_email}' and image_url = '{image_url}'
            RETURNING *
            '''
        )

        # Get the number of affected rows 
        # (deleted images)
        images_count = len(cur.fetchall())

        # Check whether the intended URL has
        # existed in the database
        if images_count == 1:
            # Commit the corresponding logs
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
            # Commit the corresponding logs
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
        
        # Permanently store the applied changes
        # in the database 
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def add_user(conn, full_name, age, email, password):
    ''' Add a new user to the database '''
    try:
        cur = conn.cursor()

        # Run the query which insert a new 
        # user to table "users" and also 
        # records its corresponding logs
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

        # Permanently store the applied changes
        # in the database 
        conn.commit()
        cur.close()
        print('User has been added to database successfully.')
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def remove_user(conn, email):
    ''' Remove a user from the database '''
    
    try:
        cur = conn.cursor()
        
        # Run the query which removes the
        # intended user from the database
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
        
        # Permanently store the applied changes
        # in the database 
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def evaluate_image(conn, user_email, image_url, model=DeepFace.build_model('Facenet512')):
    '''
    Evaluate the input image by gathering
    all the images belong to a specific user
    and the starts to get the Cosine-distance
    between the input image and the user's
    stored defining-images
    '''
    
    # Specify the upperbund distance between two
    # images' vector which are considered as belong
    # to a same a person
    THRESHOLD = 0.6

    # Making two directories. "tmp" which is used
    # for storing the downloaded images and "output"
    # which is used for storing the output of the function
    os.system('mkdir ./tmp/ ./tmp/DB ./output/')

    try:

        # Download the "defining_image" from its 
        # corresponding URL
        with open('./tmp/img.jpg', 'wb') as f:
            f.write(requests.get(image_url).content)

        # Read the downloaded into array of numbers
        img = plt.imread('./tmp/img.jpg')

        # Detect the faces appearing in the image
        # by a confidence ratio of 95%
        faces = RetinaFace.detect_faces(img, 0.95)

        cur = conn.cursor()

        # Run a query which collects all the images
        # belong to the intended person and records
        # its corresponding logs
        cur.execute(
            f'''
            SELECT who_is_in, representation 
            FROM public.images
            WHERE user_email = '{user_email}'

            INSERT INTO public.logs(user_email, action, date)
            SELECT
                '{user_email}',
                'User "' ||
                (
                    SELECT full_name
                    FROM public.users
                    WHERE email = '{user_email}'
                ) || '" evaluated the image with url ({image_url})',
                NOW()
            '''
        )

        # Extract and preprocess the stored representation
        # for each image
        representations_facenet = {}
        fetched_data = cur.fetchall()
        for indx, (who_is_in, representation) in enumerate(fetched_data):
            rep = representation.replace(' ', '')
            rep = rep.replace('[', '')
            rep = rep.replace(']', '')
            rep = list(map(float, rep.split(',')))
            representations_facenet[f'{who_is_in}_{indx}'] = rep
        
        # Mark and recognize each face which is detected in the image
        for indx, face_info in enumerate(faces.values()):
            facial_area = face_info['facial_area']
            y1 = max(facial_area[1]-200, 0)
            y2 = min(facial_area[3]+200, img.shape[0]-1)
            x1 = max(facial_area[0]-50, 0)
            x2 = min(facial_area[2]+50, img.shape[1]-1)

            # Cropped face extracted from the main image
            face = img[y1:y2, x1:x2]

            # Save each extracted person seperately
            plt.imsave(f'./output/face{indx}.jpg', face)
            
            # Get the corresponding embeding (vector of
            # 512 numbers) of the extracted face using a 
            # pretrained model
            img_rep = DeepFace.represent(np.asarray(face), 'Facenet512', model, False)

            # Get the Cosine-distance between
            # each extracted face and the user's
            # stored defining-images
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
        
        # Store the output in which faces are 
        # marked and recognized
        plt.imsave('./output/output.jpg', img)

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        # Remove the made temp directory
        # which is unused anymore
        os.system(f'rm -rf ./tmp/')