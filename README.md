# Inventory Optimizer AI - Smart Supply Chain Management

## Overview

Inventory Optimizer AI adalah aplikasi web canggih yang menggunakan artificial intelligence untuk mengoptimalkan manajemen inventory dan supply chain. Platform ini memberikan prediksi demand, rekomendasi purchase order otomatis, dan analisis kesehatan inventory secara real-time.

## Struktur Folder

```
inventory_optimizer/
├── app.py                          # Aplikasi Flask utama
├── requirements.txt                # Dependencies Python
├── run.py                         # Script startup otomatis
├── data/
│   ├── products_data.csv          # Data produk (200+ items)
│   ├── sales_data.csv             # Data penjualan (10,000+ transaksi)
│   └── inventory_data.csv         # Data inventory (6 bulan historis)
├── templates/
│   ├── index.html                 # Halaman landing page
│   ├── dashboard.html             # Dashboard analisis utama
│   └── error.html                 # Halaman error
└── static/
    ├── css/                       # Stylesheet (kosong - menggunakan inline CSS)
    ├── js/                        # JavaScript (kosong - menggunakan inline JS)
    └── images/                    # Asset gambar (kosong)
```

## Dataset yang Tersedia

### 1. Products Data (`products_data.csv`)
- **200+ produk** dengan berbagai kategori
- **Struktur data**: product_id, product_name, category, cost_price, selling_price, supplier
- **Kategori**: Electronics, Clothing, Home & Garden, Sports, Books, Beauty
- **Suppliers**: Supplier A, Supplier B, Supplier C, Supplier D

### 2. Sales Data (`sales_data.csv`)
- **10,000+ transaksi penjualan** dalam 6 bulan terakhir
- **Struktur data**: sale_id, product_id, date, quantity_sold, revenue
- **Pola musiman** dengan variasi holiday season dan post-holiday slump

### 3. Inventory Data (`inventory_data.csv`)
- **Data inventory mingguan** untuk semua produk
- **Struktur data**: product_id, date, current_stock
- **Snapshot reguler** untuk trend analysis dan pattern recognition

## Fitur AI & Analytics

### 1. Demand Prediction
- **Prediksi 30 hari ke depan** berdasarkan data historis
- **Seasonal adjustment** untuk hari dalam minggu dan bulan
- **Confidence level** (High/Medium) untuk setiap prediksi
- **Moving average analysis** dengan window 7 dan 30 hari

### 2. Optimal Stock Calculation
- **Safety stock calculation** dengan service level 95%
- **Reorder point** berdasarkan lead time demand
- **Optimal stock level** formula
- **Velocity categorization**: Fast-Moving, Medium-Moving, Slow-Moving, Dead-Stock

### 3. Automated Purchase Orders
- **Auto-generated POs** berdasarkan reorder point
- **Priority system**: Critical, High, Medium, Low
- **Order quantity optimization**
- **Lead time consideration** per supplier

### 4. Slow-Moving Inventory Identification
- **Days of supply analysis**
- **Promotion recommendations**: Clearance Sale, Bundle Promotion, Discount, Featured Placement
- **Potential loss calculation** untuk write-off risk
- **Inventory aging report**

### 5. Inventory Health Metrics
- **Overall health score** (0-100)
- **Service level percentage**
- **Overstock/Understock counts**
- **Inventory value analysis**

## Algoritma & Metodologi

### Demand Forecasting
```python
# Safety Stock Formula
safety_stock = std_daily_sold * lead_time_days * 1.65  # 95% service level

# Reorder Point
reorder_point = (avg_daily_sold * lead_time_days) + safety_stock

# Optimal Stock Level
optimal_stock = reorder_point * 1.5
```

### Velocity Categorization
- **Fast-Moving**: ≥ 10 unit/hari
- **Medium-Moving**: ≥ 5 unit/hari  
- **Slow-Moving**: ≥ 1 unit/hari
- **Dead-Stock**: < 1 unit/hari

### Priority System
- **Critical**: Stock ≤ 30% reorder point
- **High**: Stock ≤ 60% reorder point
- **Medium**: Stock ≤ 80% reorder point
- **Low**: Stock > 80% reorder point

## Teknologi & Dependencies

### Backend Framework
- **Flask 2.3.3** - Web framework ringan
- **Werkzeug 2.3.7** - WSGI utilities

### Data Analysis & Machine Learning
- **pandas 2.1.4** - Data manipulation dan analysis
- **numpy 1.26.0** - Komputasi numerik
- **scikit-learn 1.3.2** - Machine learning algorithms
- **matplotlib 3.8.2** - Static visualizations
- **seaborn 0.13.0** - Statistical visualizations
- **plotly 5.17.0** - Interactive charts

### Data Generation & Processing
- **faker 21.0.0** - Sample data generation

### Frontend Technologies
- **HTML5/CSS3** - Responsive design dengan tema biru
- **Vanilla JavaScript** - Client-side interactions
- **Font Awesome 6.0.0** - Ikon UI
- **Plotly.js** - Interactive gauge charts
- **Google Fonts (Inter)** - Modern typography

