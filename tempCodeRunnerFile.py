nked_alternatives = normalized_alternatives[['V']].sort_values(by='V', ascending=False).reset_index()
    ranked_alternatives['Rank'] = range(1, len(ranked_alternatives) + 1)

    # Menyimpan hasil ke database
    cursor = mysql.connection.cursor()
    # Hapus hasil sebelumnya untuk file ini
    cursor.execute("DELETE FROM results WHERE filename=%s", (filename,))
    for _, row in ranked_alternatives.iterrows():
        cursor.execute("""
            INSERT INTO results (filename, sector, score, rank)
            VALUES (%s, %s, %s, %s)
        """, (filename, row['alternatif'], row['V'], row['Rank']))
    mysql.connection.commit()
    cursor.close()

    # Mengubah hasil menjadi dictionary untuk ditampilkan di template
    results = ranked_alternatives.to_dict(orient='records')

    # Membuat Horizontal Bar Chart dengan Plotly Express
    fig_bar = px.bar(
        ranked_alternatives,
        x='V',
        y='alternatif',
        orientation='h',
        title='Peringkat Sektor Investasi Berdasarkan Score (V)',
        labels={'V': 'Score (V)', 'alternatif': 'Sektor'},
        text='V',
        height=600
    )

    # Menambahkan teks pada akhir setiap batang
    fig_bar.update_traces(texttemplate='%{text:.4f}', textposition='outside')

    # Menyesuaikan layout
    fig_bar.update_layout(
        yaxis=dict(autorange="reversed"),  # Membalikkan urutan agar rank 1 berada di atas
        xaxis=dict(title='Score (V)'),
        uniformtext_minsize=8,
        uniformtext_mode='hide'
    )

    barJSON = json.dumps(fig_bar, cls=plotly.utils.PlotlyJSONEncoder)

    return render_templ