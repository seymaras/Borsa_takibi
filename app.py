from flask import Flask, json, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler

app = Flask(__name__)
app.secret_key = "secret_key"

# Veritabanı bağlantısı
def create_connection(db_name="stocks.db"):
    return sqlite3.connect(db_name)

# Kullanıcı tablosu oluşturma
def create_user_table():
    conn = create_connection("users.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

# Hisseler tablosunu oluşturma
def create_stocks_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stocks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        symbol TEXT NOT NULL,
        date DATE NOT NULL,
        value DECIMAL(10, 2),
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)
    conn.commit()
    conn.close()
# Portföy tablosunu oluşturma
def create_portfolio_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS portfolios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        symbol TEXT NOT NULL,
        quantity INTEGER,
        purchase_price DECIMAL(10, 2),
        purchase_date DATE,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)
    conn.commit()
    conn.close()

# Ana sayfa
@app.route('/')
def index():
    return render_template('index.html')

# Hisse tahmini için sayfa
@app.route("/predict", methods=["GET", "POST"])
def predict():
    if request.method == "POST":
        try:
            data = request.get_json()
            symbol = data['symbol'].upper().strip()
            if not symbol.endswith('.IS'):
                symbol = f"{symbol}.IS"
            target_date = data['date']

            # Veri çekme süresini artır
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365*2)  # 2 yıllık veri
            df = yf.download(symbol, start=start_date, end=end_date, progress=False)

            if df.empty:
                return jsonify({"error": f"{symbol} için veri bulunamadı."}), 404

            # Özellik mühendisliği
            df['MA20'] = df['Close'].rolling(window=20, min_periods=1).mean()
            df['MA50'] = df['Close'].rolling(window=50, min_periods=1).mean()
            df['MA200'] = df['Close'].rolling(window=200, min_periods=1).mean()
            df['RSI'] = calculate_rsi(df['Close'])
            df['Volatility'] = df['Close'].rolling(window=20, min_periods=1).std()

            # Son değerleri al
            last_price = float(df['Close'].iloc[-1])
            
            # Teknik analiz değerlerini hesapla
            ma20 = float(df['MA20'].iloc[-1])
            ma50 = float(df['MA50'].iloc[-1])
            rsi = float(df['RSI'].iloc[-1]) if not np.isnan(df['RSI'].iloc[-1]) else 50
            volatility = float(df['Volatility'].iloc[-1])

            # Trend analizi
            trend = "Yükseliş" if ma20 > ma50 else "Düşüş"
            rsi_signal = "Aşırı Alım" if rsi > 70 else "Aşırı Satım" if rsi < 30 else "Nötr"

            # Tahmin için özellikleri hazırla
            features = np.array([[ma20, ma50, rsi, volatility]])

            # Modeli eğit
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            X = df[['MA20', 'MA50', 'RSI', 'Volatility']].iloc[:-1].values
            y = df['Close'].iloc[1:].values
            
            # NaN değerleri 0 ile doldur
            X = np.nan_to_num(X)
            y = np.nan_to_num(y)
            
            model.fit(X, y)

            # Tahmin
            prediction = model.predict(features)[0]
            price_change = ((prediction - last_price) / last_price) * 100

            return jsonify({
                "symbol": symbol,
                "current_price": round(last_price, 2),
                "predicted_price": round(prediction, 2),
                "price_change": round(price_change, 2),
                "target_date": target_date,
                "technical_analysis": {
                    "ma20": round(ma20, 2),
                    "ma50": round(ma50, 2),
                    "rsi": round(rsi, 2),
                    "trend": trend,
                    "rsi_signal": rsi_signal
                }
            })

        except Exception as e:
            return jsonify({"error": f"Analiz yapılırken bir hata oluştu: {str(e)}"}), 400

    return render_template("tahmin.html")

