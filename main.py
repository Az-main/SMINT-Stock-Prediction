import random
import datetime
import pandas as pd
import numpy as np
import streamlit as st
import os
import warnings
import joblib
import plotly.express as px  # Importing Plotly for visualization
import plotly.graph_objects as go  # For candlestick charts

# Import database module for SQLite authentication
import database as db

warnings.filterwarnings('ignore')

# Initialize the database on startup
db.init_database()

# Load the trained models
model = joblib.load('samsung_model.pkl')

def predict_open_price(year, month, day):
    """Predict the open price based on the input date."""
    input_data = pd.DataFrame([[int(year), int(month), int(day)]], columns=['year', 'month', 'day'])
    prediction = model.predict(input_data)
    return prediction[0]

def predict_price_range(start_date, end_date):
    """Predict prices for a date range."""
    predictions = []
    current_date = start_date
    while current_date <= end_date:
        pred = predict_open_price(current_date.year, current_date.month, current_date.day)
        predictions.append({
            'Date': current_date,
            'Predicted_Open': pred
        })
        current_date += datetime.timedelta(days=1)
    return pd.DataFrame(predictions)

def calculate_moving_average(df, column, window):
    """Calculate moving average for a given column."""
    return df[column].rolling(window=window).mean()

def validate_dataframe(df):
    """Validate that the dataframe has required columns."""
    required_columns = ['Date', 'open']
    missing = [col for col in required_columns if col not in df.columns]
    return len(missing) == 0, missing

def get_data_statistics(df, column):
    """Get statistics for a given column."""
    return {
        'Min': df[column].min(),
        'Max': df[column].max(),
        'Mean': df[column].mean(),
        'Median': df[column].median(),
        'Std Dev': df[column].std()
    }

# Stock class definition
class Stock:
    def __init__(self, name, symbol, price, dividend_yield=0.0):
        self.name = name
        self.symbol = symbol
        self.price = price
        self.dividend_yield = dividend_yield
        self.price_history = [price]

    def update_price(self):
        change_percentage = random.uniform(-5, 5)
        self.price += self.price * (change_percentage / 100)
        self.price_history.append(self.price)

    def pay_dividend(self):
        return self.price * (self.dividend_yield / 100)

    def __str__(self):
        return f"{self.name} ({self.symbol}): ${self.price:.2f}"

# StockMarket class definition
class StockMarket:
    def __init__(self):
        self.stocks = self.load_stocks()

    def load_stocks(self):
        return [
            Stock("Samsung Electronics", "SSNLF", 80)
        ]

    def get_stock(self, symbol):
        for stock in self.stocks:
            if stock.symbol == symbol:
                return stock
        return None

    def update_market(self):
        for stock in self.stocks:
            stock.update_price()

