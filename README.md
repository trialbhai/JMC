# GitHub Codespaces ♥️ Flask

Welcome to your shiny new Codespace running Flask! We've got everything fired up and running for you to explore Flask.

You've got a blank canvas to work on from a git perspective as well. There's a single initial commit with what you're seeing right now - where you go from here is up to you!

Everything you do here is contained within this one codespace. There is no repository on GitHub yet. If and when you’re ready you can click "Publish Branch" and we’ll create your repository and push up your project. If you were just exploring then and have no further need for this code then you can simply delete your codespace and it's gone forever.

## Running the Application

To run this application, use the following command:

```bash
flask --debug run
```

## API Endpoints

### User Authentication

- **Register**: `POST /auth/register`
  ```bash
  curl -X POST http://127.0.0.1:5000/auth/register \
       -H "Content-Type: application/json" \
       -d '{"username": "MEET", "password": "ABC@123"}'
  ```

- **Login**: `POST /auth/login`
  ```bash
  curl -X POST http://127.0.0.1:5000/auth/login \
       -H "Content-Type: application/json" \
       -d '{"username": "MEET", "password": "ABC@123"}'
  ```

- **Dashboard**: `GET /user/dashboard` (Requires JWT token)
  ```bash
  curl -X GET http://127.0.0.1:5000/user/dashboard \
       -H "Authorization: Bearer <your-token>"
  ```

### Service Management

- **Home**: `GET /home`
  ```bash
  curl -X GET http://127.0.0.1:5000/home
  ```

- **Search Service**: `GET /search?query=<service-name>`
  ```bash
  curl -X GET http://127.0.0.1:5000/search?query="service-name"
  ```

- **Redirect to Service**: `GET /service/<service-name>`
  ```bash
  curl -X GET http://127.0.0.1:5000/service/"service-name"
  ```

## Project Structure

- `app.py`: Main application file.
- `home.py`: Contains routes for home, search, and service redirection.
- `login.py`: Contains routes for user authentication.
- `templates/`: Contains HTML templates.
- `static/`: Contains static files like CSS.
- `requirements.txt`: Python dependencies.
- `.devcontainer/`: Configuration for GitHub Codespaces.
- `.gitignore`: Git ignore file.

## Requirements

- Flask==2.1.1
- flask-pymongo==2.3.0
- werkzeug==2.1.1
- flask-jwt-extended==4.4.3
- flask-cors==3.0.10
- python-dotenv==0.20.0

## License

This project is licensed under the MIT License.
