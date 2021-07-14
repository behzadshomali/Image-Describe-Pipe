from postgres import *

if __name__ == '__main__':
    password = input('Enter your password: ')
    conn = connect(password=password)

    add_defineing_image(
        conn,
        'behzad.shomali@gmail.com',
        'https://drive.google.com/file/d/1arCk-433DmaHv46wtlBd3xnmQb4iTp0A/view?usp=sharing',
        'Anna de Armas'
    )
    remove_defineing_image(
        conn,
        'behzad.shomali@gmail.com',
        'https://drive.google.com/file/d/1arCk-433DmaHv46wtlBd3xnmQb4iTp0A/view?usp=sharing',
    )

    conn.close()
    print('Databse connection closed.')