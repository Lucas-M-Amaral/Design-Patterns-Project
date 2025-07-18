# Design Patterns - Course Management with FastAPI

This project implements a FastAPI and MySQL application, likely focused on managing courses and lessons,
implementing Design Patterns such as Composite, Chain of Responsibility, Prototype, and others.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
  - [Install Dependencies](#install-dependencies)
  - [Environment Variables](#environment-variables)
  - [Running with Docker Compose](#running-with-docker-compose)
- [API Documentation](#api-documentation)

## Features

* **Course and Lesson Management:** Core functionality to handle courses and lessons.
* **Design Patterns Implementation:**
    * **Composite Pattern:** Allows for treating individual lessons and groups of lessons (module) uniformly.
    * **Chain of Responsibility Pattern:** Enables lesson completion verification to access the next lesson, allowing for flexible and decoupled processing.
    * **Prototype Pattern:** Facilitates module cloning, allowing for easy duplication of course structures.
    * **Mediator Pattern:** Enables communication between students and instructors, centralizing interactions and reducing dependencies.
    * **Observer Pattern:** Not explicitly mentioned, but could be used for notifying students about course updates or new lessons.
    * **Strategy Pattern:** Enables different payment strategies for course enrollment, allowing for flexible payment options.
    * **Data Access Object (DAO) Pattern:** Provides a structured way to interact with the database, abstracting data access logic.
    * **Business Objects (BO):** Encapsulates business logic, ensuring separation of concerns and maintainability.
    * **Model-View-Controller (MVC) Pattern:** Organizes the application into models, views, and controllers, promoting a clean architecture.
* **Dockerized Development:** Streamlined setup and consistent environment across different machines using Docker Compose.

## Prerequisites

Before getting started, ensure you have the following installed:

* **Docker Desktop:** This includes Docker Engine and Docker Compose, essential for running the project with Docker.
    * [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)

If you choose to run the project locally without Docker, you'll also need:

* **Python 3.11+:** The primary language for this project.
    * [Download Python](https://www.python.org/downloads/)
* **pip:** Python's package installer, usually included with Python.

## Setup

### Install Dependencies

First you need to install the libs from `requirements.txt` file. This file contains all the necessary dependencies 
for the project. 

- **Install the required Python packages:**
    ```bash
    pip install -r requirements.txt
    ```

### Environment Variables

Then you need to create a `.env` file that contains the environment variables required for the 
application to run.

- **Create the `.env` file:**
    ```bash
    python merge_default_dotenvs_in_dotenv.py
    ```



### Running with Docker Compose

This is the recommended approach for development, ensuring all dependencies and services are correctly managed.

1.  **Build and run the Docker containers:**
    This command will build the necessary Docker images (if they don't exist or have changed) and start the services defined in your `compose.yml`.

    ```bash
    docker-compose -f compose.yml up -d
    ```

2.  **Access the Application:**
    Once the containers are up and running, your FastAPI application should be accessible in your web browser at:
    `http://localhost:8000` (or the port configured in your `compose.yml` file).

3.  **Stop the Containers:**
    To stop and remove all services, networks, and volumes created by Docker Compose:

    ```bash
    docker-compose -f compose.yml down
    ```

## API Documentation

FastAPI automatically generates interactive API documentation, which is invaluable for understanding and testing your endpoints.

Once the server is running (either via Docker Compose or locally), you can access:

* **Swagger UI:** `http://localhost:8000/docs`
* **ReDoc:** `http://localhost:8000/redoc`
