import os
import sqlite3
import cv2
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify, abort, send_from_directory

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
THUMB_FOLDER = "thumbnails"
TEMP_FOLDER = "temp_chunks"
DB = "database.db"
for folder in (UPLOAD_FOLDER, THUMB_FOLDER, TEMP_FOLDER): os.makedirs(folder, exist_ok=True)

def get_db():
    conn = sqlite3.connect(DB); conn.row_factory = sqlite3.Row; return conn

def init_db():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS files (id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT UNIQUE, title TEXT, description TEXT, file_type TEXT, views INTEGER DEFAULT 0, length REAL, filesize INTEGER, upload_date TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS categories (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)")
        c.execute("CREATE TABLE IF NOT EXISTS file_category (file_id INTEGER, category_id INTEGER)")
init_db()

def get_file_type(filename):
    ext = filename.lower().split('.')[-1]
    if ext in {'mp4','avi','mov','mkv','flv','wmv','webm'}: return 'video'
    if ext in {'mp3','wav','ogg','flac','aac','m4a'}: return 'audio'
    return 'other'

def get_video_length(path):
    cap=cv2.VideoCapture(path)
    if not cap.isOpened(): return None
    fps=cap.get(cv2.CAP_PROP_FPS); frames=cap.get(cv2.CAP_PROP_FRAME_COUNT); cap.release()
    return round(frames/fps,2) if fps and fps>0 else None

def generate_thumbnail(path,file_id,time_sec=10):
    cap=cv2.VideoCapture(path)
    if not cap.isOpened(): return
    fps=cap.get(cv2.CAP_PROP_FPS)
    if fps and fps>0: cap.set(cv2.CAP_PROP_POS_FRAMES,int(fps*time_sec))
    success,frame=cap.read()
    if success: cv2.imwrite(f"{THUMB_FOLDER}/{file_id}.jpg",frame)
    cap.release()

@app.route('/')
def index():
    sort=request.args.get('sort','date'); category=request.args.get('category'); conn=get_db(); c=conn.cursor()
    if category:
        query="SELECT f.* FROM files f JOIN file_category fc ON f.id=fc.file_id WHERE fc.category_id=?"; params=(category,)
    else: query="SELECT * FROM files"; params=()
    query += " ORDER BY views DESC" if sort=='views' else (" ORDER BY length DESC NULLS LAST" if sort=='length' else " ORDER BY upload_date DESC")
    c.execute(query,params); files=c.fetchall(); c.execute('SELECT * FROM categories'); categories=c.fetchall(); c.execute('SELECT * FROM file_category'); file_categories=c.fetchall(); conn.close()
    return render_template('index.html',files=files,categories=categories,file_categories=file_categories)

@app.route('/add_category',methods=['POST'])
def add_category():
    name=request.form['name']; conn=get_db(); c=conn.cursor()
    try: c.execute('INSERT INTO categories (name) VALUES (?)',(name,)); conn.commit(); category_id=c.lastrowid
    except sqlite3.IntegrityError: category_id=None
    conn.close(); return jsonify({'id':category_id,'name':name})

@app.route('/scan_files')
def scan_files():
    conn=get_db(); c=conn.cursor(); existing={r['filename'] for r in c.execute('SELECT filename FROM files').fetchall()}
    for filename in os.listdir(UPLOAD_FOLDER):
        path=os.path.join(UPLOAD_FOLDER,filename)
        if os.path.isfile(path) and filename not in existing:
            ftype=get_file_type(filename); length=get_video_length(path) if ftype=='video' else None
            c.execute('INSERT INTO files (filename,title,description,file_type,length,filesize,upload_date) VALUES (?,?,?,?,?,?,?)',(filename,filename,'Автоматически добавлено',ftype,length,os.path.getsize(path),datetime.utcnow().isoformat()))
            if ftype=='video': generate_thumbnail(path,c.lastrowid,10)
    conn.commit(); conn.close(); return redirect(url_for('index'))

@app.route('/file/<int:file_id>',methods=['GET','POST'])
def file_page(file_id):
    conn=get_db(); c=conn.cursor()
    if request.method=='POST':
        c.execute('UPDATE files SET title=?, description=? WHERE id=?',(request.form['title'],request.form['description'],file_id))
        c.execute('DELETE FROM file_category WHERE file_id=?',(file_id,))
        for cat in request.form.getlist('categories'): c.execute('INSERT INTO file_category VALUES (?,?)',(file_id,cat))
        thumb_time=request.form.get('thumb_time')
        if thumb_time:
            row=c.execute('SELECT filename,file_type FROM files WHERE id=?',(file_id,)).fetchone()
            if row and row['file_type']=='video': generate_thumbnail(os.path.join(UPLOAD_FOLDER,row['filename']),file_id,float(thumb_time))
        conn.commit(); conn.close(); return redirect(url_for('file_page',file_id=file_id))
    c.execute('UPDATE files SET views=views+1 WHERE id=?',(file_id,)); conn.commit(); file=c.execute('SELECT * FROM files WHERE id=?',(file_id,)).fetchone()
    if not file: abort(404)
    categories=c.execute('SELECT * FROM categories').fetchall(); file_cats=[r['category_id'] for r in c.execute('SELECT category_id FROM file_category WHERE file_id=?',(file_id,)).fetchall()]; conn.close()
    return render_template('file.html',file=file,categories=categories,file_cats=file_cats)

@app.route('/upload')
def upload_page():
    conn=get_db(); categories=conn.execute('SELECT * FROM categories').fetchall(); conn.close(); return render_template('upload.html',categories=categories)

@app.route('/upload_chunk',methods=['POST'])
def upload_chunk():
    f=request.files['file']; filename=request.form['filename']; chunk=int(request.form['chunk']); total=int(request.form['total']); path=os.path.join(TEMP_FOLDER,f'{filename}.part{chunk}'); f.save(path)
    if chunk+1==total:
        final=os.path.join(UPLOAD_FOLDER,filename)
        with open(final,'wb') as out:
            for i in range(total):
                part=os.path.join(TEMP_FOLDER,f'{filename}.part{i}')
                with open(part,'rb') as inp: out.write(inp.read())
                os.remove(part)
    return jsonify({'status':'ok'})

@app.route('/finalize_upload',methods=['POST'])
def finalize_upload():
    filename=request.form['filename']; title=request.form['title']; desc=request.form['description']; path=os.path.join(UPLOAD_FOLDER,filename); ftype=get_file_type(filename); length=get_video_length(path) if ftype=='video' else None
    conn=get_db(); c=conn.cursor(); c.execute('INSERT INTO files (filename,title,description,file_type,length,filesize,upload_date) VALUES (?,?,?,?,?,?,?)',(filename,title,desc,ftype,length,os.path.getsize(path),datetime.utcnow().isoformat())); file_id=c.lastrowid
    for cat in request.form.getlist('categories'): c.execute('INSERT INTO file_category VALUES (?,?)',(file_id,cat))
    conn.commit(); conn.close(); thumb_time=request.form.get('thumb_time')
    if ftype=='video' and thumb_time: generate_thumbnail(path,file_id,float(thumb_time))
    return redirect(url_for('index'))

@app.route('/categories',methods=['GET','POST'])
def categories_page():
    conn=get_db(); c=conn.cursor()
    if request.method=='POST' and request.form.get('name'):
        try: c.execute('INSERT INTO categories (name) VALUES (?)',(request.form['name'],)); conn.commit()
        except sqlite3.IntegrityError: pass
    categories=c.execute('SELECT * FROM categories ORDER BY name ASC').fetchall(); conn.close(); return render_template('categories.html',categories=categories)

@app.route('/uploads/<path:filename>')
def uploaded_file(filename): return send_from_directory(UPLOAD_FOLDER,filename)
@app.route('/download/<path:filename>')
def download_file(filename): return send_from_directory(UPLOAD_FOLDER,filename,as_attachment=True)
@app.route('/thumbnails/<path:filename>')
def thumb_file(filename): return send_from_directory(THUMB_FOLDER,filename)

if __name__=='__main__': app.run(host='0.0.0.0')