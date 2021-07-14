import psycopg2

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

def add_defineing_image(conn, user_email, image_url, who_is_in):
    try:
        cur = conn.cursor()
        cur.execute(
            f'''
            INSERT INTO public.images(user_email, image_url, who_is_in)
            VALUES(
                '{user_email}',
                '{image_url}',
                '{who_is_in}'
            )
            ON CONFLICT (image_url, user_email) DO UPDATE SET who_is_in = EXCLUDED.who_is_in
            '''
        )
        conn.commit()
        cur.close()
        print('Image has been added to database successfully.')
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def remove_defineing_image(conn, user_email, image_url):
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
            conn.commit()
            print('The intended image has been removed from database successfully.')
        else:
            print('There is no image with the input information in the database.')
        
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)