from flask import Flask,render_template,request,redirect,url_for,send_from_directory
import os,sqlite3
from datetime import datetime

app=Flask(__name__)
UPLOAD='videos'; DB='videos.db'; os.makedirs(UPLOAD,exist_ok=True)

def db():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c

def init():
    with db() as c:
        c.execute('CREATE TABLE IF NOT EXISTS videos(id INTEGER PRIMARY KEY AUTOINCREMENT,filename TEXT UNIQUE,title TEXT,description TEXT,upload_date TEXT,views INTEGER DEFAULT 0)')
init()

@app.route('/')
def index():
    with db() as c: videos=c.execute('SELECT * FROM videos ORDER BY upload_date DESC').fetchall()
    return render_template('index.html',videos=videos)

@app.route('/upload',methods=['GET','POST'])
def upload():
    if request.method=='POST' and request.files.get('file'):
        f=request.files['file']; name=os.path.basename(f.filename); f.save(os.path.join(UPLOAD,name))
        with db() as c: c.execute('INSERT OR REPLACE INTO videos(filename,title,description,upload_date) VALUES(?,?,?,?)',(name,request.form.get('title') or name,request.form.get('description',''),datetime.utcnow().isoformat()))
        return redirect(url_for('index'))
    return render_template('upload.html')

@app.route('/video/<int:video_id>')
def video(video_id):
    with db() as c:
        c.execute('UPDATE videos SET views=views+1 WHERE id=?',(video_id,)); c.commit(); row=c.execute('SELECT * FROM videos WHERE id=?',(video_id,)).fetchone()
    if not row:return 'Not found',404
    return render_template('video.html',video=row)

@app.route('/videos/<path:name>')
def files(name): return send_from_directory(UPLOAD,name)

if __name__=='__main__': app.run(host='0.0.0.0',port=5000)
