from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_mysqldb import MySQL
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
import pandas as pd
import numpy as np
import os
from werkzeug.utils import secure_filename
import pymysql
import json
import plotly.graph_objs as go
import plotly
import io

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Ganti dengan secret key yang aman

# Inisialisasi Flask-Login dan Bcrypt
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

bcrypt = Bcrypt(app)

# Konfigurasi MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Ganti sesuai user MySQL Anda
app.config['MYSQL_PASSWORD'] = ''  # Ganti sesuai password MySQL Anda
app.config['MYSQL_DB'] = 'investment_db'

mysql = MySQL(app)

UPLOAD_FOLDER = 'data'
ALLOWED_EXTENSIONS = {'csv', 'xls', 'xlsx', 'json'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class User(UserMixin):
    def __init__(self, id, username, email, password):
        self.id = id
        self.username = username
        self.email = email
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    if user:
        return User(id=user[0], username=user[1], email=user[2], password=user[3])
    return None

def normalize_matrix(matrix):
    column_sums = np.sum(matrix, axis=0)
    normalized = matrix / column_sums
    return normalized

def calculate_ahp_weights(ahp_matrix):
    normalized = normalize_matrix(ahp_matrix)
    weights = np.mean(normalized, axis=1)
    weights = weights / np.sum(weights)
    return weights

def normalize_alternatives(alternatives, criteria, criteria_types):
    normalized = alternatives.copy()
    for crit in criteria:
        if criteria_types[crit] == 'benefit':
            max_val = alternatives[crit].max()
            if max_val == 0:
                normalized[crit] = 0
            else:
                normalized[crit] = alternatives[crit] / max_val
        elif criteria_types[crit] == 'cost':
            min_val = alternatives[crit].min()
            normalized[crit] = alternatives[crit].apply(lambda x: min_val / x if x != 0 else 0)
    return normalized

def calculate_wp_scores(normalized_alternatives, weights, criteria, criteria_types):
    S = []
    for idx, row in normalized_alternatives.iterrows():
        product = 1
        for crit in criteria:
            value = row[crit]
            weight = weights[crit]
            product *= value ** weight
        S.append(product)
    sum_S = sum(S)
    V = [s_i / sum_S for s_i in S]
    normalized_alternatives['S'] = S
    normalized_alternatives['V'] = V
    return normalized_alternatives

def calculate_consistency_ratio(ahp_matrix, weights):
    n = ahp_matrix.shape[0]
    weighted_sum = np.dot(ahp_matrix, weights)
    lambda_max = np.mean(weighted_sum / weights)
    CI = (lambda_max - n) / (n - 1)
    RI_dict = {1:0, 2:0, 3:0.58, 4:0.90, 5:1.12, 6:1.24, 7:1.32, 8:1.41, 9:1.45}
    RI = RI_dict.get(n, 1.49)
    CR = CI / RI
    return CR

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Password dan konfirmasi password tidak cocok.', 'danger')
            return redirect(url_for('register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        cursor = mysql.connection.cursor()
        try:
            cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", 
                           (username, email, hashed_password))
            mysql.connection.commit()
            flash('Akun berhasil dibuat. Silakan login.', 'success')
            return redirect(url_for('login'))
        except pymysql.err.IntegrityError:
            flash('Username atau email sudah digunakan.', 'danger')
            return redirect(url_for('register'))
        finally:
            cursor.close()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_or_username = request.form['email_or_username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s OR username = %s", (email_or_username, email_or_username))
        user = cursor.fetchone()
        cursor.close()

        if user and bcrypt.check_password_hash(user[3], password):
            user_obj = User(id=user[0], username=user[1], email=user[2], password=user[3])
            login_user(user_obj)
            flash('Berhasil login.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Email/Username atau password salah.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('login'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password and password != confirm_password:
            flash('Password dan konfirmasi password tidak cocok.', 'danger')
            return redirect(url_for('profile'))

        if password:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            query = "UPDATE users SET username=%s, email=%s, password=%s WHERE id=%s"
            params = (username, email, hashed_password, current_user.id)
        else:
            query = "UPDATE users SET username=%s, email=%s WHERE id=%s"
            params = (username, email, current_user.id)

        try:
            cursor.execute(query, params)
            mysql.connection.commit()
            flash('Profil berhasil diperbarui.', 'success')
        except pymysql.err.IntegrityError:
            flash('Username atau email sudah digunakan.', 'danger')
        finally:
            cursor.close()
            return redirect(url_for('profile'))
    else:
        cursor.execute("SELECT username, email FROM users WHERE id=%s", (current_user.id,))
        user = cursor.fetchone()
        cursor.close()
        return render_template('profile.html', user=user)

@app.route('/dashboard')
@login_required
def dashboard():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM alternatives WHERE user_id = %s", (current_user.id,))
    count_alternatives = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(score) FROM results WHERE user_id = %s", (current_user.id,))
    avg_score = cursor.fetchone()[0] or 0

    cursor.execute("""
        SELECT filename, created_at FROM results
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT 5
    """, (current_user.id,))
    recent_uploads = cursor.fetchall()

    cursor.execute("SELECT sector FROM alternatives WHERE user_id = %s", (current_user.id,))
    sectors = cursor.fetchall()
    cursor.close()

    sector_counts = {}
    for sector in sectors:
        sector_name = sector[0]
        if sector_name in sector_counts:
            sector_counts[sector_name] += 1
        else:
            sector_counts[sector_name] = 1

    sector_labels = list(sector_counts.keys())
    sector_data = list(sector_counts.values())

    return render_template('dashboard.html', 
                           count_alternatives=count_alternatives, 
                           avg_score=avg_score, 
                           recent_uploads=recent_uploads,
                           sector_labels=sector_labels,
                           sector_data=sector_data)

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Tidak ada file yang diunggah', 'danger')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('Tidak ada file yang dipilih', 'danger')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            file_ext = filename.rsplit('.', 1)[1].lower()
            try:
                if file_ext == 'csv':
                    data = pd.read_csv(filepath)
                elif file_ext in ['xls', 'xlsx']:
                    data = pd.read_excel(filepath)
                elif file_ext == 'json':
                    data = pd.read_json(filepath)
                else:
                    flash('Format file tidak didukung', 'danger')
                    return redirect(request.url)
            except Exception as e:
                flash(f'Terjadi kesalahan saat membaca file: {str(e)}', 'danger')
                return redirect(request.url)
            
            required_columns = ['alternatif', 'Laju Pertumbuhan Kumulatif (c-to-c)',
                                'Laju Pertumbuhan Triwulanan Berantai (q-to-q)',
                                'Laju Pertumbuhan Triwulanan terhadap Triwulan yang Sama Tahun Sebelumnya (y-on-y)',
                                'Pengangguran', 'Inflasi']
            if not all(col in data.columns for col in required_columns):
                flash('Format file salah. Pastikan semua kolom yang diperlukan ada.', 'danger')
                return redirect(request.url)
            
            cursor = mysql.connection.cursor()
            try:
                for _, row in data.iterrows():
                    cursor.execute("""
                        INSERT INTO alternatives (sector, c_to_c_growth, q_to_q_growth, y_on_y_growth, unemployment, inflation, user_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (row['alternatif'], row['Laju Pertumbuhan Kumulatif (c-to-c)'],
                          row['Laju Pertumbuhan Triwulanan Berantai (q-to-q)'],
                          row['Laju Pertumbuhan Triwulanan terhadap Triwulan yang Sama Tahun Sebelumnya (y-on-y)'],
                          row['Pengangguran'], row['Inflasi'], current_user.id))
                mysql.connection.commit()
                flash('Data berhasil di-upload dan disimpan.', 'success')
            except Exception as e:
                mysql.connection.rollback()
                flash(f'Terjadi kesalahan saat menyimpan data ke database: {str(e)}', 'danger')
            finally:
                cursor.close()

            try:
                df = data.copy()
                df['user_id'] = current_user.id
                df.to_csv(os.path.join(app.config['UPLOAD_FOLDER'], 'data.csv'), index=False)
            except Exception as e:
                flash(f'Terjadi kesalahan saat menyimpan data ke CSV: {str(e)}', 'warning')

            return redirect(url_for('results', filename=filename))
        else:
            flash('Tipe file yang diizinkan: CSV, Excel (.xls, .xlsx), JSON', 'danger')
            return redirect(request.url)
    return render_template('index.html')

@app.route('/results/<filename>')
@login_required
def results(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        flash('File tidak ditemukan', 'danger')
        return redirect(url_for('index'))
    
    try:
        file_ext = filename.rsplit('.', 1)[1].lower()
        if file_ext == 'csv':
            data = pd.read_csv(filepath)
        elif file_ext in ['xls', 'xlsx']:
            data = pd.read_excel(filepath)
        elif file_ext == 'json':
            data = pd.read_json(filepath)
        else:
            flash('Format file tidak didukung untuk analisis.', 'danger')
            return redirect(url_for('index'))
    except Exception as e:
        flash('Terjadi kesalahan saat membaca file.', 'danger')
        return redirect(url_for('index'))
    
    ahp_matrix = np.array([
        [1,    3,    2,    4,    5],
        [1/3,  1,    2,    3,    4],
        [0.5,  0.5,  1,    3,    3],
        [0.25, 0.33, 0.33, 1,    2],
        [0.2,  0.25, 0.33, 0.5,  1]
    ])
    
    criteria = [
        'Laju Pertumbuhan Kumulatif (c-to-c)',
        'Laju Pertumbuhan Triwulanan Berantai (q-to-q)',
        'Laju Pertumbuhan Triwulanan terhadap Triwulan yang Sama Tahun Sebelumnya (y-on-y)',
        'Pengangguran',
        'Inflasi'
    ]
    
    ahp_weights = calculate_ahp_weights(ahp_matrix)
    weights = dict(zip(criteria, ahp_weights))
    
    criteria_types = {
        'Laju Pertumbuhan Kumulatif (c-to-c)': 'benefit',
        'Laju Pertumbuhan Triwulanan Berantai (q-to-q)': 'benefit',
        'Laju Pertumbuhan Triwulanan terhadap Triwulan yang Sama Tahun Sebelumnya (y-on-y)': 'benefit',
        'Pengangguran': 'cost',
        'Inflasi': 'benefit'
    }
    
    try:
        alternatives = data.set_index('alternatif')
    except KeyError:
        flash('Format data salah. Pastikan ada kolom bernama "alternatif".', 'danger')
        return redirect(url_for('index'))
    
    normalized_alternatives = normalize_alternatives(alternatives, criteria, criteria_types)
    normalized_alternatives = calculate_wp_scores(normalized_alternatives, weights, criteria, criteria_types)

    CR = calculate_consistency_ratio(ahp_matrix, ahp_weights)
    if CR > 0.1:
        flash(f'Consistency Ratio (CR) = {CR:.2f} > 0.10. Matriks perbandingan tidak konsisten.', 'warning')
    else:
        flash(f'Consistency Ratio (CR) = {CR:.2f} <= 0.10. Matriks perbandingan konsisten.', 'success')
    
    ranked_alternatives = normalized_alternatives[['V']].sort_values(by='V', ascending=False).reset_index()
    ranked_alternatives['Rank'] = range(1, len(ranked_alternatives) + 1)
    ranked_alternatives.rename(columns={'alternatif': 'sector', 'V': 'score'}, inplace=True)
    
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("DELETE FROM results WHERE filename=%s AND user_id=%s", (filename, current_user.id))
        for _, row in ranked_alternatives.iterrows():
            cursor.execute("""
                INSERT INTO results (filename, sector, score, rank, user_id, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """, (filename, row['sector'], row['score'], row['Rank'], current_user.id))
        mysql.connection.commit()
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Terjadi kesalahan saat menyimpan hasil ke database: {str(e)}', 'danger')
    finally:
        cursor.close()

    results = ranked_alternatives.to_dict(orient='records')

    # Membuat Heatmap menggunakan Plotly
    heatmap = go.Heatmap(
        z=ahp_matrix.tolist(),  # Convert ndarray to list
        x=criteria,
        y=criteria,
        colorscale='Viridis',
        text=ahp_matrix.tolist(),
        texttemplate='%{text}',
        hoverinfo='text'
    )
    layout_heatmap = go.Layout(
        title='Matriks Perbandingan Berpasangan AHP',
        xaxis=dict(title='Kriteria'),
        yaxis=dict(title='Kriteria')
    )
    fig_heatmap = go.Figure(data=[heatmap], layout=layout_heatmap)
    heatmap_json = fig_heatmap.to_json()

    return render_template('results.html', results=results, heatmap_json=heatmap_json, filename=filename, weights=weights)

@app.route('/export/<string:export_format>')
@login_required
def export_data(export_format):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT sector, c_to_c_growth, q_to_q_growth, y_on_y_growth, unemployment, inflation FROM alternatives WHERE user_id = %s", (current_user.id,))
    data = cursor.fetchall()
    cursor.close()
    
    df = pd.DataFrame(data, columns=['alternatif', 'Laju Pertumbuhan Kumulatif (c-to-c)',
                                     'Laju Pertumbuhan Triwulanan Berantai (q-to-q)',
                                     'Laju Pertumbuhan Triwulanan terhadap Triwulan yang Sama Tahun Sebelumnya (y-on-y)',
                                     'Pengangguran', 'Inflasi'])
    
    if export_format == 'csv':
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        return send_file(io.BytesIO(output.getvalue().encode()), mimetype='text/csv', download_name='alternatives.csv', as_attachment=True)
    elif export_format in ['xls', 'xlsx']:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Alternatives')
        output.seek(0)
        return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', download_name='alternatives.xlsx', as_attachment=True)
    elif export_format == 'json':
        output = df.to_json(orient='records', indent=4)
        return send_file(io.BytesIO(output.encode()), mimetype='application/json', download_name='alternatives.json', as_attachment=True)
    else:
        flash('Format export tidak didukung.', 'danger')
        return redirect(url_for('alternatives_list'))

@app.route('/add_alternative', methods=['GET', 'POST'])
@login_required
def add_alternative():
    criteria = [
        'Laju Pertumbuhan Kumulatif (c-to-c)',
        'Laju Pertumbuhan Triwulanan Berantai (q-to-q)',
        'Laju Pertumbuhan Triwulanan terhadap Triwulan yang Sama Tahun Sebelumnya (y-on-y)',
        'Pengangguran',
        'Inflasi'
    ]
    
    if request.method == 'POST':
        sektor = request.form['sektor']
        c_to_c_growth = request.form['c_to_c_growth']
        q_to_q_growth = request.form['q_to_q_growth']
        y_on_y_growth = request.form['y_on_y_growth']
        unemployment = request.form['unemployment']
        inflation = request.form['inflasi']

        try:
            c_to_c_growth = float(c_to_c_growth)
            q_to_q_growth = float(q_to_q_growth)
            y_on_y_growth = float(y_on_y_growth)
            unemployment = float(unemployment)
            inflation = float(inflation)
        except ValueError:
            flash('Pastikan semua nilai kriteria adalah angka.', 'danger')
            return redirect(request.url)
        
        cursor = mysql.connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO alternatives (sector, c_to_c_growth, q_to_q_growth, y_on_y_growth, unemployment, inflation, user_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (sektor, c_to_c_growth, q_to_q_growth, y_on_y_growth, unemployment, inflation, current_user.id))
            mysql.connection.commit()
            flash('Alternatif berhasil ditambahkan dan disimpan.', 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Terjadi kesalahan saat menyimpan data ke database: {str(e)}', 'danger')
        finally:
            cursor.close()

        csv_path = os.path.join(app.config['UPLOAD_FOLDER'], 'data.csv')
        try:
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
            else:
                df = pd.DataFrame(columns=['alternatif', 'Laju Pertumbuhan Kumulatif (c-to-c)',
                                           'Laju Pertumbuhan Triwulanan Berantai (q-to-q)',
                                           'Laju Pertumbuhan Triwulanan terhadap Triwulan yang Sama Tahun Sebelumnya (y-on-y)',
                                           'Pengangguran', 'Inflasi', 'user_id'])
            
            new_entry = {
                'alternatif': sektor,
                'Laju Pertumbuhan Kumulatif (c-to-c)': c_to_c_growth,
                'Laju Pertumbuhan Triwulanan Berantai (q-to-q)': q_to_q_growth,
                'Laju Pertumbuhan Triwulanan terhadap Triwulan yang Sama Tahun Sebelumnya (y-on-y)': y_on_y_growth,
                'Pengangguran': unemployment,
                'Inflasi': inflation,
                'user_id': current_user.id
            }
            
            new_df = pd.DataFrame([new_entry])
            df = pd.concat([df, new_df], ignore_index=True)
            df.to_csv(csv_path, index=False)
        except Exception as e:
            flash(f'Terjadi kesalahan saat menyimpan data ke CSV: {str(e)}', 'warning')
        
        return redirect(url_for('alternatives_list'))
    
    return render_template('add_alternative.html', criteria=criteria)

@app.route('/alternatives')
@login_required
def alternatives_list():
    search = request.args.get('search', '').strip()
    filter_sector = request.args.get('filter_sector', '').strip()
    filter_c_to_c_min = request.args.get('filter_c_to_c_min', '').strip()
    filter_c_to_c_max = request.args.get('filter_c_to_c_max', '').strip()
    filter_inflation_min = request.args.get('filter_inflation_min', '').strip()
    filter_inflation_max = request.args.get('filter_inflation_max', '').strip()
    
    query = """
        SELECT id, sector, c_to_c_growth, q_to_q_growth, y_on_y_growth, unemployment, inflation 
        FROM alternatives 
        WHERE user_id = %s
    """
    params = [current_user.id]
    
    if search:
        query += " AND (sector LIKE %s OR id LIKE %s)"
        like_search = f"%{search}%"
        params.extend([like_search, like_search])
    
    if filter_sector:
        query += " AND sector = %s"
        params.append(filter_sector)
    
    if filter_c_to_c_min:
        try:
            c_to_c_min = float(filter_c_to_c_min)
            query += " AND c_to_c_growth >= %s"
            params.append(c_to_c_min)
        except ValueError:
            flash('Nilai minimum untuk Laju Pertumbuhan Kumulatif (c-to-c) harus berupa angka.', 'warning')
    
    if filter_c_to_c_max:
        try:
            c_to_c_max = float(filter_c_to_c_max)
            query += " AND c_to_c_growth <= %s"
            params.append(c_to_c_max)
        except ValueError:
            flash('Nilai maksimum untuk Laju Pertumbuhan Kumulatif (c-to-c) harus berupa angka.', 'warning')
    
    if filter_inflation_min:
        try:
            inflation_min = float(filter_inflation_min)
            query += " AND inflation >= %s"
            params.append(inflation_min)
        except ValueError:
            flash('Nilai minimum untuk Inflasi harus berupa angka.', 'warning')
    
    if filter_inflation_max:
        try:
            inflation_max = float(filter_inflation_max)
            query += " AND inflation <= %s"
            params.append(inflation_max)
        except ValueError:
            flash('Nilai maksimum untuk Inflasi harus berupa angka.', 'warning')
    
    query += " ORDER BY id DESC"
    
    cursor = mysql.connection.cursor()
    cursor.execute(query, tuple(params))
    alternatives = cursor.fetchall()
    cursor.close()
    
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT DISTINCT sector FROM alternatives WHERE user_id = %s", (current_user.id,))
    sectors = cursor.fetchall()
    cursor.close()
    sector_list = [sector[0] for sector in sectors]
    
    return render_template('alternatives_list.html', alternatives=alternatives, 
                           search=search, filter_sector=filter_sector,
                           filter_c_to_c_min=filter_c_to_c_min, filter_c_to_c_max=filter_c_to_c_max,
                           filter_inflation_min=filter_inflation_min, filter_inflation_max=filter_inflation_max,
                           sector_list=sector_list)

@app.route('/edit_alternative/<int:alt_id>', methods=['GET', 'POST'])
@login_required
def edit_alternative(alt_id):
    cursor = mysql.connection.cursor()
    criteria = [
        'Laju Pertumbuhan Kumulatif (c-to-c)',
        'Laju Pertumbuhan Triwulanan Berantai (q-to-q)',
        'Laju Pertumbuhan Triwulanan terhadap Triwulan yang Sama Tahun Sebelumnya (y-on-y)',
        'Pengangguran',
        'Inflasi'
    ]
    
    if request.method == 'POST':
        sektor = request.form['sektor']
        c_to_c_growth = request.form['c_to_c_growth']
        q_to_q_growth = request.form['q_to_q_growth']
        y_on_y_growth = request.form['y_on_y_growth']
        unemployment = request.form['unemployment']
        inflation = request.form['inflasi']
        
        try:
            c_to_c_growth = float(c_to_c_growth)
            q_to_q_growth = float(q_to_q_growth)
            y_on_y_growth = float(y_on_y_growth)
            unemployment = float(unemployment)
            inflation = float(inflation)
        except ValueError:
            flash('Pastikan semua nilai kriteria adalah angka.', 'danger')
            return redirect(request.url)
        
        try:
            cursor.execute("""
                UPDATE alternatives
                SET sector=%s, c_to_c_growth=%s, q_to_q_growth=%s, y_on_y_growth=%s, unemployment=%s, inflation=%s
                WHERE id=%s AND user_id=%s
            """, (sektor, c_to_c_growth, q_to_q_growth, y_on_y_growth, unemployment, inflation, alt_id, current_user.id))
            mysql.connection.commit()
            flash('Alternatif berhasil diperbarui.', 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Terjadi kesalahan saat memperbarui data: {str(e)}', 'danger')
        finally:
            cursor.close()

        csv_path = os.path.join(app.config['UPLOAD_FOLDER'], 'data.csv')
        try:
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                mask = (df['alternatif'] == sektor) & (df['user_id'] == current_user.id)
                df.loc[mask, 'Laju Pertumbuhan Kumulatif (c-to-c)'] = c_to_c_growth
                df.loc[mask, 'Laju Pertumbuhan Triwulanan Berantai (q-to-q)'] = q_to_q_growth
                df.loc[mask, 'Laju Pertumbuhan Triwulanan terhadap Triwulan yang Sama Tahun Sebelumnya (y-on-y)'] = y_on_y_growth
                df.loc[mask, 'Pengangguran'] = unemployment
                df.loc[mask, 'Inflasi'] = inflation
                df.to_csv(csv_path, index=False)
        except Exception as e:
            flash(f'Terjadi kesalahan saat memperbarui data di CSV: {str(e)}', 'warning')
        
        return redirect(url_for('alternatives_list'))
    
    cursor.execute("SELECT id, sector, c_to_c_growth, q_to_q_growth, y_on_y_growth, unemployment, inflation FROM alternatives WHERE id=%s AND user_id=%s", (alt_id, current_user.id))
    alt = cursor.fetchone()
    cursor.close()
    if not alt:
        flash('Alternatif tidak ditemukan.', 'danger')
        return redirect(url_for('alternatives_list'))
    
    return render_template('edit_alternative.html', alt=alt, criteria=criteria)

@app.route('/delete_alternative/<int:alt_id>', methods=['GET'])
@login_required
def delete_alternative(alt_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT sector FROM alternatives WHERE id=%s AND user_id=%s", (alt_id, current_user.id))
    sektor = cursor.fetchone()
    if not sektor:
        flash('Alternatif tidak ditemukan.', 'danger')
        cursor.close()
        return redirect(url_for('alternatives_list'))
    
    try:
        cursor.execute("DELETE FROM alternatives WHERE id=%s AND user_id=%s", (alt_id, current_user.id))
        mysql.connection.commit()
        flash('Alternatif berhasil dihapus.', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Terjadi kesalahan saat menghapus alternatif: {str(e)}', 'danger')
    finally:
        cursor.close()
    
    csv_path = os.path.join(app.config['UPLOAD_FOLDER'], 'data.csv')
    try:
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            df = df[(df['alternatif'] != sektor[0]) | (df['user_id'] != current_user.id)]
            df.to_csv(csv_path, index=False)
    except Exception as e:
        flash(f'Terjadi kesalahan saat menghapus data di CSV: {str(e)}', 'warning')
    
    return redirect(url_for('alternatives_list'))

@app.route('/delete_all_alternatives', methods=['POST'])
@login_required
def delete_all_alternatives():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM alternatives WHERE user_id=%s", (current_user.id,))
        cursor.execute("DELETE FROM results WHERE user_id=%s", (current_user.id,))
        mysql.connection.commit()
        cursor.close()

        csv_path = os.path.join(app.config['UPLOAD_FOLDER'], 'data.csv')
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            df = df[df['user_id'] != current_user.id]
            df.to_csv(csv_path, index=False)

        flash('Semua alternatif berhasil dihapus.', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Terjadi kesalahan saat menghapus semua alternatif: {str(e)}', 'danger')
    finally:
        cursor.close()
    
    return redirect(url_for('alternatives_list'))

@app.route('/latest_results')
@login_required
def latest_results():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT filename FROM results
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT 1
    """, (current_user.id,))
    result = cursor.fetchone()
    cursor.close()
    if result:
        return redirect(url_for('results', filename=result[0]))
    else:
        flash('Belum ada hasil perangkingan. Silakan upload data terlebih dahulu.', 'info')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
