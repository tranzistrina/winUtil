from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os, sqlite3
from datetime import datetime

app=Flask(__name__)
VIDEO_DIR='videos'; THUMB_DIR='thumbnails'; DB='database.db'
for d in (VIDEO_DIR,THUMB_DIR): os.makedirs(d,exist_ok=True)

def get_db():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c

def init_db():
    with get_db() as c:
        c.execute('CREATE TABLE IF NOT EXISTS videos (id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT UNIQUE, title TEXT, description TEXT, upload_date TEXT, views INTEGER DEFAULT 0)')
        c.execute('CREATE TABLE IF NOT EXISTS categories (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)')
        c.execute('CREATE TABLE IF NOT EXISTS video_category (video_id INTEGER, category_id INTEGER)')
init_db()

@app.route('/')
def index():
    with get_db() as c:
        videos=c.execute('SELECT * FROM videos ORDER BY upload_date DESC').fetchall(); categories=c.execute('SELECT * FROM categories ORDER BY name').fetchall()
    return render_template('index.html',videos=videos,categories=categories)

@app.route('/upload',methods=['GET','POST'])
def upload():
    if request.method=='POST' and request.files.get('file'):
        f=request.files['file']; filename=os.path.basename(f.filename); f.save(os.path.join(VIDEO_DIR,filename))
        with get_db() as c: c.execute('INSERT OR REPLACE INTO videos(filename,title,description,upload_date) VALUES(?,?,?,?)',(filename,request.form.get('title') or filename,request.form.get('description',''),datetime.utcnow().isoformat()))
        return redirect(url_for('index'))
    with get_db() as c: categories=c.execute('SELECT * FROM categories').fetchall()
    return render_template('upload.html',categories=categories)

@app.route('/video/<int:video_id>')
def video(video_id):
    with get_db() as c:
        c.execute('UPDATE videos SET views=views+1 WHERE id=?',(video_id,)); row=c.execute('SELECT * FROM videos WHERE id=?',(video_id,)).fetchone()
    if not row:return 'Not found',404
    return render_template('video.html',video=row)

@app.route('/category',methods=['POST'])
def category():
    name=request.form.get('name','').strip()
    if name:
        with get_db() as c: c.execute('INSERT OR IGNORE INTO categories(name) VALUES(?)',(name,))
    return redirect(url_for('index'))

@app.route('/videos/<path:filename>')
def files(filename): return send_from_directory(VIDEO_DIR,filename)

if __name__=='__main__': app.run(host='0.0.0.0',port=5000,debug=False)