def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# Kayıt ol
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = create_connection("users.db")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            flash("Kayıt başarılı!", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Bu kullanıcı adı zaten alınmış!", "danger")
        conn.close()

    return render_template("register.html")

# Giriş yap
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = create_connection("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        if user:
            flash(f"Hoş geldin, {username}!", "success")
            session["username"] = username
            session["id"] = user[0]
            return redirect(url_for("tahmin"))
        else:
            flash("Kullanıcı adı veya şifre yanlış!", "danger")
        conn.close()

    return render_template("login.html")

# Çıkış yap
@app.route("/logout", methods=["POST"])
def logout():
    session.pop("username", None)
    flash("Başarıyla çıkış yaptınız.", "success")
    return redirect(url_for("tahmin"))

# Tahmin sayfası
@app.route('/tahmin', methods=['GET', 'POST'])
def tahmin():
    if "username" not in session:
        flash("Lütfen önce giriş yapın!", "danger")
        return redirect(url_for("login"))

    # Tahmin işlemleri burada yapılacak
    return render_template('tahmin.html')

@app.route('/add_to_portfolio', methods=['POST'])
def add_to_portfolio():
    if "username" not in session:
        return jsonify({"error": "Lütfen giriş yapın"}), 401
    
    try:
        data = request.get_json()
        symbol = data.get('symbol').upper()
        if not symbol.endswith('.IS'):
            symbol = f"{symbol}.IS"
        quantity = data.get('quantity')
        purchase_price = data.get('purchase_price')
        
        conn = create_connection()
        cursor = conn.cursor()
        
        # Portföye hisse ekleme
        cursor.execute("""
        INSERT INTO portfolios (user_id, symbol, quantity, purchase_price, purchase_date)
        VALUES (?, ?, ?, ?, ?)
        """, (session['id'], symbol, quantity, purchase_price, datetime.now().date()))
        
        conn.commit()
        conn.close()
        
        return jsonify({"message": "Hisse portföye başarıyla eklendi"})
        
    except Exception as e:
        return jsonify({"error": f"Hisse eklenirken bir hata oluştu: {str(e)}"}), 400

@app.route('/get_portfolio', methods=['GET'])
def get_portfolio():
    if "username" not in session:
        return jsonify({"error": "Lütfen giriş yapın"}), 401
    
    try:
        conn = create_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT symbol, quantity, purchase_price, purchase_date 
        FROM portfolios 
        WHERE user_id = ?
        """, (session['id'],))
        
        portfolio = cursor.fetchall()
        
        portfolio_data = []
        for item in portfolio:
            symbol, quantity, purchase_price, purchase_date = item
            
            try:
                df = yf.download(symbol, start=datetime.now() - timedelta(days=1), 
                               end=datetime.now(), progress=False)
                current_price = float(df['Close'].iloc[-1])
                
                profit_loss = (current_price - purchase_price) * quantity
                profit_loss_percentage = ((current_price - purchase_price) / purchase_price) * 100
                
                portfolio_data.append({
                    "symbol": symbol,
                    "quantity": quantity,
                    "purchase_price": purchase_price,
                    "purchase_date": purchase_date,
                    "current_price": round(current_price, 2),
                    "profit_loss": round(profit_loss, 2),
                    "profit_loss_percentage": round(profit_loss_percentage, 2)
                })
            except:
                continue
        
        conn.close()
        return jsonify({"portfolio": portfolio_data})
    except Exception as e:
        return jsonify({"error": f"Portföy bilgileri alınırken bir hata oluştu: {str(e)}"}), 400

@app.route('/get_predictions')
def get_predictions():
    if "username" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT symbol, date, value 
            FROM stocks 
            WHERE user_id = ? 
            ORDER BY date DESC 
            LIMIT 5
        """, (session['id'],))
        predictions = cursor.fetchall()
        conn.close()
        
        return jsonify([{
            "symbol": pred[0],
            "date": pred[1],
            "value": pred[2]
        } for pred in predictions])
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Program giriş noktası
if __name__ == "__main__":
    create_user_table()
    create_stocks_table()
    create_portfolio_table()
    app.run(debug=True, port=5001)

