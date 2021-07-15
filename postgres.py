from typing import final
import psycopg2
from deepface import DeepFace
from retinaface import RetinaFace
import matplotlib.pyplot as plt
import cv2
from PIL import Image
import numpy as np
import pandas as pd
from pathlib import Path
import os
import urllib.request
import pickle

def connect(password, host='localhost', database='Image describe pipe DB', user='postgres'):
    """ Connect to the PostgreSQL database server """
    conn = None
    model = DeepFace.build_model('Facenet')
    try:
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(
            host = host,
            database = database,
            user = user,
            password = password)
        print('Connection has established successfully.')

        return conn, model
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def disconnect(conn):
    conn.close()
    print('Database connection closed.')


def add_defining_image(conn, model, user_email, image_url, who_is_in):
    os.system('mkdir ./tmp/ ./tmp/DB')
    os.system(f'touch ./tmp/tmp.jpg ./tmp/DB/{who_is_in.split()[0]}.jpg')

    urllib.request.urlretrieve(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/66/Temporary_plate.svg/1202px-Temporary_plate.svg.png"
        ,'./tmp/tmp.jpg'
        )

    urllib.request.urlretrieve(
        image_url
        ,f'./tmp/DB/{who_is_in.split()[0]}.jpg'
        )

    
    DeepFace.find('./tmp/tmp.jpg', './tmp/DB', 'Facenet', model=model, enforce_detection=False)

    with open('./tmp/DB/representations_facenet.pkl', 'rb') as f:
        data = pickle.load(f)

    try:
        cur = conn.cursor()
        cur.execute(
            f'''
            INSERT INTO public.images(user_email, image_url, representation, who_is_in)
            VALUES(
                '{user_email}',
                '{image_url}',
                '{data[0][1]}',
                '{who_is_in}'
            )
            ON CONFLICT (image_url, user_email) DO UPDATE SET who_is_in = EXCLUDED.who_is_in, representation = EXCLUDED.representation;

            INSERT INTO public.logs(user_email, action, date)
            VALUES(
                '{user_email}',
                'Added/updated a defining image',
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
        os.system('rm -rf ./tmp')


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
                    'Removed a defining image',
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
                    'Tried to remove a unexisting defining image',
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
            VALUES(
                '{email}',
                'User is updated/added to database',
                NOW()
            )
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