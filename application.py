import os
import requests

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
login_id = 0
# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/",methods=['GET', 'POST'])
def index():
    global login_id
    if login_id > 0:
        inp ={ "isbn":"","title":"","author":""}
        return render_template("search.html",inp=inp)    
    if request.method == "POST":
        log = request.form.get('login')
        pas = request.form.get('pass')
        res = db.execute("SELECT id FROM users WHERE login=:l AND pass=:p",{"l":log,"p":pas}).fetchone()
        if res:
            login_id=res['id']
            inp ={ "isbn":"","title":"","author":""}
            return search()
        else:
            return render_template("login.html",msg="Login fail. Try again")         
    return render_template("login.html")

@app.route("/search",methods=['GET'])
def search():
    if login_id==0: return render_template("login.html")
    res = []
    sql = []
    isb = request.args.get('isbn')
    if isb is None :
        isb=''
    elif len(isb)>1:
        sql.append("lower(isbn) like '%"+isb.lower()+"%'")
    tit = request.args.get('title')
    if tit is None : 
        tit=''
    elif len(tit)>1:
        sql.append("lower(title) like '%"+tit.lower()+"%'")
    aut = request.args.get('author')
    if aut is None : 
        aut=''
    elif len(aut)>1:
        sql.append("lower(author) like '%"+aut.lower()+"%'")
    inp ={ "isbn":isb , "title":tit , "author":aut}
    if sql:
        a = " and "
        q = "SELECT * FROM books where "+a.join(sql)+" limit 100"
    else:
        q = "SELECT * FROM books limit 100"
    res = db.execute(q).fetchall()
    return render_template("search.html",inp=inp,res=res)

@app.route("/del_review/<isbn>") 
def del_review(isbn):
    global login_id
    if login_id==0: return render_template("login.html")
    db.execute("delete from review where isbn=:i and user_id=:u",{"i":isbn,"u":login_id}) 
    db.commit()
    return book(isbn)
@app.route("/api/<isbn>") 
def api(isbn):
    book = db.execute("SELECT title,author,year FROM books WHERE isbn=:i",{"i":isbn}).fetchone()
    if book:
        r = '{"title":"'+book['title']+'","author":"'+book['author']+'","year":'+str(book['year'])+'","isbn":"'+isbn+'","review_count":'
        avg = db.execute("SELECT count(*),to_char(avg(rating),'FM9.9') from review where isbn=:i",{"i":isbn}).fetchone()
        if avg[0]: 
            r = r+str(avg[0])+',"average_score":'+str(avg[1])+'}'
        else:
            r = r+'0,"average_score":0}'
    else:
        r='404 error'
    return r

@app.route("/book/<isbn>", methods=['GET', 'POST']) 
def book(isbn):
    global login_id
    if login_id==0: return render_template("login.html")
    rev=''
    add_review = True
    if request.method == "POST":
        rev = request.form.get('review')
        rat = request.form.get('rating')
        if len(rev)>5:
            q = "SELECT id from review where isbn=:i and user_id=:u"
            r = db.execute(q,{"i":isbn,"u":login_id}).fetchone()
            if r:
                q = "UPDATE review set rating=:rat,review=:rev,dt=now() WHERE id=:i"
                db.execute(q,{"rat":rat,"rev":rev,"i":r['id']})
            else: 
                q = "INSERT into review (isbn,user_id,rating,review,dt) VALUES (:i,:usr,:rat,:rev,now())"
                db.execute(q,{"i":isbn,"usr":login_id,"rat":rat,"rev":rev}) 
            db.commit()
            add_review = False
    book = db.execute("SELECT isbn,title,author,year FROM books where isbn=:i",{"i":isbn}).fetchone()
    if book is None: 
        book = ['N/A','N/A','N/A','N/A']
        add_review = False
        res=[]
    else:
        q = "SELECT user_id,rating,review,sex,age,dt FROM review join users on user_id=users.id WHERE isbn=:i order by review.id desc limit 100"
        res = db.execute(q,{"i":isbn}).fetchall()
        for r in res:
            if r[0]==login_id: add_review=False
    more = more_info(isbn)
    return render_template("book.html",book=book,more=more,reviews=res,addReview=add_review,rev=rev,me=login_id) 

@app.route("/logout")
def logout():
    global login_id
    login_id=0
    return render_template("login.html",msg="Logout Successfully") 

@app.route("/reg" , methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        pas = request.form.get('pass')
        log = request.form.get('login')
        err = ''
        if len(pas)<6:
            err = 'Password too short (minimum 6 chars)'
        else:
            used = db.execute("SELECT 1 FROM users where login=:l",{"l":log}).fetchone()
            if used:
                err = 'Login already in use, select a different one'
        if err:
            return render_template("register.html",err=err)
        db.execute("INSERT INTO users(login,pass,sex,age) VALUES (:l,:p,:s,:a)",
            {"l":log,"p":pas,"s":request.form.get('gen'),'a':request.form.get('age')})
        db.commit()
        return render_template("login.html",msg="Welcome as a new member. You can now login")
    else:
        return render_template("register.html")
        
def more_info(isbn):
    ret = '<div class="row">'
    url = 'https://www.googleapis.com/books/v1/volumes?q=isbn:'+isbn
    r = requests.get(url=url)
    try:
        d = r.json()
        v = d['items'][0]['volumeInfo']
        ret = ret + "<label class='col-2'>GoogleAPI:</label><div class='col-8'>page_count: "+str(v['pageCount']) + ", ratings_count: "  
        ret = ret + str(v['ratingsCount']) + ", average_rating: " + str(v['averageRating'])+"<br>"
        ret = ret + "Description: " + v['description'] + "</div><div class='col-2'><img src='" + v['imageLinks']['thumbnail']+"'></div></div>"
    except:
        ret = '<p>API call to googleapis.com/books for isbn '+isbn+' fail: '+r.text+ "</p></div>"
    ret = ret + '<div class="row">'
    url = 'https://www.goodreads.com/book/review_counts.json?key=zGIQgZbn6KDXzWbp1pY5sg&isbns='+isbn
    r = requests.get(url=url)
    try:
        d = r.json()
        v = d['books'][0]
        ret = ret + "<label class='col-2'><a target=out href='http://www.goodreads.com/book/isbn/"+isbn+"'>Goodreads stats</a>:</label> " 
        ret = ret + "<div class='col-10'>ratings_count: "+str(v['ratings_count']) + ", average_rating: "+v['average_rating'] + "</div></div>"
    except:
        ret = ret + '<p>API call to goodreads for isbn '+isbn+' fail: '+r.text + "</p></div>"
    return ret