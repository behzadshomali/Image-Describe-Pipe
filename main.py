from postgres import *

if __name__ == '__main__':
    password = input('Enter your password: ')
    conn = connect(password=password)

    # add_defining_image(
    #     conn,
    #     'behnam.shomali@gmail.com',
    #     'https://drive.google.com/file/d/1arCk-433DmaHv46wtlBd3xnmQb4iTp0A/view?usp=sharing',
    #     'Anna de Armas'
    # )
    # remove_defining_image(
    #     conn,
    #     'behzad.shomali@gmail.com',
    #     'https://drive.google.com/file/d/1-m7nsPQxdyx4yxIWhC4KaatUkyk_YiGX/view?usp=sharing',
    # )
    add_user(conn, 'Behnam Shomali', 15, 'behnam.shomali@gmail.com', '123')
    # remove_user(conn, 'behnam.shomali@gmail.com')
    conn.close()
    print('Database connection closed.')