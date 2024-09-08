DeepDanBooru Scripts

- `crawl.py` - this goes through an images directory and generates tags and scores for each image it finds. The results are stored in a sqlite db.
- `display` - generates an web page displaying images, tags, and scores
- `web.py` - a web UI for uploading a single image which returns tags and scores for it. Taken from https://github.com/KichangKim/DeepDanbooru/issues/94#issuecomment-1557571288.

Set Up

Make an venv, install `requirements.txt` and `requirements_ddb.txt`. Go through the script you want to run and configure the paths. You should have DDB downloaded so you can point to its `db_released_project` directory that contains DDB configs and the special `model-resnet_custom_v3.h5` model.
