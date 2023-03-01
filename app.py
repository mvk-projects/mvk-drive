import os
from functools import wraps

from flask import Flask, request, render_template, redirect, make_response
from mega import Mega

app = Flask(__name__)

mega = Mega()

email = ""
password = ""


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if auth:
            return f(*args, **kwargs)
        return make_response('Could not verify login!!', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

    return decorated


@app.route('/')
@auth_required
def index():
    try:
        m = mega.login(request.authorization.username, request.authorization.password)
    except:
        return render_template("errorAuth.html")
    m.empty_trash()
    files = m.get_files()
    list_files = ""
    for x in files:
        if files[x]['t'] == 0:
            list_files += ((files[x]['a']['n']) + "$")
    return render_template("main.html", list_files=list_files)


@app.route('/manage', methods=['POST'])
def manage():
    try:
        m = mega.login(request.authorization.username, request.authorization.password)
    except:
        return render_template("errorAuth.html")
    if request.method == 'POST':
        filename = request.form.get("input", None)
        if filename.endswith("$$$del"):
            original_file_name = filename.replace("$$$del", "")
            file_exits = m.find(original_file_name)
            if file_exits is None:
                return render_template("error.html")
            link = m.get_link(m.find(original_file_name))
            m.delete_url(link)
            return redirect("/", code=302)
        else:
            file_exits = m.find(filename)
            if file_exits is None:
                return render_template("error.html")
            return redirect(m.get_link(file_exits), code=302)


@app.route('/upload', methods=['POST'])
def main():
    return render_template("manage.html")


@app.route('/uploader', methods=['POST'])
def upload_file():
    try:
        m = mega.login(request.authorization.username, request.authorization.password)
    except:
        return render_template("errorAuth.html")
    if request.method == 'POST':
        files = request.files.getlist("file")
        failedUploadList = []
        for file in files:
            get_files = m.get_files()
            list_files = []
            for x in get_files:
                if get_files[x]['t'] == 0:
                    list_files.append(get_files[x]['a']['n'])
            if list_files.count(file.filename) > 0:
                failedUploadList.append(file.filename)
                continue
            file.save(file.filename)
            path = os.path.abspath(file.filename)
            m.upload(path)
            os.remove(path)
    return render_template("success.html", failedUploadList=(",".join(failedUploadList)))


if __name__ == '__main__':
    app.run()
