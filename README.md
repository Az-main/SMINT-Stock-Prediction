# 📈 SMINT - Stock Price Prediction & Portfolio Management

## 🌐 Live Demo

Try the application here: **[Launch SMINT](https://smint-stock-prediction-ng4ud2x8vpaevm8pdkujsh.streamlit.app/)**

> SMINT is an educational project originally built during my second trimester.  
> The hosted version is intended as a small demonstration, and stored accounts or transaction data may reset when the application restarts.

A Streamlit-based web application for stock price prediction using Machine Learning, with interactive data visualization and a portfolio trading simulator.

> **Project context:** I built SMINT during my **2nd trimester of my BSc in Data Science** as part of my **Object-Oriented Programming (OOP)** course.  
> This was one of my **first complete end-to-end projects**, focused on practicing clean structure, core OOP concepts, and building a working ML-powered app.  
> I’m continuously improving and learning — future versions will include stronger modeling, validation, and more advanced features.

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
