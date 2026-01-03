#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import os
import secrets
import subprocess
import threading
import time

import cv2
import dotenv
from flask import Flask, redirect, render_template, request, send_from_directory
from flask_wtf import CSRFProtect, FlaskForm

# from telegram import Update
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired

# from bot import create_dispatcher, register_handlers
# from highlighter import get_languages  # make_image, get_languages
# from logic import get_random_bg
# from uploader import gen_name_uniq, UPLOAD_DIR


IMAGE_DIR = "data_images"
TEXT_DIR = "data_text"


dotenv.load_dotenv()


video = cv2.VideoCapture(1)
if not video.isOpened():
    print("Error: Could not open video source.")
    exit()


class _videocache:
    frame = None


def camera_thread():
    while True:
        ret, frame = video.read()
        if ret:
            _videocache.frame = frame
        time.sleep(0.0001)


threading.Thread(target=camera_thread).start()


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET")
# TG_TOKEN = os.environ.get("TG_TOKEN")
csrf = CSRFProtect(app)

# bot, queue, dp = create_dispatcher(TG_TOKEN)
# register_handlers(dp)


class MyForm(FlaskForm):
    language = StringField("language")
    code = TextAreaField("code", validators=[DataRequired()])


@app.route("/")
def hello_world():
    return render_template("input.html", languages=[])  # get_languages())


@app.route("/upload/<path:filename>")
def image(filename):
    return send_from_directory(
        "data_images", filename, as_attachment=("download" in request.args)
    )


# @app.route("/code", methods=["POST"])
# def render_code():
#     form = MyForm()
#     if not form.validate():
#         return redirect("/")
#     name = gen_name_uniq(5)
#     path = os.path.join(UPLOAD_DIR, name + ".jpg")
#     make_image(form.code.data, path, form.language.data, background=get_random_bg())
#     # upload(path, name, nickname)
#     return redirect("/i/" + name)


@app.route("/code", methods=["POST"])
def render_code_new():
    form = MyForm()
    if not form.validate():
        return redirect("/")

    name = secrets.token_hex(32)
    txt_path = os.path.join(TEXT_DIR, name + ".txt")
    print(f"writing {txt_path}")
    with open(txt_path, "w") as fp:
        fp.write(form.code.data)

    print(f"opening {txt_path} with gedit")
    proc = subprocess.Popen(["gedit", txt_path])
    time.sleep(2)

    print("taking picture")
    # ret, frame = video.read()
    frame = _videocache.frame

    jpg_path = os.path.join(IMAGE_DIR, name + ".jpg")
    print(f"writing {jpg_path}")
    cv2.imwrite(jpg_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 90])

    print("killing gedit")
    proc.kill()

    print("success!")
    return redirect(f"/i/{name}")


@app.route("/i/<path:filename>")
def custom_static(filename):
    path = os.path.join(IMAGE_DIR, filename + ".jpg")
    diff = os.path.relpath(path, IMAGE_DIR)
    if diff != filename + ".jpg":
        return "nice try", 404
    if os.path.exists(path):
        return render_template("image.html", image=filename)
    else:
        return render_template("not_found.html"), 404


# @app.route('/hook/' + TG_TOKEN, methods=['POST'])
# @csrf.exempt
# def tg_webhook():
#     logging.info("tg_webhook")
#     data = request.get_json(force=True)
#     logging.info(data)
#     update = Update.de_json(data, bot=bot)
#     dp.process_update(update)
#     return "OK"


# @app.route('/hook/' + TG_TOKEN, methods=['GET'])
# def webhook_get():
#     return redirect("https://telegram.me/links_forward_bot", code=302)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        app.run()
    finally:
        print(f"Shutting down. Closing cv2 resources.")
        video.release()
        cv2.destroyAllWindows()  # Closes all OpenCV windows