## Cara Menjalankan

### Opsi 1: Script Otomatis (Recommended)
```bash
cd inventory_optimizer
python run.py
```

### Opsi 2: Manual Execution
```bash
cd inventory_optimizer

# Install dependencies
pip install -r requirements.txt

# Jalankan aplikasi
python app.py
```

### Akses Aplikasi
Buka browser dan kunjungi: `http://localhost:5000`

## API Endpoints

### Main Routes
- `GET /` - Landing page dengan overview fitur
- `GET /dashboard` - Dashboard analisis utama
- `GET /api/purchase_orders` - Data purchase orders (JSON)
- `GET /api/slow_movers` - Data slow-moving inventory (JSON)

## Visualisasi & Dashboard

### Charts & Metrics
1. **Inventory Health Donut Chart** - Distribusi kesehatan inventory
2. **Service Level Gauge** - Interactive gauge chart untuk service level
3. **Purchase Orders Table** - Rekomendasi PO dengan priority system
4. **Slow-Moving Inventory Table** - Inventory butuh perhatian
5. **Demand Forecast Table** - Prediksi 10 hari ke depan

### Key Metrics Display
- **Inventory Health Score** - Overall health (0-100)
- **Total Products** - Jumlah produk dalam sistem
- **Understock Risk** - Produk dengan stock rendah
- **Service Level** - Persentase service level

## Business Intelligence Features

### Inventory Optimization
- **Reduced Stockouts** - Dengan accurate demand prediction
- **Minimized Overstock** - Melalui optimal stock calculation
- **Improved Cash Flow** - Dengan inventory turnover yang better
- **Enhanced Service Level** - Melalui safety stock optimization

### Supply Chain Efficiency
- **Automated Reordering** - Mengurangi manual work
- **Supplier Performance** - Lead time consideration
- **Cost Optimization** - Melalui optimal order quantities
- **Risk Management** - Dengan safety stock calculation

## Use Cases

### Untuk Inventory Manager
- **Proactive stock management** dengan demand prediction
- **Automated purchase ordering** mengurangi manual work
- **Slow-moving identification** untuk cash flow improvement
- **Supplier performance tracking** melalui lead time analysis

### Untuk Supply Chain Director
- **Overall inventory health** monitoring
- **Service level optimization**
- **Cost reduction opportunities**
- **Strategic decision support**

### Untuk Finance Team
- **Inventory valuation** insights
- **Cash flow forecasting** melalui inventory planning
- **Cost of goods sold** optimization
- **Write-off risk identification**

## Customization & Configuration

### Modifikasi Safety Stock Level
Edit di method `calculate_optimal_stock`:
```python
# 95% service level (Z-score = 1.65)
safety_stock = std_daily_sold * lead_time_days * 1.65

# Untuk 99% service level (Z-score = 2.33)
safety_stock = std_daily_sold * lead_time_days * 2.33
```

### Menambah Kategori Produk
Edit variabel `categories` dalam data generator:
```python
categories = ['Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Books', 'Beauty', 'New Category']
```

### Adjust Velocity Thresholds
Modifikasi conditions dalam `calculate_optimal_stock`:
```python
conditions = [
    df['avg_daily_sold'] >= 15,  # Fast-Moving threshold
    df['avg_daily_sold'] >= 8,   # Medium-Moving threshold
    df['avg_daily_sold'] >= 2    # Slow-Moving threshold
]
```

## Data Security & Privacy

- **Local data storage** - Semua data disimpan secara lokal
- **No external dependencies** - Tidak ada API calls keluar
- **Session management** - Dengan secret key encryption
- **On-premise ready** - Dapat di-deploy di environment tertutup

## Performance Considerations

- **Efficient data processing** dengan pandas operations
- **Lazy loading** untuk large datasets
- **Cached calculations** untuk frequent operations
- **Optimized visualizations** dengan appropriate chart types

## Support & Troubleshooting

### Common Issues
1. **Port 5000 unavailable** - Ganti port: `app.run(port=5001)`
2. **Import errors** - Pastikan semua dependencies terinstall
3. **Data loading failed** - Check file existence di folder `data/`

### Debug Mode
- Enable: `app.run(debug=True)`
- Check console untuk error messages
- Validasi data format di CSV files

## Deployment Recommendations

### Untuk Production
1. **Disable debug mode**: `app.run(debug=False)`
2. **Use production WSGI server**: Gunicorn atau uWSGI
3. **Environment variables** untuk configuration
4. **Database integration** untuk persistent storage

### Scaling Considerations
- **Database migration** ke PostgreSQL/MySQL
- **Caching layer** dengan Redis
- **Load balancing** untuk multiple instances
- **Background processing** untuk heavy calculations

## License & Usage

MIT License - Bebas untuk penggunaan komersial dan non-komersial. Dapat dikustomisasi sesuai kebutuhan supply chain spesifik.

---

**Inventory Optimizer AI** - Mentransformasi manajemen inventory dari reactive menjadi proactive melalui predictive analytics dan automated optimization.
