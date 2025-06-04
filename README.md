# Internship Assignment: Basic Trading System

This project is a basic trading system built to fulfill an internship assignment. It includes a REST API for managing trades, real-time stock data processing simulation via WebSockets, and cloud integration with AWS (S3 and Lambda) for data analysis.

## Table of Contents

*   [Project Overview](#project-overview)
*   [Features Implemented](#features-implemented)
*   [Technologies Used](#technologies-used)
*   [Setup Instructions](#setup-instructions)
    *   [Prerequisites](#prerequisites)
    *   [1. REST API (Django)](#1-rest-api-django)
    *   [2. Real-Time Data Processing (WebSockets)](#2-real-time-data-processing-websockets)
    *   [3. Cloud Integration (AWS Lambda & S3)](#3-cloud-integration-aws-lambda--s3)
*   [Running the Application](#running-the-application)
    *   [Running the REST API](#running-the-rest-api)
    *   [Running the WebSocket Mock Server](#running-the-websocket-mock-server)
    *   [Running the WebSocket Client](#running-the-websocket-client)
    *   [Triggering the AWS Lambda Function](#triggering-the-aws-lambda-function)
*   [API Endpoints](#api-endpoints)
*   [Assumptions Made](#assumptions-made)
*   [Future Enhancements (Optional)](#future-enhancements-optional)

## Project Overview

 This system allows users to record stock trades via a REST API, simulates receiving real-time stock price updates, and uses AWS Lambda to analyze daily trade data stored in S3.

## Features Implemented

*   **Task 1: REST API Development**
    *   Endpoint to add trades (`POST /api/trades/`) with details: ticker, price, quantity, side, timestamp.
    *   Endpoint to fetch trades (`GET /api/trades/`) with optional filtering by `ticker` and `date_range` (e.g., `?ticker=AAPL&start_date=YYYY-MM-DDTHH:MM:SSZ&end_date=YYYY-MM-DDTHH:MM:SSZ`).
    *   Data storage in PostgreSQL.
    *   Input validation for trade details (e.g., non-negative price/quantity, valid ticker format).
    *   **Bonus:** Integrated Celery with Redis for asynchronous background task processing (e.g., sending a notification) when a new trade is created.
*   **Task 2: Real-Time Data Processing**
    *   A Python script (`mock_server.py`) that simulates a WebSocket server sending mock stock price updates.
    *   A Python script (`websocket_client.py`) that connects to the mock server, receives price updates, and triggers a console notification if a stock's price increases by more than 2% within a minute.
*   **Task 3: Cloud Integration with AWS**
    *   Trade data is assumed to be stored in S3 (e.g., `s3://<your-bucket-name>/YEAR/MONTH/DATE/trades.csv`).
    *   An AWS Lambda function (`tradeAnalyzerFunction`) that:
        *   Fetches the `trades.csv` file from S3 for a given date.
        *   Calculates the total traded volume and average price for each stock in the file.
        *   Saves the analysis results back to S3 as `YEAR/MONTH/DATE/analysis_DATE.csv`.

## Technologies Used

*   **Backend:** Python, Django, Django REST Framework
*   **Database:** PostgreSQL
*   **Asynchronous Task Queue:** Celery
*   **Message Broker/Cache:** Redis
*   **Real-Time Simulation:** Python `websockets` library
*   **Cloud:** AWS S3, AWS Lambda, `boto3` (AWS SDK for Python)
*   **Concurrency (for Celery on Windows):** eventlet
*   **Version Control:** Git (implied)

## Setup Instructions

### Prerequisites

*   Python (version 3.8+ recommended)
*   `pip` (Python package installer)
*   PostgreSQL server installed and running.
*   **Redis server installed and running.**
*   AWS Account with CLI access configured ...
*   Git (optional, for cloning if you host it on GitHub).

### 1. REST API (Django)

1.  **Clone the repository (if applicable):**
    ```bash
    git clone https://github.com/Hemanth0411/trading_system
    cd trading_system
    ```
2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows
    source venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```
3.  **Install Python dependencies:**
    Create a `requirements.txt` file (see below) and run:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Set up PostgreSQL Database:**
    *   Create a PostgreSQL database (e.g., `trading_system_db`).
    *   Create a database user (e.g., `trading_user` with password `trading_user`).
    *   Grant appropriate permissions to the user on the database (as detailed in our previous steps for `GRANT USAGE, CREATE ON SCHEMA public` and `GRANT ALL PRIVILEGES ON DATABASE`).
5.  **Set up Redis Server:**
    *   Install Redis (refer to official Redis documentation for your OS).
        *   **macOS (Homebrew):** `brew install redis && brew services start redis`
        *   **Linux (Ubuntu):** `sudo apt update && sudo apt install redis-server && sudo systemctl start redis-server`
        *   **Windows:** Recommended to run Redis via WSL (Windows Subsystem for Linux) or Docker.
            *   Inside WSL (e.g., Ubuntu): `sudo apt update && sudo apt install redis-server && sudo service redis-server start`
    *   Ensure Redis server is running (typically on `localhost:6379`). You can test with `redis-cli ping` (should return `PONG`).
6.  **Configure Django Settings:**
    *   Open `trading_system/settings.py`.
    *   Update the `DATABASES` setting with your PostgreSQL connection details (name, user, password, host, port).
7.  **Apply Database Migrations:**
    ```bash
    python manage.py makemigrations trades_api
    python manage.py migrate
    ```

### 2. Real-Time Data Processing (WebSockets)

1.  **Install `websockets` library (if not already in `requirements.txt`):**
    ```bash
    pip install websockets
    ```
    *(The scripts `mock_server.py` and `websocket_client.py` are standalone but use this library).*

### 3. Cloud Integration (AWS Lambda & S3)

1.  **AWS S3 Bucket:**
    *   Create an S3 bucket in your AWS account (e.g., `lonelys-fintech-assignemnt`).
    *   Ensure your local AWS CLI/SDK environment is configured with credentials that have access to this bucket if you plan to interact with it outside of Lambda.
2.  **AWS Lambda Function (`tradeAnalyzerFunction`):**
    *   The Lambda function code is provided (e.g., `lambda_function.py` or you can copy it from the AWS console).
    *   **Deployment:**
        *   Create a new Lambda function in the AWS console.
        *   Choose Python (e.g., 3.9) as the runtime.
        *   Copy the provided Lambda code into the inline editor.
        *   **Crucially, update the `bucket_name = 'YOUR_BUCKET_NAME'` line in the Lambda code to your actual S3 bucket name.**
        *   Deploy the function.
    *   **IAM Role & Permissions:**
        *   The Lambda function's execution role needs permissions to read from and write to your S3 bucket (e.g., attach `AmazonS3FullAccess` or a more specific policy granting `s3:GetObject` and `s3:PutObject` for the target bucket).
        *   It also needs basic Lambda execution permissions (e.g., for CloudWatch Logs).
    *   **Test Event:** Configure a test event in the Lambda console with the following JSON structure to specify the date to process:
        ```json
        {
          "date": "YYYY-MM-DD"
        }
        ```
        (Replace `YYYY-MM-DD` with a date for which you have uploaded a `trades.csv` file to S3, e.g., "2024-05-15").

## Running the Application

For the full application experience (including background task processing for trade notifications), you'll need to run the Django development server, the Redis server, and the Celery worker.

1.  **Ensure Redis Server is Running.** (As per setup instructions).
2.  **Ensure PostgreSQL Server is Running.**

### Running the REST API

1.  Navigate to the Django project root directory (where `manage.py` is).
2.  Ensure your virtual environment is activated.
3.  Start the Django development server:
    ```bash
    python manage.py runserver
    ```
    The API will typically be available at `http://127.0.0.1:8000/api/`.

### Running the Celery Worker

1.  Open a **new terminal window/tab**.
2.  Navigate to the Django project root directory.
3.  Activate your virtual environment.
4.  Start the Celery worker:
    ```bash
    # On Linux/macOS:
    celery -A trading_system worker -l info
    # On Windows (recommended):
    celery -A trading_system worker -l info -P eventlet
    ```
    The worker will connect to Redis and wait for tasks.

### Running the WebSocket Mock Server

1.  Navigate to the directory containing `mock_server.py`.
2.  Run the script:
    ```bash
    python mock_server.py
    ```
    The server will start, usually on `ws://localhost:8765`.

### Running the WebSocket Client

1.  Open a new terminal.
2.  Navigate to the directory containing `websocket_client.py`.
3.  Ensure the mock server is running.
4.  Run the script:
    ```bash
    python websocket_client.py
    ```
    The client will connect to the server and start displaying price updates and alerts.

### Triggering the AWS Lambda Function

1.  Go to your `tradeAnalyzerFunction` in the AWS Lambda console.
2.  Select your configured test event (e.g., `ProcessMay15Trades`).
3.  Click the "Test" button.
4.  Check the execution results, CloudWatch logs, and verify the output `analysis_DATE.csv` file in your S3 bucket.

## API Endpoints

*   **Add Trade:**
    *   `POST /api/trades/`
    *   **Request Body (JSON):**
        ```json
        {
            "ticker": "MSFT",
            "price": "310.50",
            "quantity": 50,
            "side": "BUY",
            "timestamp": "2025-06-03T12:00:00Z"
        }
        ```
    *   **Success Response (201 Created):** The created trade object.
*   **Fetch Trades:**
    *   `GET /api/trades/`
    *   **Optional Query Parameters:**
        *   `ticker=<STOCK_TICKER>` (e.g., `?ticker=MSFT`)
        *   `start_date=<ISO_DATETIME>` (e.g., `?start_date=2025-06-01T00:00:00Z`)
        *   `end_date=<ISO_DATETIME>` (e.g., `?end_date=2025-06-03T23:59:59Z`)
    *   **Success Response (200 OK):** A list of trade objects.

## Assumptions Made

*   **Timestamp Input:** Timestamps for trades are provided by the client in ISO 8601 format and are assumed to be in UTC if no timezone offset is specified (or handled correctly by `DateTimeField` and `parse_datetime`).
*   **S3 File Structure:** The Lambda function assumes input `trades.csv` files are stored in S3 with the exact path structure `YEAR/MONTH/DAY/trades.csv`.
*   **Lambda Trigger:** For this assignment, the Lambda function is triggered manually via a test event. A production system might use S3 event triggers or a scheduled trigger.
*   **Valid Tickers (Format):** Ticker validation in the API currently checks for format (1-5 uppercase letters) but not against a pre-defined list of actual, existing stock tickers.
*   **WebSocket Data:** The WebSocket mock server sends a list of all mock ticker updates in each message.
*   **Error Handling:** Basic error handling is implemented. Production systems would require more comprehensive logging and error management.
*   **Database for WebSocket Client:** The bonus task to store 5-minute average prices from the WebSocket client into the Task 1 database was not implemented in the core tasks.
*   **Redis server** is accessible on localhost:6379 for **Celery**.

## Future Enhancements (Optional)

*   Implement the bonus tasks (Average price storage for WebSocket, API Gateway for Lambda).
*   Implement the optional Algorithmic Trading Simulation (Task 4).
*   More robust error handling and logging throughout the application.
*   User authentication and authorization for the API.
*   Deployment of the Django API to a web server (e.g., Gunicorn + Nginx, or a PaaS like Heroku/AWS Elastic Beanstalk).
*   Automated triggers for the Lambda function (e.g., S3 put event).