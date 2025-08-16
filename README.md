🌤️ Weather Pro – Flask Weather App

A modern, responsive weather forecasting web application built with Flask, OpenWeather API, and Bootstrap, featuring real-time weather updates, hourly forecasts, and a 5-day outlook.

🚀 Features

Live Weather Data – Current temperature, feels-like, humidity, wind speed, clouds, and pressure.

Next 12 Hours Forecast – Hourly temperature chart powered by Chart.js.

5-Day Forecast – Aggregated min/max temperatures with weather icons.

Dark/Light Theme Toggle – User-friendly interface with theme switching.

Unit Conversion – Switch between Celsius (°C) and Fahrenheit (°F).

Favorites & Recent Searches – Quick access to saved cities.

Responsive Design – Works seamlessly on desktop and mobile devices.

Caching – Speeds up repeated requests using in-memory cache.

🛠️ Tech Stack

Frontend: HTML, CSS, JavaScript, Bootstrap, Chart.js

Backend: Python, Flask

API: OpenWeather API

Environment Management: python-dotenv

📂 Project Structure
├── app.py             # Flask backend server
├── templates/
│   └── index.html     # Main UI
├── static/            # CSS, JS, and images (if any)
├── .env               # API key storage
├── requirements.txt   # Python dependencies
└── app.log            # Application logs

⚙️ Setup Instructions
1. Clone the Repository
git clone https://github.com/yourusername/weather-pro.git
cd weather-pro

2. Install Dependencies
pip install -r requirements.txt

3. Get Your OpenWeather API Key

Sign up at OpenWeather

Create a .env file in the project root:

API_KEY=your_openweather_api_key

4. Run the App
python app.py


The app will start on http://127.0.0.1:5000

📸 Screenshots

<img width="1917" height="922" alt="image" src="https://github.com/user-attachments/assets/bf175cf7-7d96-4680-abb9-5ed7584d9153" />
<img width="1087" height="828" alt="image" src="https://github.com/user-attachments/assets/00218d1e-99d9-402d-8e79-2ad081d22fb8" />
<img width="1121" height="817" alt="image" src="https://github.com/user-attachments/assets/ab621297-bf44-4a81-b16b-3ef516b40068" />


📜 License

This project is licensed under the MIT License – feel free to use and modify.
