# from postgres import *
from website import create_app


if __name__ == '__main__':
    # password = input('Enter your password: ')
    # conn = connect(password=password)

    # # add_defining_image(
    # #     conn,
    # #     'behnam.shomali@gmail.com',
    # #     'https://m.media-amazon.com/images/M/MV5BMWM3MDMzNjMtODM5Ny00YmY0LWJhNzQtNTE1ZDNlNjllNDQ0XkEyXkFqcGdeQXVyODkzNTgxMDg@._V1_.jpg',
    # #     'Anna'
    # # )
    # # remove_defining_image(
    # #     conn,
    # #     'behzad.shomali@gmail.com',
    # #     'https://drive.google.com/file/d/1-m7nsPQxdyx4yxIWhC4KaatUkyk_YiGX/view?usp=sharing',
    # # )
    # # add_user(conn, 'Behnam Shomali', 15, 'behnam.shomali@gmail.com', '123')
    # # remove_user(conn, 'behnam.shomali@gmail.com')
    # evaluate_image(conn, 
    #     'behzad.shomali@gmail.com', 
    #     'https://i.pinimg.com/originals/09/88/1f/09881f0ef958f782c8bf73e89ab9bdfd.jpg')
    # disconnect(conn)
    app = create_app()
    app.run(debug=True)