# Portfolio class definition
class Portfolio:
    def __init__(self, username, transaction_history=None):
        self.username = username
        self.stocks = {}
        self.cash = 100000
        self.transaction_history = transaction_history if transaction_history is not None else pd.DataFrame(columns=["Date", "Type", "Symbol", "Quantity", "Price", "Total Cost/Value"])
        self.total_profit = 0

    def buy_stock(self, stock, quantity):
        total_cost = stock.price * quantity
        if total_cost > self.cash:
            return f"Not enough cash to buy {quantity} shares of {stock.symbol}."
        else:
            if stock.symbol in self.stocks:
                self.stocks[stock.symbol]['quantity'] += quantity
            else:
                self.stocks[stock.symbol] = {'stock': stock, 'quantity': quantity}
            self.cash -= total_cost
            self.log_transaction("Buy", stock.symbol, quantity, stock.price, total_cost)
            return f"Bought {quantity} shares of {stock.symbol} at BDT{stock.price:.2f} each."

    def sell_stock(self, stock_symbol, quantity):
        if stock_symbol not in self.stocks or self.stocks[stock_symbol]['quantity'] < quantity:
            return f"Not enough shares of {stock_symbol} to sell."
        else:
            stock = self.stocks[stock_symbol]['stock']
            total_value = stock.price * quantity
            self.stocks[stock_symbol]['quantity'] -= quantity
            self.cash += total_value
            profit = total_value - stock.price * quantity
            self.total_profit += profit
            if self.stocks[stock_symbol]['quantity'] == 0:
                del self.stocks[stock_symbol]
            self.log_transaction("Sell", stock_symbol, quantity, stock.price, total_value)
            return f"Sold {quantity} shares of {stock_symbol} at {stock.price:.2f}BDT each."

    def log_transaction(self, transaction_type, stock_symbol, quantity, price, total_cost_value):
        new_transaction = pd.DataFrame([{
            "Date": datetime.datetime.now(),
            "Type": transaction_type,
            "Symbol": stock_symbol,
            "Quantity": quantity,
            "Price": price,
            "Total Cost/Value": total_cost_value
        }])
        self.transaction_history = pd.concat([self.transaction_history, new_transaction], ignore_index=True)

    def show_portfolio(self):
        portfolio_str = f"Cash: ${self.cash:.2f}\n\n"
        for stock_data in self.stocks.values():
            stock = stock_data['stock']
            quantity = stock_data['quantity']
            portfolio_str += f"{stock.name} ({stock.symbol}): {quantity} shares @ ${stock.price:.2f}\n"
        return portfolio_str

    def show_transaction_history(self):
        return self.transaction_history

    def show_performance_summary(self):
        return f"Total Profit: {self.total_profit:.2f}BDT"

# Database functions are now in database.py
# Using SQLite with password hashing for secure authentication

# Save transaction history to CSV
def save_transaction_history(portfolio):
    filename = f"{portfolio.username}_transaction_history.csv"
    portfolio.transaction_history.to_csv(filename, index=False)
    st.success(f"Transaction history saved as {filename}.")

# Load transaction history from CSV
def load_transaction_history(username):
    filename = f"{username}_transaction_history.csv"
    if os.path.exists(filename):
        return pd.read_csv(filename)
    else:
        return pd.DataFrame(columns=["Date", "Type", "Symbol", "Quantity", "Price", "Total Cost/Value"])

