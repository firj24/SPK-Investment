from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import pandas as pd
import numpy as np
import os
from werkzeug.utils import secure_filename
from flask_mysqldb import MySQL
import pymysql
import plotly.express as px  # Pastikan baris ini ada
import plotly
import plotly.graph_objs as go
import json
import io

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Gantilah dengan kunci rahasia Anda

# Konfigurasi MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Ganti sesuai dengan user yang dibuat
app.config['MYSQL_PASSWORD'] = ''  # Ganti sesuai dengan password yang dibuat
app.config['MYSQL_DB'] = 'investment_db'

# Inisialisasi MySQL
mysql = MySQL(app)

# Konfigurasi Upload Folder
UPLOAD_FOLDER = 'data'
ALLOWED_EXTENSIONS = {'csv', 'xls', 'xlsx', 'json'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Fungsi untuk normalisasi matriks AHP
def normalize_matrix(matrix):
    column_sums = np.sum(matrix, axis=0)
    normalized = matrix / column_sums
    return normalized

# Fungsi untuk menghitung bobot AHP
def calculate_ahp_weights(ahp_matrix):
    normalized = normalize_matrix(ahp_matrix)
    weights = np.mean(normalized, axis=1)
    weights = weights / np.sum(weights)
    return weights

# Fungsi untuk normalisasi alternatif
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
            # Menghindari pembagian dengan nol
            normalized[crit] = alternatives[crit].apply(lambda x: min_val / x if x != 0 else 0)
    return normalized

# Fungsi untuk menghitung skor WP
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

# Fungsi untuk menghitung Consistency Ratio
def calculate_consistency_ratio(ahp_matrix, weights):
    n = ahp_matrix.shape[0]
    weighted_sum = np.dot(ahp_matrix, weights)
    lambda_max = np.mean(weighted_sum / weights)
    CI = (lambda_max - n) / (n - 1)
    RI_dict = {1:0, 2:0, 3:0.58, 4:0.90, 5:1.12, 6:1.24, 7:1.32, 8:1.41, 9:1.45}
    RI = RI_dict.get(n, 1.49)  # RI untuk n > 10 adalah 1.49
    CR = CI / RI
    return CR

# Route Index untuk Upload File (CSV, Excel, JSON)
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Menangani file upload
        if 'file' not in request.files:
            flash('Tidak ada file yang diunggah')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('Tidak ada file yang dipilih')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            # Tentukan format file berdasarkan ekstensi
            file_ext = filename.rsplit('.', 1)[1].lower()
            try:
                if file_ext == 'csv':
                    data = pd.read_csv(filepath)
                elif file_ext in ['xls', 'xlsx']:
                    data = pd.read_excel(filepath)
                elif file_ext == 'json':
                    data = pd.read_json(filepath)
                else:
                    flash('Format file tidak didukung')
                    return redirect(request.url)
            except Exception as e:
                flash(f'Terjadi kesalahan saat membaca file: {str(e)}')
                return redirect(request.url)
            
            # Validasi kolom yang diperlukan
            required_columns = ['alternatif', 'Laju Pertumbuhan Kumulatif (c-to-c)',
                                'Laju Pertumbuhan Triwulanan Berantai (q-to-q)',
                                'Laju Pertumbuhan Triwulanan terhadap Triwulan yang Sama Tahun Sebelumnya (y-on-y)',
                                'Pengangguran', 'Inflasi']
            if not all(col in data.columns for col in required_columns):
                flash('Format file salah. Pastikan semua kolom yang diperlukan ada.')
                return redirect(request.url)
            
            # Simpan data ke database
            cursor = mysql.connection.cursor()
            try:
                for _, row in data.iterrows():
                    cursor.execute("""
                        INSERT INTO alternatives (sector, c_to_c_growth, q_to_q_growth, y_on_y_growth, unemployment, inflation)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (row['alternatif'], row['Laju Pertumbuhan Kumulatif (c-to-c)'],
                          row['Laju Pertumbuhan Triwulanan Berantai (q-to-q)'],
                          row['Laju Pertumbuhan Triwulanan terhadap Triwulan yang Sama Tahun Sebelumnya (y-on-y)'],
                          row['Pengangguran'], row['Inflasi']))
                mysql.connection.commit()
                flash('Data berhasil di-upload dan disimpan.')
            except Exception as e:
                mysql.connection.rollback()
                flash(f'Terjadi kesalahan saat menyimpan data ke database: {str(e)}')
            finally:
                cursor.close()
            
            # Update CSV (opsional)
            try:
                df = data.copy()
                df.to_csv(os.path.join(app.config['UPLOAD_FOLDER'], 'data.csv'), index=False)
            except Exception as e:
                flash(f'Terjadi kesalahan saat menyimpan data ke CSV: {str(e)}')
            
            # Redirect ke halaman hasil
            return redirect(url_for('results', filename=filename))
        else:
            flash('Tipe file yang diizinkan: CSV, Excel (.xls, .xlsx), JSON')
            return redirect(request.url)
    return render_template('index.html')


# Route untuk Menampilkan Hasil
@app.route('/results/<filename>')
def results(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        flash('File tidak ditemukan')
        return redirect(url_for('index'))
    
    # Membaca dataset dari file yang di-upload
    try:
        file_ext = filename.rsplit('.', 1)[1].lower()
        if file_ext == 'csv':
            data = pd.read_csv(filepath)
        elif file_ext in ['xls', 'xlsx']:
            data = pd.read_excel(filepath)
        elif file_ext == 'json':
            data = pd.read_json(filepath)
        else:
            flash('Format file tidak didukung untuk analisis.')
            return redirect(url_for('index'))
    except Exception as e:
        flash('Terjadi kesalahan saat membaca file.')
        return redirect(url_for('index'))
    
    # Definisikan matriks perbandingan berpasangan AHP
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
    
    # Hitung bobot AHP
    ahp_weights = calculate_ahp_weights(ahp_matrix)
    weights = dict(zip(criteria, ahp_weights))
    
    # Definisikan jenis kriteria
    criteria_types = {
        'Laju Pertumbuhan Kumulatif (c-to-c)': 'benefit',
        'Laju Pertumbuhan Triwulanan Berantai (q-to-q)': 'benefit',
        'Laju Pertumbuhan Triwulanan terhadap Triwulan yang Sama Tahun Sebelumnya (y-on-y)': 'benefit',
        'Pengangguran': 'cost',
        'Inflasi': 'benefit'
    }
    
    # Menyiapkan data alternatif
    try:
        alternatives = data.set_index('alternatif')
    except KeyError:
        flash('Format data salah. Pastikan ada kolom bernama "alternatif".')
        return redirect(url_for('index'))
    
    # Normalisasi alternatif
    normalized_alternatives = normalize_alternatives(alternatives, criteria, criteria_types)
    
    # Hitung skor WP
    normalized_alternatives = calculate_wp_scores(normalized_alternatives, weights, criteria, criteria_types)
    
    # Hitung Consistency Ratio (CR)
    CR = calculate_consistency_ratio(ahp_matrix, ahp_weights)
    if CR > 0.1:
        flash(f'Consistency Ratio (CR) = {CR:.2f} > 0.10. Matriks perbandingan tidak konsisten.')
    else:
        flash(f'Consistency Ratio (CR) = {CR:.2f} <= 0.10. Matriks perbandingan konsisten.')
    
    # Mengurutkan alternatif berdasarkan skor V
    ranked_alternatives = normalized_alternatives[['V']].sort_values(by='V', ascending=False).reset_index()
    ranked_alternatives['Rank'] = range(1, len(ranked_alternatives) + 1)
    
    # Rename columns untuk konsistensi dengan frontend
    ranked_alternatives.rename(columns={'alternatif': 'sector', 'V': 'score'}, inplace=True)
    
    # Menyimpan hasil ke database
    cursor = mysql.connection.cursor()
    # Hapus hasil sebelumnya untuk file ini
    cursor.execute("DELETE FROM results WHERE filename=%s", (filename,))
    for _, row in ranked_alternatives.iterrows():
        cursor.execute("""
            INSERT INTO results (filename, sector, score, rank)
            VALUES (%s, %s, %s, %s)
        """, (filename, row['sector'], row['score'], row['Rank']))
    mysql.connection.commit()
    cursor.close()
    
    # Mengubah hasil menjadi dictionary untuk ditampilkan di template
    # Mengubah hasil menjadi dictionary untuk ditampilkan di template
    results = ranked_alternatives.to_dict(orient='records')

    # Menyimpan hasil ke database
    cursor = mysql.connection.cursor()
    # Hapus hasil sebelumnya untuk file ini
    cursor.execute("DELETE FROM results WHERE filename=%s", (filename,))
    for _, row in ranked_alternatives.iterrows():
        cursor.execute("""
            INSERT INTO results (filename, sector, score, rank)
            VALUES (%s, %s, %s, %s)
        """, (filename, row['sector'], row['score'], row['Rank']))
    mysql.connection.commit()
    cursor.close()

    # Mengubah hasil menjadi dictionary untuk ditampilkan di template
    results = ranked_alternatives.to_dict(orient='records')

    # Membuat Heatmap untuk Matriks AHP dengan Plotly
    heatmap = go.Heatmap(
        z=ahp_matrix,
        x=criteria,
        y=criteria,
        colorscale='Viridis',
        text=ahp_matrix,  # Menambahkan teks pada setiap sel
        texttemplate='%{text}',
        hoverinfo='text'
    )

    layout_heatmap = go.Layout(
        title='Matriks Perbandingan Berpasangan AHP',
        xaxis=dict(title='Kriteria'),
        yaxis=dict(title='Kriteria')
    )

    fig_heatmap = go.Figure(data=[heatmap], layout=layout_heatmap)
    heatmapJSON = json.dumps(fig_heatmap, cls=plotly.utils.PlotlyJSONEncoder)

    # Tambahkan 'weights' ke dalam context render_template
    return render_template('results.html', results=results, heatmapJSON=heatmapJSON, filename=filename, weights=weights)


# Route Export Data
@app.route('/export/<string:export_format>')
def export_data(export_format):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT sector, c_to_c_growth, q_to_q_growth, y_on_y_growth, unemployment, inflation FROM alternatives")
    data = cursor.fetchall()
    cursor.close()
    
    # Convert data ke DataFrame
    df = pd.DataFrame(data, columns=['alternatif', 'Laju Pertumbuhan Kumulatif (c-to-c)',
                                     'Laju Pertumbuhan Triwulanan Berantai (q-to-q)',
                                     'Laju Pertumbuhan Triwulanan terhadap Triwulan yang Sama Tahun Sebelumnya (y-on-y)',
                                     'Pengangguran', 'Inflasi'])
    
    # Ekspor berdasarkan format
    if export_format == 'csv':
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype='text/csv',
            download_name='alternatives.csv',
            as_attachment=True
        )
    elif export_format in ['xls', 'xlsx']:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Alternatives')
        output.seek(0)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            download_name='alternatives.xlsx',
            as_attachment=True
        )
    elif export_format == 'json':
        output = df.to_json(orient='records', indent=4)
        return send_file(
            io.BytesIO(output.encode()),
            mimetype='application/json',
            download_name='alternatives.json',
            as_attachment=True
        )
    else:
        flash('Format export tidak didukung.')
        return redirect(url_for('alternatives_list'))

# Route untuk Menambah Alternatif Baru
@app.route('/add_alternative', methods=['GET', 'POST'])
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
        inflation = request.form['inflasi']  # Pastikan konsistensi nama field
        
        # Validasi input (opsional)
        try:
            c_to_c_growth = float(c_to_c_growth)
            q_to_q_growth = float(q_to_q_growth)
            y_on_y_growth = float(y_on_y_growth)
            unemployment = float(unemployment)
            inflation = float(inflation)
        except ValueError:
            flash('Pastikan semua nilai kriteria adalah angka.')
            return redirect(request.url)
        
        # Simpan ke database
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO alternatives (sector, c_to_c_growth, q_to_q_growth, y_on_y_growth, unemployment, inflation)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (sektor, c_to_c_growth, q_to_q_growth, y_on_y_growth, unemployment, inflation))
        mysql.connection.commit()
        cursor.close()
        
        # Update CSV (atau format lain jika diperlukan)
        csv_path = os.path.join(app.config['UPLOAD_FOLDER'], 'data.csv')
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
        else:
            df = pd.DataFrame(columns=['alternatif', 'Laju Pertumbuhan Kumulatif (c-to-c)',
                                       'Laju Pertumbuhan Triwulanan Berantai (q-to-q)',
                                       'Laju Pertumbuhan Triwulanan terhadap Triwulan yang Sama Tahun Sebelumnya (y-on-y)',
                                       'Pengangguran', 'Inflasi'])
        
        new_entry = {
            'alternatif': sektor,
            'Laju Pertumbuhan Kumulatif (c-to-c)': c_to_c_growth,
            'Laju Pertumbuhan Triwulanan Berantai (q-to-q)': q_to_q_growth,
            'Laju Pertumbuhan Triwulanan terhadap Triwulan yang Sama Tahun Sebelumnya (y-on-y)': y_on_y_growth,
            'Pengangguran': unemployment,
            'Inflasi': inflation
        }
        
        # Menggunakan pd.concat sebagai pengganti append
        new_df = pd.DataFrame([new_entry])
        df = pd.concat([df, new_df], ignore_index=True)
        df.to_csv(csv_path, index=False)
        
        flash('Alternatif berhasil ditambahkan dan diperbarui.')
        return redirect(url_for('alternatives_list'))
    
    return render_template('add_alternative.html', criteria=criteria)

# Route untuk Menampilkan Daftar Alternatif
@app.route('/alternatives')
def alternatives_list():
    filename = request.args.get('filename')  # Mengambil parameter filename dari query string
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM alternatives")
    alternatives = cursor.fetchall()
    cursor.close()
    return render_template('alternatives_list.html', alternatives=alternatives, filename=filename)


# Route untuk Mengedit Alternatif
@app.route('/edit_alternative/<int:alt_id>', methods=['GET', 'POST'])
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
        inflation = request.form['inflasi']  # Pastikan konsistensi nama field
        
        # Validasi input (opsional)
        try:
            c_to_c_growth = float(c_to_c_growth)
            q_to_q_growth = float(q_to_q_growth)
            y_on_y_growth = float(y_on_y_growth)
            unemployment = float(unemployment)
            inflation = float(inflation)
        except ValueError:
            flash('Pastikan semua nilai kriteria adalah angka.')
            return redirect(request.url)
        
        # Update database
        cursor.execute("""
            UPDATE alternatives
            SET sector=%s, c_to_c_growth=%s, q_to_q_growth=%s, y_on_y_growth=%s, unemployment=%s, inflation=%s
            WHERE id=%s
        """, (sektor, c_to_c_growth, q_to_q_growth, y_on_y_growth, unemployment, inflation, alt_id))
        mysql.connection.commit()
        
        # Update CSV (atau format lain jika diperlukan)
        csv_path = os.path.join(app.config['UPLOAD_FOLDER'], 'data.csv')
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            # Cari baris yang cocok berdasarkan 'alternatif'
            df.loc[df['alternatif'] == sektor, 'Laju Pertumbuhan Kumulatif (c-to-c)'] = c_to_c_growth
            df.loc[df['alternatif'] == sektor, 'Laju Pertumbuhan Triwulanan Berantai (q-to-q)'] = q_to_q_growth
            df.loc[df['alternatif'] == sektor, 'Laju Pertumbuhan Triwulanan terhadap Triwulan yang Sama Tahun Sebelumnya (y-on-y)'] = y_on_y_growth
            df.loc[df['alternatif'] == sektor, 'Pengangguran'] = unemployment
            df.loc[df['alternatif'] == sektor, 'Inflasi'] = inflation
            df.to_csv(csv_path, index=False)
        
        cursor.close()
        flash('Alternatif berhasil diperbarui.')
        return redirect(url_for('alternatives_list'))
    
    # GET request: ambil data alternatif
    cursor.execute("SELECT * FROM alternatives WHERE id=%s", (alt_id,))
    alt = cursor.fetchone()
    cursor.close()
    if not alt:
        flash('Alternatif tidak ditemukan.')
        return redirect(url_for('alternatives_list'))
    
    return render_template('edit_alternative.html', alt=alt, criteria=criteria)

# Route untuk Menghapus Alternatif
@app.route('/delete_alternative/<int:alt_id>', methods=['GET'])
def delete_alternative(alt_id):
    cursor = mysql.connection.cursor()
    # Dapatkan nama sektor sebelum dihapus
    cursor.execute("SELECT sector FROM alternatives WHERE id=%s", (alt_id,))
    sektor = cursor.fetchone()
    if not sektor:
        flash('Alternatif tidak ditemukan.')
        cursor.close()
        return redirect(url_for('alternatives_list'))
    
    # Hapus dari database
    cursor.execute("DELETE FROM alternatives WHERE id=%s", (alt_id,))
    mysql.connection.commit()
    cursor.close()
    
    # Hapus dari CSV (atau format lain jika diperlukan)
    csv_path = os.path.join(app.config['UPLOAD_FOLDER'], 'data.csv')
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df = df[df['alternatif'] != sektor[0]]
        df.to_csv(csv_path, index=False)
    
    flash('Alternatif berhasil dihapus.')
    return redirect(url_for('alternatives_list'))
    
@app.route('/delete_all_alternatives', methods=['POST'])
def delete_all_alternatives():
    try:
        cursor = mysql.connection.cursor()
        # Hapus semua data dari tabel 'alternatives'
        cursor.execute("DELETE FROM alternatives")
        mysql.connection.commit()
        cursor.close()

        # Hapus data.csv jika ada
        csv_path = os.path.join(app.config['UPLOAD_FOLDER'], 'data.csv')
        if os.path.exists(csv_path):
            os.remove(csv_path)

        flash('Semua alternatif berhasil dihapus.')
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Terjadi kesalahan saat menghapus semua alternatif: {str(e)}')
    finally:
        cursor.close()
    
    return redirect(url_for('alternatives_list'))
if __name__ == '__main__':
    app.run(debug=True)
