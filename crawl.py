import os
import hashlib
import sqlite3
from datetime import datetime
import deepdanbooru
from deepdanbooru.commands import evaluate_image
import traceback
from tensorflow.python.framework.errors_impl import InvalidArgumentError
from tqdm import tqdm

def get_image_tagscore(image_path):
    result = evaluate_image(image_path, MODEL, TAGS, 0.1)
    results = dict()
    for tag, score in result:
        results[tag] = score
    return results


def get_sha256(file_path):
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


def setup_database(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY,
            filename TEXT,
            directory TEXT,
            sha256_digest TEXT UNIQUE,
            capture_time TEXT
        )
    ;""")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tagscores (
            id INTEGER PRIMARY KEY,
            image_id INTEGER,
            tag TEXT,
            score REAL,
            FOREIGN KEY (image_id) REFERENCES images (id),
            UNIQUE (image_id, tag)
        )
    ;""")
    conn.commit()
    return conn


def process_images(directory, conn, cursor):
    completed_file_path = set()

    for root, _, files in os.walk(directory):
        for file in tqdm(files):
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                file_path = os.path.join(root, file)

                if VERBOSE: print(f'File, {file_path}')

                if file_path in completed_file_path:
                    continue

                sha256_digest = get_sha256(file_path)

                capture_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                params = (file, root, sha256_digest, capture_time)

                cursor.execute("""
                    INSERT INTO images (filename, directory, sha256_digest, capture_time)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(sha256_digest) DO UPDATE SET filename=excluded.filename, directory=excluded.directory, capture_time=excluded.capture_time
                ;""", params)

                image_id = cursor.execute('SELECT id FROM images WHERE sha256_digest=?;', (sha256_digest,)).fetchone()[0]

                try:
                    tagscore = get_image_tagscore(file_path)
                except InvalidArgumentError:
                    continue

                for tag, score in tagscore.items():
                    cursor.execute("""
                        INSERT INTO tagscores (image_id, tag, score)
                        VALUES (?, ?, ?)
                        ON CONFLICT(image_id, tag) DO UPDATE SET score=excluded.score
                    ;""", (image_id, tag, round(float(score), 5)))

                conn.commit()
                if VERBOSE: print(f"Committed")



if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))

    PROJECT_PATH = '/media/scripts/deepdanbooru/db_released_project'
    MODEL = deepdanbooru.project.load_model_from_project(PROJECT_PATH, compile_model=False)
    TAGS = deepdanbooru.project.load_tags_from_project(PROJECT_PATH)

    VERBOSE = False

    target_directory = '/path/to/images'
    database_file = 'crawl.db'

    conn = setup_database(database_file)
    cursor = conn.cursor()
    try:
        process_images(target_directory, conn, cursor)
    except Exception as e:
        print(f'{traceback.format_exception(e)}')
    finally:
        cursor.close()
        conn.close()