# Login or Create New User (Using SQLite Database)
def login_or_create_account():
    st.sidebar.header("User Login")

    # Check if user is logged in
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False  # Initialize logged_in state

    if not st.session_state.logged_in:
        # Login Section
        st.sidebar.subheader("Login")
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")

        # Check login credentials using database
        if st.sidebar.button("Login"):
            if username and password:
                success, message = db.verify_user(username, password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success(message)
                    st.rerun()  # Refresh to show logged-in state
                else:
                    st.error(message)
            else:
                st.error("Please enter both username and password.")

        # Create new account option
        st.sidebar.markdown("---")
        st.sidebar.subheader("Create New Account")
        new_username = st.sidebar.text_input("New Username")
        new_email = st.sidebar.text_input("Email")
        new_password = st.sidebar.text_input("New Password", type="password")
        confirm_password = st.sidebar.text_input("Confirm Password", type="password")

        if st.sidebar.button("Create Account"):
            # Validation
            if not new_username or not new_email or not new_password:
                st.error("Please fill in all fields.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters.")
            elif "@" not in new_email:
                st.error("Please enter a valid email address.")
            else:
                # Create user in database
                success, message = db.create_user(new_username, new_email, new_password)
                if success:
                    st.success(message)
                else:
                    st.error(message)
    else:
        # Show logged-in user info
        user_info = db.get_user_info(st.session_state.username)
        st.sidebar.success(f"Logged in as: {st.session_state.username}")
        if user_info:
            st.sidebar.caption(f"Email: {user_info['email']}")
        
        if st.sidebar.button("Logout"):
            if 'portfolio' in st.session_state:
                save_transaction_history(st.session_state.portfolio)  # Save transaction history
            st.session_state.logged_in = False
            st.session_state.pop('portfolio', None)
            st.session_state.pop('username', None)
            st.rerun()  # Refresh to show login form

# Main App
def main():
    # Set the page configuration
    st.set_page_config(page_title="Stock Prediction", page_icon=":chart_with_upwards_trend:", layout="wide")

    # Title of the app
    st.title(":chart_with_upwards_trend: Stock Prediction and Portfolio Management")

    login_or_create_account()

    if st.session_state.logged_in:
        # Initialize market and portfolio if not already done
        if 'market' not in st.session_state:
            st.session_state.market = StockMarket()
        
        if 'portfolio' not in st.session_state:
            transaction_history = load_transaction_history(st.session_state.username)
            st.session_state.portfolio = Portfolio(st.session_state.username, transaction_history)

        # Initialize prediction history
        if 'prediction_history' not in st.session_state:
            st.session_state.prediction_history = pd.DataFrame(columns=['Date', 'Predicted_Open', 'Actual_Open', 'Difference'])

        # Create tabs for different sections
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Data & Visualization", "🔮 Price Prediction", "💼 Portfolio", "📊 Stock Market"])

        # ==================== TAB 1: DATA & VISUALIZATION ====================
        with tab1:
            st.header("Stock Data Analysis")
            
            # File uploader with multiple format support
            st.subheader("📁 Upload Stock Data")
            fl = st.file_uploader(
                "Upload your stock data file", 
                type=["csv", "xlsx", "xls", "txt"],
                help="Supported formats: CSV, Excel (xlsx, xls), Text files"
            )
            
            # Load data
            if fl is not None:
                try:
                    filename = fl.name
                    if filename.endswith('.csv') or filename.endswith('.txt'):
                        df = pd.read_csv(fl, encoding="ISO-8859-1")
                    elif filename.endswith(('.xlsx', '.xls')):
                        df = pd.read_excel(fl)
                    st.success(f"✅ File uploaded successfully: {filename}")
                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")
                    df = pd.read_csv("Samsung_stock.csv", encoding="ISO-8859-1")
            else:
                df = pd.read_csv("Samsung_stock.csv", encoding="ISO-8859-1")
                st.info("📌 Using default Samsung stock data. Upload your own file above.")

            # Validate dataframe
            if df.empty:
                st.warning("⚠️ The uploaded file is empty.")
                return

            # Check required columns
            is_valid, missing_cols = validate_dataframe(df)
            if not is_valid:
                st.warning(f"⚠️ Missing required columns: {missing_cols}. Some features may not work.")

            # Data preprocessing
            df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
            
            # Clean numeric columns
            numeric_cols = ['open', 'High', 'Low', 'Close/Last', 'Volume']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col].astype(str).str.replace('$', '').str.replace(',', ''), errors='coerce')

            # Data preview section
            st.subheader("📋 Data Preview")
            col_preview1, col_preview2 = st.columns([3, 1])
            with col_preview1:
                rows_to_show = st.slider("Rows to display", 5, 50, 10)
                st.dataframe(df.head(rows_to_show), use_container_width=True)
            with col_preview2:
                st.metric("Total Rows", len(df))
                st.metric("Total Columns", len(df.columns))
                st.metric("Date Range", f"{df['Date'].min().strftime('%Y-%m-%d') if pd.notna(df['Date'].min()) else 'N/A'}")

            # Date range filter
            st.subheader("📅 Filter by Date Range")
            col_date1, col_date2 = st.columns(2)
            
            min_date = df['Date'].min()
            max_date = df['Date'].max()
            
            if pd.notna(min_date) and pd.notna(max_date):
                with col_date1:
                    start_date = st.date_input("Start Date", min_date.date())
                with col_date2:
                    end_date = st.date_input("End Date", max_date.date())
                
                # Filter data
                df_filtered = df[(df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))].copy()
                
                if df_filtered.empty:
                    st.warning("No data available for the selected date range.")
                    return
            else:
                df_filtered = df.copy()
                st.warning("Date column has invalid values. Showing all data.")

            # Data Statistics
            st.subheader("📊 Data Statistics")
            if 'open' in df_filtered.columns:
                stats_cols = st.columns(5)
                stats = get_data_statistics(df_filtered, 'open')
                stats_cols[0].metric("Min Price", f"${stats['Min']:.2f}")
                stats_cols[1].metric("Max Price", f"${stats['Max']:.2f}")
                stats_cols[2].metric("Average", f"${stats['Mean']:.2f}")
                stats_cols[3].metric("Median", f"${stats['Median']:.2f}")
                stats_cols[4].metric("Std Dev", f"${stats['Std Dev']:.2f}")

            # Calculate Moving Averages
            if 'open' in df_filtered.columns and len(df_filtered) > 7:
                df_filtered['MA_7'] = calculate_moving_average(df_filtered, 'open', 7)
                df_filtered['MA_30'] = calculate_moving_average(df_filtered, 'open', 30)

            # Visualization Options
            st.subheader("📈 Visualization")
            
            viz_col1, viz_col2 = st.columns([1, 3])
            
            with viz_col1:
                # Select columns to visualize
                available_cols = [col for col in df_filtered.columns if col not in ['Date', 'Unnamed: 0', 'month', 'day', 'year']]
                price_column = st.selectbox("Select Price Column", available_cols, index=0 if available_cols else 0)
                
                graph_type = st.selectbox(
                    "Chart Type", 
                    ["Line Chart", "Candlestick", "Area Chart", "Bar Chart", "Scatter Plot"]
                )
                
                show_ma = st.checkbox("Show Moving Averages", value=True)
                show_volume = st.checkbox("Show Volume", value=False)

            with viz_col2:
                # Create visualization based on selection
                if graph_type == "Candlestick" and all(col in df_filtered.columns for col in ['open', 'High', 'Low', 'Close/Last']):
                    fig = go.Figure(data=[go.Candlestick(
                        x=df_filtered['Date'],
                        open=df_filtered['open'],
                        high=df_filtered['High'],
                        low=df_filtered['Low'],
                        close=df_filtered['Close/Last'],
                        name='OHLC'
                    )])
                    fig.update_layout(title="Candlestick Chart", xaxis_title="Date", yaxis_title="Price ($)")
                    
                elif graph_type == "Line Chart":
                    fig = px.line(df_filtered, x='Date', y=price_column, title=f"Line Chart of {price_column}")
                    
                    # Add moving averages
                    if show_ma and 'MA_7' in df_filtered.columns:
                        fig.add_scatter(x=df_filtered['Date'], y=df_filtered['MA_7'], mode='lines', name='7-Day MA', line=dict(dash='dash'))
                    if show_ma and 'MA_30' in df_filtered.columns:
                        fig.add_scatter(x=df_filtered['Date'], y=df_filtered['MA_30'], mode='lines', name='30-Day MA', line=dict(dash='dot'))
                
                elif graph_type == "Area Chart":
                    fig = px.area(df_filtered, x='Date', y=price_column, title=f"Area Chart of {price_column}")
                
                elif graph_type == "Bar Chart":
                    fig = px.bar(df_filtered, x='Date', y=price_column, title=f"Bar Chart of {price_column}")
                
                elif graph_type == "Scatter Plot":
                    fig = px.scatter(df_filtered, x='Date', y=price_column, title=f"Scatter Plot of {price_column}")
                
                else:
                    fig = px.line(df_filtered, x='Date', y=price_column, title=f"{price_column} Over Time")

                fig.update_layout(
                    xaxis_title="Date", 
                    yaxis_title="Price ($)",
                    hovermode='x unified',
                    xaxis_tickangle=-45
                )
                st.plotly_chart(fig, use_container_width=True)

            # Volume Chart
            if show_volume and 'Volume' in df_filtered.columns:
                st.subheader("📊 Trading Volume")
                vol_fig = px.bar(df_filtered, x='Date', y='Volume', title="Trading Volume Over Time")
                vol_fig.update_layout(xaxis_title="Date", yaxis_title="Volume")
                st.plotly_chart(vol_fig, use_container_width=True)

            # Download filtered data
            st.subheader("⬇️ Download Data")
            col_dl1, col_dl2 = st.columns(2)
            with col_dl1:
                csv_data = df_filtered.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Filtered Data (CSV)",
                    data=csv_data,
                    file_name=f"stock_data_{start_date}_to_{end_date}.csv",
                    mime="text/csv"
                )

        # ==================== TAB 2: PREDICTION ====================
        with tab2:
            st.header("🔮 Stock Price Prediction")
            
            pred_col1, pred_col2 = st.columns(2)
            
            with pred_col1:
                st.subheader("Single Date Prediction")
                prediction_date = st.date_input(
                    "Select Date for Prediction",
                    value=datetime.datetime.now().date(),
                    min_value=datetime.date(2000, 1, 1),
                    max_value=datetime.date(2100, 12, 31)
                )
                
                if st.button("🔮 Predict Price", key="single_predict"):
                    year, month, day = prediction_date.year, prediction_date.month, prediction_date.day
                    predicted_price = predict_open_price(year, month, day)
                    
                    # Check if we have actual data for this date
                    actual_price = None
                    if 'df_filtered' in dir() and 'Date' in df_filtered.columns:
                        actual_row = df_filtered[df_filtered['Date'].dt.date == prediction_date]
                        if not actual_row.empty and 'open' in actual_row.columns:
                            actual_price = actual_row['open'].values[0]
                    
                    # Display prediction
                    st.success(f"📈 Predicted Open Price for {prediction_date}: **${predicted_price:.2f}**")
                    
                    if actual_price is not None:
                        difference = predicted_price - actual_price
                        accuracy = (1 - abs(difference) / actual_price) * 100
                        
                        metric_col1, metric_col2, metric_col3 = st.columns(3)
                        metric_col1.metric("Predicted", f"${predicted_price:.2f}")
                        metric_col2.metric("Actual", f"${actual_price:.2f}")
                        metric_col3.metric("Accuracy", f"{accuracy:.1f}%", f"${difference:+.2f}")
                    
                    # Add to prediction history
                    new_pred = pd.DataFrame([{
                        'Date': prediction_date,
                        'Predicted_Open': predicted_price,
                        'Actual_Open': actual_price if actual_price else 'N/A',
                        'Difference': f"${difference:.2f}" if actual_price else 'N/A'
                    }])
                    st.session_state.prediction_history = pd.concat([st.session_state.prediction_history, new_pred], ignore_index=True)

            with pred_col2:
                st.subheader("Range Prediction")
                range_col1, range_col2 = st.columns(2)
                with range_col1:
                    range_start = st.date_input("Start Date", value=datetime.datetime.now().date(), key="range_start")
                with range_col2:
                    range_end = st.date_input("End Date", value=datetime.datetime.now().date() + datetime.timedelta(days=7), key="range_end")
                
                if st.button("🔮 Predict Range", key="range_predict"):
                    if range_start > range_end:
                        st.error("Start date must be before end date.")
                    else:
                        with st.spinner("Generating predictions..."):
                            predictions_df = predict_price_range(range_start, range_end)
                            
                            st.success(f"✅ Generated {len(predictions_df)} predictions")
                            
                            # Show predictions chart
                            pred_fig = px.line(
                                predictions_df, 
                                x='Date', 
                                y='Predicted_Open',
                                title=f"Predicted Prices: {range_start} to {range_end}",
                                markers=True
                            )
                            pred_fig.update_layout(xaxis_title="Date", yaxis_title="Predicted Price ($)")
                            st.plotly_chart(pred_fig, use_container_width=True)
                            
                            # Show predictions table
                            st.dataframe(predictions_df, use_container_width=True)
                            
                            # Download predictions
                            pred_csv = predictions_df.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label="📥 Download Predictions",
                                data=pred_csv,
                                file_name=f"predictions_{range_start}_to_{range_end}.csv",
                                mime="text/csv"
                            )

            # Prediction vs Actual Comparison
            st.subheader("📊 Prediction vs Actual Comparison")
            
            if 'df_filtered' in dir() and 'open' in df_filtered.columns:
                compare_df = df_filtered.copy()
                compare_df['Predicted_Open'] = compare_df.apply(
                    lambda row: predict_open_price(row['Date'].year, row['Date'].month, row['Date'].day) 
                    if pd.notna(row['Date']) else None, 
                    axis=1
                )
                
                # Comparison chart
                comp_fig = go.Figure()
                comp_fig.add_trace(go.Scatter(x=compare_df['Date'], y=compare_df['open'], mode='lines', name='Actual Price', line=dict(color='blue')))
                comp_fig.add_trace(go.Scatter(x=compare_df['Date'], y=compare_df['Predicted_Open'], mode='lines', name='Predicted Price', line=dict(color='red', dash='dash')))
                comp_fig.update_layout(title="Actual vs Predicted Prices", xaxis_title="Date", yaxis_title="Price ($)", hovermode='x unified')
                st.plotly_chart(comp_fig, use_container_width=True)

            # Prediction History
            st.subheader("📜 Prediction History")
            if not st.session_state.prediction_history.empty:
                st.dataframe(st.session_state.prediction_history, use_container_width=True)
                if st.button("🗑️ Clear History"):
                    st.session_state.prediction_history = pd.DataFrame(columns=['Date', 'Predicted_Open', 'Actual_Open', 'Difference'])
                    st.rerun()
            else:
                st.info("No predictions made yet. Use the prediction tools above.")

        # ==================== TAB 3: PORTFOLIO ====================
        with tab3:
            st.header("💼 Portfolio Management")

            port_col1, port_col2 = st.columns(2)
            
            with port_col1:
                st.subheader("Your Portfolio")
                st.text(st.session_state.portfolio.show_portfolio())
                
                st.subheader("Performance Summary")
                st.info(st.session_state.portfolio.show_performance_summary())

            with port_col2:
                st.subheader("Buy/Sell Stocks")
                action = st.radio("Select Action", ["Buy", "Sell"], horizontal=True)

                stock_symbol = st.selectbox("Select Stock", [stock.symbol for stock in st.session_state.market.stocks])
                selected_stock = st.session_state.market.get_stock(stock_symbol)
                
                if selected_stock:
                    st.caption(f"Current Price: ${selected_stock.price:.2f}")
                
                quantity = st.number_input("Quantity", min_value=1, value=1)
                total_cost = selected_stock.price * quantity if selected_stock else 0
                st.caption(f"Total: ${total_cost:.2f}")

                if action == "Buy":
                    if st.button("🛒 Buy", use_container_width=True):
                        result = st.session_state.portfolio.buy_stock(selected_stock, quantity)
                        st.success(result)
                elif action == "Sell":
                    if st.button("💰 Sell", use_container_width=True):
                        result = st.session_state.portfolio.sell_stock(stock_symbol, quantity)
                        st.success(result)

            # Transaction History
            st.subheader("📜 Transaction History")
            trans_history = st.session_state.portfolio.show_transaction_history()
            if not trans_history.empty:
                st.dataframe(trans_history, use_container_width=True)
            else:
                st.info("No transactions yet.")

        # ==================== TAB 4: STOCK MARKET ====================
        with tab4:
            st.header("📊 Stock Market")
            
            st.subheader("Available Stocks")
            
            market_data = []
            for stock in st.session_state.market.stocks:
                market_data.append({
                    "Name": stock.name,
                    "Symbol": stock.symbol,
                    "Price": f"${stock.price:.2f}",
                    "Dividend Yield": f"{stock.dividend_yield}%"
                })
            
            st.dataframe(pd.DataFrame(market_data), use_container_width=True)
            
            if st.button("🔄 Update Market Prices"):
                st.session_state.market.update_market()
                st.success("Market prices updated!")
                st.rerun()

# Run the app
if __name__ == "__main__":
    main()
