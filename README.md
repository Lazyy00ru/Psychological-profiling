# Psychological Profiling Web Application

## Overview

This project is developed for 159.352 Advanced Web Development (2026 S1).

It is a FastAPI-based web application that generates a psychological profile based on user input. The system analyses personality traits and integrates external APIs to produce results including career suggestions, movie recommendations, and pet images.

## Features

• Basic HTTP Authentication using student ID
• Single Page Application (SPA) frontend
• Personality analysis using the Big Five model
• Career suitability evaluation
• Movie recommendations via OMDb API
• Random animal images (Dog, Cat, Duck APIs)
• Input data and profile viewing endpoints
• Docker-based deployment

## Technologies Used

• Backend: FastAPI (Python)
• Frontend: HTML, CSS, JavaScript

• APIs:
o OMDb API
o dog.ceo
o thecatapi.com
o random-d.uk

• Deployment: Docker

## Authentication

All endpoints are protected using HTTP Basic Authentication.

Username: admin
Password: admin

## Running the Application (Docker)

1. Load the Docker image:

```bash
docker load -i psychological-app.tar
```

2. Run the container:

```bash
docker run -p 8000:8000 psychological-app
```

3. Open in browser:

```text
http://localhost:8000
```

## Running the Application Locally with main.py

### For macOS

1. Open Terminal and go to the project folder:

```bash
cd ~/Downloads/WebAssignment1
```

2. Install required packages:

```bash
python3 -m pip install -r requirements.txt
```

3. Run the FastAPI application:

```bash
python3 -m uvicorn main:app --reload
```

4. Open in browser:

```text
http://127.0.0.1:8000
```

### For Windows

1. Open Command Prompt or PowerShell and go to the project folder:

```bash
cd Downloads\WebAssignment1
```

2. Install required packages:

```bash
py -m pip install -r requirements.txt
```

3. Run the FastAPI application:

```bash
py -m uvicorn main:app --reload
```

4. Open in browser:

```text
http://127.0.0.1:8000
```

## How to Use the Website

1. Open the application in a browser:

```text
http://localhost:8000
```

2. Log in using:

Username: admin
Password: admin

3. Click “Take the Test” on the homepage.

4. Fill in the form:
   • Enter personal details (name, gender, etc.)
   • Answer all 20 personality questions
   • Select preferred job and pets

5. Click “Submit Form” (left sidebar).

6. Click “Run Analysis” to generate your psychological profile.

7. View results:
   • Click “My Profile” to see:
   o Personality traits
   o Career evaluation
   o Movie recommendations
   o Pet images

8. To view submitted data:
   • Click “Input Data” tab or “Load Input Data” button

9. Optional features:
   • View previous records using Input Data History or Profile History
   • Use the search bar to find questions

10. To restart:
    • Click “Reset Data” to clear current session data

## Notes

• Analysis must be run after submitting the form
• All data processing and API calls are handled by the server
• The application runs as a Single Page Application without page reloads

## Project Structure

```text
WebAssignment1/
├── main.py
├── Dockerfile
├── requirements.txt
├── Frontend/
│ ├── index.html
│ └── psycho.html
├── data/
├── images/
├── psychological-app.tar
```

## Application Flow

1. Access the application at `/`
2. Load the form via `/form`
3. Submit user input via `/submit`
4. Run analysis via `/analyze`
5. View profile results via `/view/profile`
6. View input data via `/view/input`

## Notes

• All external API calls are handled on the server side
• The frontend is implemented as a Single Page Application
• Data is stored temporarily on the server
• Folder naming is case-sensitive in Docker environments
