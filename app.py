#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import atexit
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

from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired


IMAGE_DIR = "data_images"
TEXT_DIR = "data_text"


dotenv.load_dotenv()


VIDEO_SOURCE = int(os.getenv("VIDEO_SOURCE"))


video = cv2.VideoCapture(VIDEO_SOURCE)
if not video.isOpened():
    print("Error: Could not open video source.")
    exit()


class _videocache:
    frame = None
    run_thread = True
    cleanup_done = False
    last_frame = "no-uploads-yet"


def capture_camera():
    try:
        while _videocache.run_thread:
            ret, frame = video.read()
            if ret:
                _videocache.frame = frame
            time.sleep(0.0001)

    finally:
        print("Closing cv2 resources.")
        video.release()
        cv2.destroyAllWindows()  # Closes all OpenCV windows


camera_thread = threading.Thread(target=capture_camera)
camera_thread.start()

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


@app.route("/code", methods=["POST"])
def render_code_new():
    form = MyForm()
    if not form.validate():
        return redirect("/")

    name = secrets.token_urlsafe(8)
    txt_path = os.path.join(TEXT_DIR, name + ".txt")
    print(f"writing {txt_path}")
    with open(txt_path, "w") as fp:
        fp.write(form.code.data)

    print(f"opening {txt_path} with gedit")
    proc = subprocess.Popen(["gedit", txt_path])
    time.sleep(3)

    print("taking picture")
    # ret, frame = video.read()
    frame = _videocache.frame

    jpg_path = os.path.join(IMAGE_DIR, name + ".jpg")
    print(f"writing {jpg_path}")
    cv2.imwrite(jpg_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 90])

    print("killing gedit")
    proc.kill()

    _videocache.last_frame = name

    print("success!")
    return redirect(f"/i/{name}")


@app.route("/i/<path:filename>")
def custom_static(filename):
    if filename == "last":
        filename = _videocache.last_frame
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


def cleanup_tasks():
    if not _videocache.cleanup_done:
        print("Shutting down.")
        if camera_thread.is_alive():
            _videocache.run_thread = False
            camera_thread.join()
        print("Done.")
        _videocache.cleanup_done = True


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        app.run()
    finally:
        cleanup_tasks()
else:
    atexit.register(cleanup_tasks)
