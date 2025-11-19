from flask import Flask, render_template, request, jsonify, session
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import base64
import json
import random
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import os
import warnings
warnings.filterwarnings('ignore')

# Setup matplotlib untuk non-GUI environment
plt.switch_backend('Agg')

app = Flask(__name__)
app.secret_key = 'inventory_optimizer_secret_2024'

class InventoryOptimizer:
    def __init__(self):
        self.sales_data = None
        self.inventory_data = None
        self.products_data = None
        
    def load_data(self):
        """Load data dari file CSV"""
        try:
            self.sales_data = pd.read_csv('data/sales_data.csv')
            self.inventory_data = pd.read_csv('data/inventory_data.csv')
            self.products_data = pd.read_csv('data/products_data.csv')
            
            # Convert date columns
            self.sales_data['date'] = pd.to_datetime(self.sales_data['date'])
            self.inventory_data['date'] = pd.to_datetime(self.inventory_data['date'])
            
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def predict_demand(self, product_id=None, days=30):
        """Predict demand untuk 30 hari ke depan"""
        if product_id:
            product_sales = self.sales_data[self.sales_data['product_id'] == product_id]
        else:
            product_sales = self.sales_data
            
        # Aggregasi sales harian
        daily_sales = product_sales.groupby('date').agg({
            'quantity_sold': 'sum',
            'revenue': 'sum'
        }).reset_index()
        
        # Feature engineering
        daily_sales['day_of_week'] = daily_sales['date'].dt.dayofweek
        daily_sales['month'] = daily_sales['date'].dt.month
        daily_sales['is_weekend'] = daily_sales['day_of_week'].isin([5, 6]).astype(int)
        
        # Simple moving average prediction
        daily_sales['ma_7'] = daily_sales['quantity_sold'].rolling(window=7).mean()
        daily_sales['ma_30'] = daily_sales['quantity_sold'].rolling(window=30).mean()
        
        # Prediksi sederhana (dalam production gunakan model ML)
        last_ma = daily_sales['ma_30'].iloc[-1]
        if pd.isna(last_ma):
            last_ma = daily_sales['quantity_sold'].mean()
        
        # Generate predictions
        future_dates = [datetime.now() + timedelta(days=i) for i in range(1, days+1)]
        predictions = []
        
        for i, date in enumerate(future_dates):
            # Seasonal adjustment based on day of week
            day_of_week = date.weekday()
            seasonal_factor = 1.2 if day_of_week in [0, 4] else 1.0  # Monday & Friday higher
            seasonal_factor = 0.8 if day_of_week in [2, 3] else seasonal_factor  # Wed & Thu lower
            
            predicted_qty = max(0, last_ma * seasonal_factor * random.uniform(0.9, 1.1))
            
            predictions.append({
                'date': date.strftime('%Y-%m-%d'),
                'predicted_demand': round(predicted_qty),
                'confidence': 'High' if i < 7 else 'Medium'
            })
        
        return predictions
    
    def calculate_optimal_stock(self):
        """Hitung optimal stock level untuk setiap produk"""
        # Analisis sales velocity
        sales_velocity = self.sales_data.groupby('product_id').agg({
            'quantity_sold': ['sum', 'mean', 'std'],
            'revenue': 'sum'
        }).round(2)
        
        sales_velocity.columns = ['total_sold', 'avg_daily_sold', 'std_daily_sold', 'total_revenue']
        sales_velocity = sales_velocity.reset_index()
        
        # Merge dengan product data
        stock_recommendations = pd.merge(sales_velocity, self.products_data, on='product_id')
        
        # Hitung optimal stock level (safety stock + lead time demand)
        stock_recommendations['lead_time_days'] = stock_recommendations['supplier'].map({
            'Supplier A': 7, 'Supplier B': 5, 'Supplier C': 10, 'Supplier D': 3
        })
        
        # Safety stock formula
        stock_recommendations['safety_stock'] = (stock_recommendations['std_daily_sold'] * 
                                               stock_recommendations['lead_time_days'] * 1.65)  # 95% service level
        
        # Reorder point
        stock_recommendations['reorder_point'] = (stock_recommendations['avg_daily_sold'] * 
                                                stock_recommendations['lead_time_days'] + 
                                                stock_recommendations['safety_stock'])
        
        # Optimal stock level
        stock_recommendations['optimal_stock'] = stock_recommendations['reorder_point'] * 1.5
        
        # Kategori produk berdasarkan velocity
        conditions = [
            stock_recommendations['avg_daily_sold'] >= 10,
            stock_recommendations['avg_daily_sold'] >= 5,
            stock_recommendations['avg_daily_sold'] >= 1
        ]
        choices = ['Fast-Moving', 'Medium-Moving', 'Slow-Moving']
        stock_recommendations['velocity_category'] = np.select(conditions, choices, default='Dead-Stock')
        
        return stock_recommendations
    
    def generate_purchase_orders(self):
        """Generate purchase order recommendations"""
        stock_recommendations = self.calculate_optimal_stock()
        current_inventory = self.inventory_data.groupby('product_id')['current_stock'].last().reset_index()
        
        # Merge dengan current stock
        po_candidates = pd.merge(stock_recommendations, current_inventory, on='product_id', how='left')
        po_candidates['current_stock'] = po_candidates['current_stock'].fillna(0)
        
        # Identifikasi produk yang perlu reorder
        po_candidates['need_reorder'] = po_candidates['current_stock'] <= po_candidates['reorder_point']
        po_candidates['order_quantity'] = np.where(
            po_candidates['need_reorder'],
            (po_candidates['optimal_stock'] - po_candidates['current_stock']).clip(lower=0),
            0
        )
        
        # Filter hanya yang perlu order
        purchase_orders = po_candidates[po_candidates['order_quantity'] > 0].copy()
        
        # Prioritaskan berdasarkan criticality
        def calculate_criticality(row):
            stock_ratio = row['current_stock'] / row['reorder_point'] if row['reorder_point'] > 0 else 0
            if stock_ratio <= 0.3:
                return 'Critical'
            elif stock_ratio <= 0.6:
                return 'High'
            elif stock_ratio <= 0.8:
                return 'Medium'
            else:
                return 'Low'
        
        purchase_orders['priority'] = purchase_orders.apply(calculate_criticality, axis=1)
        
        # Format PO data
        po_list = []
        for _, row in purchase_orders.iterrows():
            po_list.append({
                'product_id': row['product_id'],
                'product_name': row['product_name'],
                'supplier': row['supplier'],
                'current_stock': int(row['current_stock']),
                'reorder_point': int(row['reorder_point']),
                'order_quantity': int(row['order_quantity']),
                'priority': row['priority'],
                'estimated_cost': round(row['order_quantity'] * row['cost_price'], 2),
                'lead_time_days': row['lead_time_days']
            })
        
        return po_list
    
    def identify_slow_moving_inventory(self):
        """Identifikasi slow-moving inventory untuk promo"""
        stock_analysis = self.calculate_optimal_stock()
        current_inventory = self.inventory_data.groupby('product_id')['current_stock'].last().reset_index()
        
        # Merge data
        inventory_analysis = pd.merge(stock_analysis, current_inventory, on='product_id', how='left')
        inventory_analysis['current_stock'] = inventory_analysis['current_stock'].fillna(0)
        
        # Hitung days of supply
        inventory_analysis['days_of_supply'] = np.where(
        inventory_analysis['avg_daily_sold'] > 0,
        inventory_analysis['current_stock'] / inventory_analysis['avg_daily_sold'],
        999  # Untuk produk yang tidak terjual
        )
        # Handle division by zero lebih aman
        inventory_analysis['days_of_supply'] = inventory_analysis['days_of_supply'].replace([np.inf, -np.inf], 999)
                
        # Identifikasi slow-movers
        slow_movers = inventory_analysis[
            (inventory_analysis['days_of_supply'] > 60) |  # Stok > 60 hari
            (inventory_analysis['velocity_category'] == 'Slow-Moving') |
            (inventory_analysis['velocity_category'] == 'Dead-Stock')
        ].copy()
        
        # Rekomendasi promo
        def generate_promo_recommendation(row):
            if row['days_of_supply'] > 120:
                return 'Clearance Sale - 50% Off'
            elif row['days_of_supply'] > 90:
                return 'Bundle Promotion - Buy 1 Get 1'
            elif row['days_of_supply'] > 60:
                return 'Discount - 25% Off'
            else:
                return 'Featured Placement'
        
        slow_movers['promo_recommendation'] = slow_movers.apply(generate_promo_recommendation, axis=1)
        
        # Format output
        promo_list = []
        for _, row in slow_movers.iterrows():
            promo_list.append({
                'product_id': row['product_id'],
                'product_name': row['product_name'],
                'category': row['category'],
                'current_stock': int(row['current_stock']),
                'avg_daily_sold': round(row['avg_daily_sold'], 1),
                'days_of_supply': int(row['days_of_supply']),
                'velocity_category': row['velocity_category'],
                'promo_recommendation': row['promo_recommendation'],
                'potential_loss': round(row['current_stock'] * row['cost_price'] * 0.3, 2)  # 30% write-off risk
            })
        
        return promo_list
    
    def calculate_inventory_health(self):
        """Hitung overall inventory health metrics"""
        stock_recommendations = self.calculate_optimal_stock()
        current_inventory = self.inventory_data.groupby('product_id')['current_stock'].last().reset_index()
        
        # Merge data
        health_data = pd.merge(stock_recommendations, current_inventory, on='product_id', how='left')
        health_data['current_stock'] = health_data['current_stock'].fillna(0)
        
        # Hitung metrics
        total_products = len(health_data)
        
        # Overstock (stok > 2x optimal)
        overstock_count = len(health_data[health_data['current_stock'] > health_data['optimal_stock'] * 2])
        
        # Understock (stok < reorder point)
        understock_count = len(health_data[health_data['current_stock'] < health_data['reorder_point']])
        
        # Optimal stock
        optimal_count = total_products - overstock_count - understock_count
        
        # Inventory value
        total_inventory_value = (health_data['current_stock'] * health_data['cost_price']).sum()
        overstock_value = (health_data[health_data['current_stock'] > health_data['optimal_stock'] * 2]['current_stock'] * 
                        health_data[health_data['current_stock'] > health_data['optimal_stock'] * 2]['cost_price']).sum()
        
        # Service level estimation - FIXED: Handle division by zero
        high_demand_products = health_data[health_data['velocity_category'] == 'Fast-Moving']
        if len(high_demand_products) > 0:
            service_level = len(high_demand_products[high_demand_products['current_stock'] > 0]) / len(high_demand_products) * 100
        else:
            service_level = 0  # Default value jika tidak ada Fast-Moving products
        
        return {
            'total_products': total_products,
            'overstock_count': overstock_count,
            'understock_count': understock_count,
            'optimal_count': optimal_count,
            'total_inventory_value': round(total_inventory_value, 2),
            'overstock_value': round(overstock_value, 2),
            'service_level': round(service_level, 1),
            'health_score': max(0, 100 - (overstock_count/total_products*50) - (understock_count/total_products*50))
        }
    
    def generate_visualizations(self, health_metrics):
        """Generate visualisasi data"""
        visualizations = {}
        
        # Color palette - biru monokrom
        blue_palette = ['#1E3A8A', '#3B82F6', '#60A5FA', '#93C5FD', '#DBEAFE']
        
        # 1. Inventory Health Donut Chart
        fig1, ax1 = plt.subplots(figsize=(8, 8))
        sizes = [health_metrics['optimal_count'], health_metrics['overstock_count'], health_metrics['understock_count']]
        labels = ['Optimal', 'Overstock', 'Understock']
        colors = [blue_palette[1], blue_palette[3], blue_palette[4]]
        
        ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax1.set_title('Inventory Health Distribution', fontsize=14, fontweight='bold', color=blue_palette[0])
        
        img1 = io.BytesIO()
        plt.savefig(img1, format='png', bbox_inches='tight', facecolor='#FFFFFF')
        img1.seek(0)
        visualizations['health_donut'] = base64.b64encode(img1.getvalue()).decode()
        plt.close(fig1)
        
        # 2. Service Level Gauge
        fig2 = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = health_metrics['service_level'],
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Service Level %", 'font': {'color': blue_palette[0]}},
            delta = {'reference': 90, 'increasing': {'color': blue_palette[1]}},
            gauge = {
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': blue_palette[0]},
                'bar': {'color': blue_palette[1]},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': blue_palette[0],
                'steps': [
                    {'range': [0, 80], 'color': blue_palette[4]},
                    {'range': [80, 95], 'color': blue_palette[2]},
                    {'range': [95, 100], 'color': blue_palette[1]}],
                'threshold': {
                    'line': {'color': blue_palette[0], 'width': 4},
                    'thickness': 0.75,
                    'value': 90}}))
        
        fig2.update_layout(font = {'color': blue_palette[0], 'family': "Arial"})
        visualizations['service_gauge'] = fig2.to_html()
        
        return visualizations

