# Bookstore API Documentation

## Getting Started

This guide will help you to set up and run the Bookstore API on your local machine using Docker.

### Prerequisites

Make sure you have Docker installed on your system. The API relies on the following Docker images:

- python
- redis
- celery

### Running the API

1. **Build the Image and Run the Container**

   To build the image and download any images which are not installed, run:

    ```bash
    docker compose run django
    ```

2. **Start the Services**

   To get everything up and running, use:

    ```bash
    docker compose up
    ```

3. **Access the API Container**

   In a new terminal window, enter the following command to access the API container:

    ```bash
    docker exec -it book_api /bin/bash
    ```

4. **Run Migrations**

   Inside the container, run the migrations with the following command:

    ```bash
    python manage.py migrate
    ```

   Now the API is ready for use.

   **Note:** For this demo, we have not used any environment variables for sensitive information.

## Using the API

To start using the API, you will need to first register by sending a JSON object to `api/register/`.

## API Endpoints

### User Authentication

#### Register a New User

- **URL**: `api/register/`
- **Method**: `POST`
- **Permissions**: `AllowAny`
- **Input**:
  - `username`: String
  - `password`: String
- **Response**: A JSON object with the new user's details.

#### Obtain JWT Token

- **View**: `MyTokenObtainPairView`
- **Method**: `POST`
- **Permissions**: `AllowAny`
- **Input**:
  - `username`: String
  - `password`: String
- **Response**: A JSON object containing the access and refresh tokens. Add the access token as Auth Headers like this: "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." to authourize subsequent requests. This can be done using Thunderclient (VS code extension) or Postman
#### Logout User
- - **URL**: `api/logout/`
- **View**: `BlacklistTokenUpdateView`
- **Method**: `POST`
- **Permissions**: `AllowAny`
- **Input**:
  - `refresh`: String (Refresh Token which is obtained when user logs in.) 
- **Response**: A message indicating successful logout.

### Welcome Message

#### Welcome

- **URL**: `GET api/welcome/`
- **Permissions**: `IsAuthenticated`
- **Response**: A welcome message with the username.

### Book Management

#### List/Create/Update/Delete Books

- **URL**: `api/books/:id (if PUT,PATCH or GET one)/`
- **Methods**: `GET`, `POST`, `PUT`, `DELETE`
- **Permissions**: `IsAuthenticated`
- **Response**: A list of books or details of a single book.

### Author Management

#### List/Create/Update/Delete Authors

- **URL**: `api/authors/:id (if PUT,PATCH or GET one)/`
- **Methods**: `GET`, `POST`, `PUT`, `DELETE`
- **Permissions**: `IsAuthenticated`
- **Response**: A list of authors or details of a single author.

### Category Management

#### List/Create/Update/Delete Categories

- **URL**: `api/categories/:id (if PUT,PATCH or GET one)/`
- **Methods**: `GET`, `POST`, `PUT`, `DELETE`
- **Permissions**: `IsAuthenticated`
- **Response**: A list of categories or details of a single category.

### Shopping Cart

#### View Cart

- **URL**: `GET api/view_cart/`
- **Permissions**: `IsAuthenticated`
- **Response**: A list of items in the shopping cart.

#### Add to Cart

- **URL**: `POST api/add_to_cart/`
- **Permissions**: `IsAuthenticated`
- **Input**:
  - `book_id`: Integer (ID of the book to add)
- **Response**: The updated cart item information.

#### Remove from Cart

- **URL**: `POST api/remove_from_cart/`
- **Permissions**: `IsAuthenticated`
- **Input**:
  - `book_id`: Integer (ID of the book to remove)
- **Response**: The updated cart item information or a message if the item was removed.


#### checkout

- **URL**: `GET api/checkout/`
- **Permissions**: `IsAuthenticated`
- **Response**: A success message or an error if the checkout fails.

URL: [GET] /checkout/
Permissions: IsAuthenticated
Response: A success message or an error if the checkout fails.
