# Trash Blog Cleanup Website - Built on Python Flask

# Trash Clean Up Blog

Trash Clean Up Blog is a web application that allows users to register, log in, and post information about trash clean-up activities. Users can upload photos, provide details about the location and date of the clean-up, and view historical posts.

## About Us
Welcome to the Trash Clean Up Blog. This page is dedicated to helping clean up the Earth that we all live in. Take a photo of a straw you picked up that would have been stuck in a turtle's nose, or a water bottle or plastic bag on the walk to the store from the parking lot in the trash bin that otherwise would have been in a whale's stomach. That piece of trash you throw away each day in the bin 20 steps away sure adds up. 

## Disclaimer
We are not responsible for any actions taken by users. Users must follow all laws and regulations regarding safe trash disposal and handling of hazardous materials where they live. We are not responsible for any inappropriate content posted by users. Keep yourself clean, this site clean as well as well as the earth you live in.

## Features

- User registration and login
- Password reset functionality
- Post trash clean-up activities with photos
- View historical posts
- Ensure compliance with local disposal laws and regulations for safe trash disposal

## Requirements

- Python 3.10+
- Flask 2.0.2
- Flask-Session 0.4.0
- Werkzeug 2.0.2
- itsdangerous 2.0.1
- Jinja2 3.0.3
- MarkupSafe 2.0.1
- click 8.0.3
- importlib-metadata 4.8.2
- zipp 3.6.0
- typing-extensions 3.10.0.2
- gunicorn 20.1.0

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/trash-clean-up-blog.git
    cd trash-clean-up-blog
    ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

4. Initialize the database:
    ```sh
    python -c "from app import init_db; init_db()"
    ```

## Usage

1. Run the Flask application:
    ```sh
    flask run
    ```

2. Open your web browser and go to `http://127.0.0.1:3000`.

## Project Structure

```plaintext
trash-clean-up-blog/
├── app.py                  # Main application file
├── requirements.txt        # List of dependencies
├── .gitignore              # Git ignore file
├── README.md               # Project README file
├── templates/              # HTML templates
│   ├── base.html           # Base template
│   ├── index.html          # Home page template
│   ├── register.html       # Registration page template
│   ├── login.html          # Login page template
│   ├── drop_off.html       # Drop off page template
│   ├── historical_posts.html # Historical posts page template
│   ├── reset_password.html # Password reset page template
│   ├── set_new_password.html # Set new password page template
│   ├── about.html          # About page template
│   ├── eula.html           # End User License Agreement page template
├── static/
│   ├── uploads/            # Directory for uploaded photos
└── flask_session/          # Directory for Flask session files

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Contact
If you have any questions or suggestions, please contact me at wnadim2992@gmail.com.
