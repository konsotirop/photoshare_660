# TODO: (ben) MERGE
@app.route('/top_users', methods=['GET'])
def top_users():
    cursor = conn.cursor()

    query = 'SELECT uid, SUM(cnt) FROM ( ' \
                'SELECT uid, COUNT(*) AS photo_freq(uid, cnt) FROM PHOTO GROUP BY uid' \
                'UNION ALL ' \
                'SELECT uid, COUNT(*) AS comment_freq(uid, cnt) FROM COMMENT GROUP BY uid)' \
            'GROUP BY uid' \
            'LIMIT 10'
    cursor.execute(query)
    # will return list of (uid, score) tuples
    data = cursor.fetchall()

    # TODO: (ben) need to return an HTML template that takes data as parameter


# TODO: (ben) MERGE
@app.route('/all_photos', methods=['GET'])
def browse_photos():
    query = 'SELECT img_data FROM PHOTO'

    cursor.execute(query)

    data = cursor.fetchall()

    # TODO: (ben) need to return HTML template that takes data as parameter
    # TODO: (ben) could add functionality to order by number of likes