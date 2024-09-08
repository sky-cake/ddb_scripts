from flask import Flask, render_template, g, send_file
import sqlite3
import os

# configs
os.chdir(os.path.dirname(__file__))
DATABASE = 'crawl.db'
images_path = '/path/to/images'
app = Flask(__name__)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = dict_factory
    return db


def dict_factory(cursor, row):
    d = {}
    for i, col in enumerate(cursor.description):
        d[col[0]] = row[i]
    return d


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


@app.route('/images/<path:filename>')
def serve_static(filename):
    file_path = os.path.join(images_path, filename)
    return send_file(file_path)


@app.route('/')
def index():
    sql_string = """
        SELECT images.id, filename
        FROM images
        LIMIT 50;
    """
    images = query_db(sql_string)

    placeholder = ','.join(['?'] * len(images))
    sql_string = f"""
        SELECT image_id, tag, score
        FROM tagscores
        WHERE image_id IN ({placeholder}) and score > 0.8
        ;
    """
    tagscores = query_db(sql_string, [image['id'] for image in images])

    for i, image in enumerate(images):
        images[i]['tagscores'] = [(tagscore['tag'], tagscore['score']) for tagscore in tagscores if tagscore['image_id'] == image['id']]

    print(images[0])
    return render_template('display.html', images_data=images)

if __name__ == '__main__':
    app.run(port=9000)
