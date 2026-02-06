# 📈 SMINT - Stock Price Prediction & Portfolio Management

A Streamlit-based web application for stock price prediction using Machine Learning, with interactive data visualization and a portfolio trading simulator.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.50-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 🚀 Features

### 🔐 User Authentication
- SQLite-based user registration and login
- SHA-256 password hashing for security
- User profile management

### 📊 Data Visualization
- Upload stock data (CSV, Excel, TXT)
- Multiple chart types: Line, Bar, Scatter, Area, **Candlestick**
- **7-day and 30-day Moving Averages**
- Volume chart overlay
- Interactive date range filtering
- Data statistics (Min, Max, Mean, Median, Std Dev)
- Download filtered data as CSV

### 🔮 Stock Price Prediction
- ML-based stock price prediction using trained model
- **Single date** prediction
- **Date range** prediction with visualization
- **Predicted vs Actual** price comparison chart
- Prediction accuracy metrics
- Prediction history tracking

### 💼 Portfolio Simulator
- Virtual portfolio with $100,000 starting cash
- Buy/Sell stocks
- Real-time portfolio tracking
- Transaction history
- Performance summary

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Az-main/SMINT-Stock-Prediction.git
   cd SMINT-Stock-Prediction
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run main.py
   ```

4. **Open in browser**
   - The app will open at `http://localhost:8501`

## 🔑 Default Login
- **Username:** `admin`
- **Password:** `password123`

Or create a new account from the sidebar.

## 📁 Project Structure
```
SMINT-Stock-Prediction/
├── main.py               # Main application
├── database.py           # SQLite database operations
├── samsung_model.pkl     # Trained ML model
├── Samsung_stock.csv     # Stock data
├── requirements.txt      # Python dependencies
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## 🛠️ Tech Stack
- **Frontend:** Streamlit
- **Visualization:** Plotly, Plotly Graph Objects
- **ML Model:** Scikit-learn (trained model)
- **Database:** SQLite3
- **Security:** SHA-256 Password Hashing
- **Data Processing:** Pandas, NumPy

## 📸 Screenshots

### Login Page
Login or create a new account from the sidebar.

### Data Visualization
Upload stock data and visualize with multiple chart types including candlestick charts.

### Price Prediction
Predict future stock prices and compare with actual values.

## 🤝 Contributing
Feel free to fork this repository and submit pull requests.

## 📄 License
This project is open source and available under the [MIT License](LICENSE).

## 👤 Author
- **Azmain** - [GitHub](https://github.com/Az-main)
