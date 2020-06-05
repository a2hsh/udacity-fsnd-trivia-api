# Udacitrivia

## Introduction

Udacitrivia is a website backed by a restful API, which allows you to create questions, view different categories, and play a quiz to test your knowledge. So, are you ready for it?
This Udacity FullStack project demenstrates my knowledge in building REST APIs with [Flask](https://palletsprojects.com/p/flask/).

## Starting the project
1. Clone the repo to your device.
2. From the backend directory, create a virtual environment and set the required environment variables.
3. Start the backend server using `python wsgi.py`
4. Run another terminal session. In the frontend directory, run `npm install` to install the required dependencies.
5. Finally, start the frontend server using `npm start`
6. You can view the website by visiting [http://localhost:3000](http://localhost:3000) in your browser.

For more information about how to get up and running, consult the following documents:
- [Backend Documentation](backend/README.md)
- [Frontend Documentation](frontend/README.md)

## About the Stack

the [backend](backend/) is a server created using Flask and SQLAlchemy.
The [frontend](frontend/) uses react. The two servers communicate using an api. Checkout the API Reference in the backend readme file to learn more.