# Initialize optimizer
optimizer = InventoryOptimizer()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if not optimizer.load_data():
        return render_template('error.html', message="Failed to load data")
    
    # Analisis data
    health_metrics = optimizer.calculate_inventory_health()
    purchase_orders = optimizer.generate_purchase_orders()
    slow_movers = optimizer.identify_slow_moving_inventory()
    demand_predictions = optimizer.predict_demand()
    
    # Generate visualizations
    visuals = optimizer.generate_visualizations(health_metrics)
    
    return render_template('dashboard.html',
                         health_metrics=health_metrics,
                         purchase_orders=purchase_orders,
                         slow_movers=slow_movers,
                         demand_predictions=demand_predictions[:10],  # 10 predictions saja
                         visuals=visuals)

@app.route('/api/purchase_orders')
def api_purchase_orders():
    if not optimizer.load_data():
        return jsonify({'error': 'Data loading failed'})
    
    purchase_orders = optimizer.generate_purchase_orders()
    return jsonify(purchase_orders)

@app.route('/api/slow_movers')
def api_slow_movers():
    if not optimizer.load_data():
        return jsonify({'error': 'Data loading failed'})
    
    slow_movers = optimizer.identify_slow_moving_inventory()
    return jsonify(slow_movers)

if __name__ == '__main__':
    print("Starting Inventory Optimizer AI...")
    print("Access the application at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
