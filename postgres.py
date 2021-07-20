from typing import final
import psycopg2
from deepface import DeepFace
import os
import requests
import pickle
import matplotlib.pyplot as plt

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


def add_defining_image(conn, user_email, image_url, who_is_in, model=DeepFace.build_model('Facenet')):
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
        data = DeepFace.represent(img, 'Facenet', model)

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