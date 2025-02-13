import os, secrets
from flask import render_template, request, redirect, session, flash, jsonify

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename                                                                  
from datetime import datetime
from home import app
from home.models import User, db, Property_listing, Message_table, User, State, Property_type, Property_image
from sqlalchemy import desc
from sqlalchemy.orm.exc import NoResultFound

@app.errorhandler(404)
def page_not_found(error):
    return render_template("user/error404.html",error=error), 404



@app.route("/",methods=["GET"])
def index_page():
    state = db.session.query(State).all()
    prop = db.session.query(Property_type).all()
    liss = db.session.query(Property_listing).order_by(desc(Property_listing.created_on)).limit(3).all()
    if len(liss) < 3:
        liss = []
        

    
    if request.method == 'GET':
        stat = request.args.get("state")
        type = request.args.get("type")
        st = db.session.query(State).filter(State.state_name == stat).first()
        ty = db.session.query(Property_type).filter(Property_type.property_name == type).first()

        return render_template("user/index.html",state=state,prop=prop,st=st,ty=ty,liss=liss)
    else:
        return render_template("index.html",state=state,prop=prop,liss=liss)



@app.route("/search/",methods=["POST","GET"])
def search_page():
    stat = request.args.get("state")
    type = request.args.get("type")
    st = db.session.query(State).filter(State.state_name == stat).first()
    ty = db.session.query(Property_type).filter(Property_type.property_name == type).first()
    if not st or not ty:
        return redirect("/")
    li = db.session.query(Property_listing).filter(Property_listing.property_state_id == st.state_id,Property_listing.property_type_id == ty.property_id).order_by(desc(Property_listing.created_on)).all()
    
    lis = db.session.query(Property_listing).all()
    return render_template("user/search.html",li=li,lis=lis)
@app.route("/home/")
def home_page():
    email = session.get("email")
    id = db.session.execute(db.text(f"SELECT user_id FROM `user` WHERE user_email = '{email}' "))
    id=id.fetchone()
    liss = db.session.query(Property_listing).order_by(desc(Property_listing.created_on)).limit(3).all()
    if len(liss) < 3:
        liss = []
    

    state = db.session.query(State).all()
    prop = db.session.query(Property_type).all()
    if email == None:
        return redirect("/")
    else:
        for d in id:
            ids = d
    return render_template("user/home.html",ids=ids,state=state,prop=prop,liss=liss)
@app.route("/layout/")
def layout():
    email = session.get("email")
    id = db.session.execute(db.text(f"SELECT user_id FROM `user` WHERE user_email = '{email}' "))
    id=id.fetchone()
    if email == None:
        return redirect("/")
    else:
        for d in id:
            ids = d
    return render_template("user/layout.html",ids=ids)
    

@app.route("/profile/<id>/",methods=["POST","GET"])
def profile_page(id):
    email = session.get("email")

    name = db.session.execute(db.text(f"SELECT user_firstname,user_lastname FROM `user` WHERE user_email = '{email}' "))
    names = name.fetchone()

    id = db.session.execute(db.text(f"SELECT user_id FROM `user` WHERE user_email = '{email}' "))
    id=id.fetchone()

    rows = db.session.execute(db.text(f"SELECT user_type FROM `user` WHERE user_email = '{email}' "))
    type = rows.fetchone()

    use = db.session.execute(db.text(f"SELECT user_status FROM `user` WHERE user_email = '{email}' "))
    status = use.fetchone()
    if not status:
        return redirect("/login/")
    
    

    
    

    state = db.session.query(State).all()
    prop = db.session.query(Property_type).all()

    mes = request.form.get("mesor")

    if email == None:
        return redirect("/login/")
    else:
        if status[0] == "Inactive":
            flash("errormsg","Your Account have been freezed, please contact the admin ")
            return redirect("/login/")
        
        for d in id: 
            user = db.session.query(User).filter(User.user_id == d).all()
            if id:
                chat_users = db.session.query(User).filter(User.user_id.in_(db.session.query(Message_table.reciever_id).filter(Message_table.sender_id == d))|User.user_id.in_(db.session.query(Message_table.sender_id).filter(Message_table.reciever_id == d))).all()
                li = db.session.query(Property_listing).filter(Property_listing.user_id == d).order_by(desc(Property_listing.created_on)).all()
                
                for c in chat_users:
                  
                    
                    try:
                        mes = db.session.query(Message_table).filter((Message_table.sender_id == d)&(Message_table.reciever_id == c.user_id)|((Message_table.sender_id == c.user_id)&(Message_table.reciever_id == d))).all()
                       
                        return render_template("user/profile.html",names=names,type=type,chat_users=chat_users,state=state,prop=prop,d=d,li=li,user=user,id=id)
                    except TypeError:
                        return render_template("user/profile.html",names=names,type=type,chat_users=chat_users,state=state,prop=prop,d=d,li=li,user=user,id=id)
                    
                    
                    
                
                
            elif id == "NoneType":
                return redirect("/login/")
        

    
    
    return render_template("user/profile.html",names=names,type=type,chat_users=chat_users,state=state,prop=prop,d=d,li=li,user=user,id=id)
    

@app.route("/owner/<ide>/<die>/",methods=["POST","GET"])
def owner_page(ide,die):
    email = session.get("email")
    id = db.session.execute(db.text(f"SELECT user_id FROM `user` WHERE user_email = '{email}' "))
    id=id.fetchone()
    if not id :
        id = db.session.execute(db.text(f"SELECT admin_id FROM `admin` WHERE admin_email = '{email}' "))
        id=id.fetchone()
    user = db.session.query(User).filter(User.user_id == die).one()
    if email == None:
        flash("feedback","Login to contact realtor ")
        return redirect("/login/")
    else:
        for d in id:
            li = db.session.query(Property_listing).filter(Property_listing.user_id == die).order_by(desc(Property_listing.created_on)).all()
            if request.method == "POST":
                name = request.form.get("name")
                emai = request.form.get("email")
                num = request.form.get("num")
                text = request.form.get("text")
                mese = Message_table(message_content=f"{name}\n {emai}\n {num}\n {text}\n",sender_id=d,reciever_id=die,property_id=ide)
                db.session.add(mese)
                db.session.commit()
                return redirect(f"/info/{ide}/{die}/")
            else:
                return render_template("user/owner.html",li=li,user=user,ids=die)
        return render_template("user/owner.html",li=li,user=user,ids=die)

@app.route("/rent/",methods=["POST","GET"])
def rent_page():
    email = session.get("email") 
    
    if email == None:
        ids = 0
    else:
        id = db.session.execute(db.text(f"SELECT user_id FROM `user` WHERE user_email = '{email}' "))
        id=id.fetchone()
        if not id:
            id = db.session.execute(db.text(f"SELECT admin_id FROM `admin` WHERE admin_email = '{email}' "))
            id=id.fetchone()
        ids = id[0]

    state = db.session.query(State).all()
    prop = db.session.query(Property_type).all()
    prope = db.session.query(Property_listing).all()

    

    if request.method == 'POST':    
        stat = request.form.get("state")
        type = request.form.get("type")

        st = db.session.query(State).filter(State.state_name == stat).first()
        ty = db.session.query(Property_type).filter(Property_type.property_name == type).first()
        if st == None or ty == None:
            flash("errormsg","Please select both options before proceeding ")
            return redirect("/rent/")

        if not stat or not type:
            flash("errormsg","Please select both options before proceeding")
            return redirect("/rent/")
        
        li = db.session.query(Property_listing).filter(Property_listing.property_state_id == st.state_id,Property_listing.property_type_id == ty.property_id,Property_listing.property_category == "rent").order_by(desc(Property_listing.created_on)).all()
        lis = db.session.query(Property_listing).filter(Property_listing.property_category == "rent").order_by(desc(Property_listing.created_on)).all()  
        return render_template('user/rent.html',state=state,prop=prop,prope=prope,stat=stat,type=type,st=st,ty=ty,li=li,lis=lis)
          
    else:
        lis = db.session.query(Property_listing).filter(Property_listing.property_category == "rent").order_by(desc(Property_listing.created_on)).all()
        return render_template('user/rent.html',state=state,prop=prop,lis=lis,ids=ids)


@app.route("/buy/",methods=["POST","GET"])
def buy_page():
    email = session.get("email")
    if email == None:
        ids = 0
        
    else:
        id = db.session.execute(db.text(f"SELECT user_id FROM `user` WHERE user_email = '{email}' "))
        id=id.fetchone()
        if not id:
            id = db.session.execute(db.text(f"SELECT admin_id FROM `admin` WHERE admin_email = '{email}' "))
            id=id.fetchone()

        ids = id[0]

    state = db.session.query(State).all()
    prop = db.session.query(Property_type).all()
    prope = db.session.query(Property_listing).all()


    if request.method == 'POST':
        stat = request.form.get("state")
        type = request.form.get("type")

        st = db.session.query(State).filter(State.state_name == stat).first()
        ty = db.session.query(Property_type).filter(Property_type.property_name == type).first()
        if st == None or ty == None:
            flash("errormsg","Please select both options before proceeding ")
            return redirect("/buy/")

        if not stat or not type:
            flash("errormsg","Please select both options before proceeding")
            return redirect("/buy/")
        
        li = db.session.query(Property_listing).filter(Property_listing.property_state_id == st.state_id,Property_listing.property_type_id == ty.property_id,Property_listing.property_category == "buy").order_by(desc(Property_listing.created_on)).all()
        lis = db.session.query(Property_listing).filter(Property_listing.property_category == "buy").order_by(desc(Property_listing.created_on)).all()
        return render_template('user/buy.html',state=state,prop=prop,prope=prope,stat=stat,type=type,st=st,ty=ty,li=li,lis=lis)
               
    else:
        lis = db.session.query(Property_listing).filter(Property_listing.property_category == "buy").order_by(desc(Property_listing.created_on)).all()
        return render_template('user/buy.html',state=state,prop=prop,lis=lis,ids=ids)

@app.route("/shortlet/",methods=["POST","GET"])
def shortlet_page():
    email = session.get("email")
    if email == None:
        ids = 0
    else:
        id = db.session.execute(db.text(f"SELECT user_id FROM `user` WHERE user_email = '{email}' "))
        id=id.fetchone()
        if not id:
            id = db.session.execute(db.text(f"SELECT admin_id FROM `admin` WHERE admin_email = '{email}' "))
            id=id.fetchone()
        ids = id[0]

    state = db.session.query(State).all()
    prop = db.session.query(Property_type).all()
    prope = db.session.query(Property_listing).all()


    if request.method == 'POST':
        stat = request.form.get("state")
        type = request.form.get("type")

        st = db.session.query(State).filter(State.state_name == stat).first()
        ty = db.session.query(Property_type).filter(Property_type.property_name == type).first()
        if st == None or ty == None:
            flash("errormsg","Please select both options before proceeding ")
            return redirect("/shortlet/")

        if not stat or not type:
            flash("errormsg","Please select both options before proceeding")
            return redirect("/shortlet/")
        
        li = db.session.query(Property_listing).filter(Property_listing.property_state_id == st.state_id,Property_listing.property_type_id == ty.property_id,Property_listing.property_category == "shortlet").order_by(desc(Property_listing.created_on)).all()
        lis = db.session.query(Property_listing).filter(Property_listing.property_category == "shortlet").order_by(desc(Property_listing.created_on)).all()
        return render_template('user/shortlet.html',state=state,prop=prop,prope=prope,stat=stat,type=type,st=st,ty=ty,li=li,lis=lis)
               
    else:
        lis = db.session.query(Property_listing).filter(Property_listing.property_category == "shortlet").order_by(desc(Property_listing.created_on)).all()
        return render_template('user/shortlet.html',state=state,prop=prop,ids=ids,lis=lis)

@app.route("/demo_prop/")
def demo_prop():
    flash("feedback"," Oops! That property is not available")
    return redirect("/buy/")
@app.route("/info/<ida>/<uid>/",methods=["POST","GET"])
def info_page(ida,uid):
    email = session.get("email")
    
    user = db.session.query(User).filter(User.user_id == uid).one()
    inf = db.session.query(Property_listing).filter(Property_listing.property_id == ida).first()
    sate = db.session.query(State).filter(State.state_id == inf.property_state_id).first()
    pic = db.session.query(Property_image).filter(Property_image.property_id == ida).all()
    leen = len(pic)
    if email == None:
        flash("feedback","Login to get more info about the property ")
        return redirect("/login/")
    else:
        id = db.session.execute(db.text(f"SELECT user_id FROM `user` WHERE user_email = '{email}' "))
        id=id.fetchone()
        
        if id:
            di = id.user_id
            print(di)
            for d in id:
                if request.method == "POST":
                    name = request.form.get("name")
                    emai = request.form.get("email")
                    num = request.form.get("num")
                    text = request.form.get("text")
                    mese = Message_table(message_content=f"{name}\n {emai}\n {num}\n {text}\n",sender_id=d,reciever_id=uid,property_id=ida)
                    db.session.add(mese)
                    db.session.commit()
                    return redirect(f"/info/{ida}/{uid}/")
                else:
                    return render_template("user/info.html",ida=ida,uid=uid,user=user,ids=di,inf=inf,pic=pic,leen=leen,sate=sate)
                
        else:
            id = db.session.execute(db.text(f"SELECT admin_id FROM `admin` WHERE admin_email = '{email}' "))
            id=id.fetchone()
            di = id.admin_id
            print(di)
            for d in id:
                if request.method == "POST":
                    name = request.form.get("name")
                    emai = request.form.get("email")
                    num = request.form.get("num")
                    text = request.form.get("text")
                    mese = Message_table(message_content=f"{name}\n {emai}\n {num}\n {text}\n",sender_id=d,reciever_id=uid,property_id=ida)
                    db.session.add(mese)
                    db.session.commit()
                    return redirect(f"/info/{ida}/{uid}/")
                else:
                    return render_template("user/info.html",ida=ida,uid=uid,user=user,ids=di,inf=inf,pic=pic,leen=leen,sate=sate)

        return render_template("user/info.html",ida=ida,uid=uid,user=user,ids=di,inf=inf,pic=pic,leen=leen,sate=sate)

@app.route("/logout/")
def logout_page():
    session.pop("email",None)
    flash("feedback","You have logged out")
    return redirect("/login/")

@app.route("/login/",methods=["POST","GET"])
def login_page():
    if request.method == "GET":
        return render_template("user/login.html")
    else:
        email = request.form.get("email")
        password = request.form.get("password")

        record = db.session.query(User).filter(User.user_email==email).first()
        if record: 
            hashed_password = record.user_password
            chk = check_password_hash(hashed_password,password)#compare the hashed password with the plain text coming from the form. return true or false
            if chk:
                use = db.session.execute(db.text(f"SELECT user_status FROM `user` WHERE user_password = '{hashed_password}' AND user_email = '{email}' "))
                status = use.fetchone()
                if status[0] == "Inactive":
                    flash("errormsg","Your Account have been freezed, please contact the admin ")
                    return redirect("/login/")
                else:
                
                    lo = db.session.query(User).get(record.user_id)
                    lo.last_login = datetime.now()
                    db.session.commit()
                    session["email"]= email
                    return redirect(f"/profile/{record.user_id}/")
            else:
                flash('errormsg', 'Invalid Password')
                return redirect ('/login/')
        else:
            flash('errormsg', 'Invalid Email')
            return redirect ('/login/')


     

@app.route("/register/",methods=["POST","GET"])
def register_page():
    if request.method == "GET":
        return render_template("user/register.html") 
    else:
        fname = request.form.get("firstname")
        lname = request.form.get("lastname")
        email = request.form.get("email")
        number = request.form.get("number")
        password = request.form.get("password")
        cpassword = request.form.get("cpassword")
        select = request.form.get("select")
        if password != cpassword:
            flash("errormsg","Password mismatch, please try again ")
            return redirect("/register/")
        elif fname == "":
            flash("errormsg","Please enter your Firstname ")
            return redirect("/register/")
        elif lname == "":
            flash("errormsg","Please enter your Lastname ")
            return redirect("/register/")
        elif email == "":
            flash("errormsg","Please enter your Email ")
            return redirect("/register/")
        elif password == "":
            flash("errormsg","Please enter your Password ")
            return redirect("/register/")
        elif select == "Select User type":
            flash("errormsg","Please Select user type ")
            return redirect("/register/")
        else:
            hashed = generate_password_hash(password)
            user =User(user_firstname=fname,user_lastname=lname,user_email=email,user_number=number,user_password=hashed,user_type=select)
            db.session.add(user)
            db.session.commit()
            flash("feedback","An account has been created for you please login ")
            return redirect("/login/")









        




@app.route("/profile/<id>/Property/listing/", methods=["POST","GET"])
def property_listing(id):
    state = db.session.query(State).all()
    prop = db.session.query(Property_type).all()

    if request.method == 'POST':
        stat = request.form.get("state")
        type = request.form.get("type")
        cat = request.form.get("cat")
        title = request.form.get("title")
        desc = request.form.get("desc")
        amen = request.form.get("amen")
        price = request.form.get("price")
        image = request.form.get("image")

        st = db.session.query(State).filter(State.state_name == stat)
        ty = db.session.query(Property_type).filter(Property_type.property_name == type)
        email = session.get("email")
        id = db.session.execute(db.text(f"SELECT user_id FROM `user` WHERE user_email = '{email}' "))
        id=id.fetchone()

        for d in id:
            prop = Property_listing(user_id=d,title=title,description=desc,property_price=price,property_type_id=ty.property_id,property_amenities=amen,property_category=cat,property_state_id=st.state_id)
            db.session.add(prop)
            db.session.commit()

        return redirect(f"/profile/{d}/")
    return redirect(f"/profile/{d}/")





@app.route("/upload/property/", methods=["POST","GET"])
def upload():
    email = session.get("email")
    id = db.session.execute(db.text(f"SELECT user_id FROM `user` WHERE user_email = '{email}' "))
    id=id.fetchone()
    dit = id.user_id

    state = db.session.query(State).all()
    prop = db.session.query(Property_type).all()

    if request.method == 'POST':
        stat = request.form.get("state")
        type = request.form.get("type")
        cat = request.form.get("cat")
        title = request.form.get("title")
        desc = request.form.get("desc")
        amen = request.form.get("amen")
        price = request.form.get("price")
        bed = request.form.get("bed")
        bat = request.form.get("bat")
        park = request.form.get("park")

        allowed_ext = [".jpg", ".jpeg", ".png", ".gif"]
        uploaded_files = []

        for i in range(1, 6):  # Loop through file inputs im1 to im5
            file = request.files.get(f"im{i}")
            if file:
                _, ext = os.path.splitext(file.filename)
                if ext.lower() in allowed_ext:
                    filename = f"{secrets.token_hex(10)}{ext}"
                    file.save(f"home/static/uploads/{filename}")
                    uploaded_files.append(filename)

        

        
        if cat == "property category":
            flash("errormsg","Please select a Category")
            return redirect("/upload/property/")
        elif type == "property type":
            flash("errormsg","Please select Property type")
            return redirect("/upload/property/")
        elif stat == "property state":
            flash("errormsg","Please select Property state")
            return redirect("/upload/property/")
        elif bed == "bed many":
            flash("errormsg","Please select Bedroom")
            return redirect("/upload/property/")
        elif bat == "bat many":
            flash("errormsg","Please select Bathroom")
            return redirect("/upload/property/")
        elif park == "park many":
            flash("errormsg","Please select Parking Space")
            return redirect("/upload/property/")
        elif title == "":
            flash("errormsg","Please select a title")
            return redirect("/upload/property/")
        elif desc == "":
            flash("errormsg","Please The Property description")
            return redirect("/upload/property/")
        elif amen == "":
            flash("errormsg","Please The Property Amenities")
            return redirect("/upload/property/")
        elif price == "":
            flash("errormsg","Please The Property Price")
            return redirect("/upload/property/")

        st = db.session.query(State).filter(State.state_name == stat).first()
        ty = db.session.query(Property_type).filter(Property_type.property_name == type).first()
        allowed_ext = [".jpg",".jpeg",".png",".gif"]
        file = request.files.get("image")
        _,ext = os.path.splitext(file.filename)
        rand_str = secrets.token_hex(10)
        filename = ""
        if ext in allowed_ext:
            filename = f"{rand_str}{ext}"
            file.save(f"home/static/uploads/{filename}")

        else:
            flash ('feedback', 'Your cover image must be an image file')
            return redirect("/profile/")
        for d in id:
            
            prop = Property_listing(user_id=d,title=title,description=desc,property_price=price,property_cover_picture=filename,property_amenities=amen,property_category=cat,property_state_id=st.state_id,property_type_id=ty.property_id,bedroom_number=bed,bathroom_number=bat,parking_space=park)
            db.session.add(prop)
            db.session.commit()
            if uploaded_files:
                images = [
                    Property_image(property_picture=file, property_id=prop.property_id)
                    for file in uploaded_files
                ]
                db.session.add_all(images)  # Add all images to the session
                db.session.commit() 
            flash('feedback',"Post Uploaded successfully!")
            return redirect(f"/profile/{d}/")
        return redirect(f"/profile/{d}/")
    

    return render_template("user/upload.html",state=state,prop=prop,ids=dit)
    

@app.route("/edit/<idt>/post/", methods=["POST","GET"])
def edit_post(idt):
    email = session.get("email")
    id = db.session.execute(db.text(f"SELECT user_id FROM `user` WHERE user_email = '{email}' "))
    id=id.fetchone()


    state = db.session.query(State).all()
    prop = db.session.query(Property_type).all()

    iddt = db.session.query(Property_listing).filter(Property_listing.property_id == idt).first()

    sta = db.session.query(State).filter(State.state_id == iddt.property_state_id).one()
    tya = db.session.query(Property_type).filter(Property_type.property_id == iddt.property_type_id).one()
    print(iddt.property_state_id)
    print(sta.state_name, tya.property_name)

    for d in id:
        li = db.session.query(Property_listing).filter(Property_listing.property_id == idt).all()
    if request.method == 'POST':
        stat = request.form.get("state")
        type = request.form.get("type")
        cat = request.form.get("cat")
        title = request.form.get("title")
        desc = request.form.get("desc")
        amen = request.form.get("amen")
        price = request.form.get("price")
        bed = request.form.get("bed")
        bat = request.form.get("bat")
        park = request.form.get("park")

        if cat == "property category":
            flash("errormsg","Please select a Category")
            return redirect(f"/edit/{idt}/post/")
        elif type == "property type":
            flash("errormsg","Please select Property type")
            return redirect(f"/edit/{idt}/post/")
        elif stat == "property state":
            flash("errormsg","Please select Property state")
            return redirect(f"/edit/{idt}/post/")
        elif title == "":
            flash("errormsg","Please select a title")
            return redirect(f"/edit/{idt}/post/")
        elif desc == "":
            flash("errormsg","Please The Property description")
            return redirect(f"/edit/{idt}/post/")
        elif amen == "":
            flash("errormsg","Please The Property Amenities")
            return redirect(f"/edit/{idt}/post/")
        elif price == "":
            flash("errormsg","Please The Property Price")
            return redirect(f"/edit/{idt}/post/")
        elif bed == "bed many":
            flash("errormsg","Please select Bedroom")
            return redirect("/upload/property/")
        elif bat == "bat many":
            flash("errormsg","Please select Bathroom")
            return redirect("/upload/property/")
        elif park == "park many":
            flash("errormsg","Please select Parking Space")
            return redirect("/upload/property/")

        st = db.session.query(State).filter(State.state_name == stat).one()
        ty = db.session.query(Property_type).filter(Property_type.property_name == type).one()

        allowed_ext = [".jpg",".jpeg",".png",".gif"]
        file = request.files.get("image")
        _,ext = os.path.splitext(file.filename)
        rand_str = secrets.token_hex(10)
        filename = ""
        if ext in allowed_ext:
            filename = f"{rand_str}{ext}"
            file.save(f"home/static/uploads/{filename}")   
        else:
            flash ('errormsg', 'Your cover image must be an image file')
            return redirect(f"/edit/{idt}/post/")
        for l in li:
            l=l
        
        post = Property_listing.query.get(l.property_id)
        post.title = title
        post.description = desc
        post.property_price = price
        post.property_cover_picture = filename
        post.property_amenities = amen
        post.property_category = cat
        post.property_state_id = st.state_id
        post.property_type_id = ty.property_id

        post.bedroom_number = bed
        post.bathroom_number = bat
        post.parking_space = park

       

        db.session.commit()

        flash ('feedback', 'Post Edited successfully')   
        return redirect(f"/profile/{d}/")
    return render_template("user/edit_post.html",state=state,prop=prop,ids=d,idt=iddt,sta=sta,tya=tya)


@app.route("/profile/<id>/edit/", methods=["POST","GET"])
def profile_edit(id):
    email = session.get("email")

    ida = db.session.execute(db.text(f"SELECT user_id FROM `user` WHERE user_email = '{email}' "))
    ida=ida.fetchone()

    fname = request.form.get("fname")
    lname = request.form.get("lname")
    num = request.form.get("num")
    emai = request.form.get("email")
    img = request.form.get("image")
    if fname == "":
        flash ('errormsg', 'Please First Name is required')
        return redirect(f"/profile/{id}/edit")
    elif lname == "":
        flash ('errormsg', 'Please Last Name is required')
        return redirect(f"/profile/{id}/edit")
    elif num == "":
        flash ('errormsg', 'Please Number is required')
        return redirect(f"/profile/{id}/edit")
    elif emai == "":
        flash ('errormsg', 'Please Email is required')
        return redirect(f"/profile/{id}/edit")

    for d in ida:
        user = db.session.query(User).filter(User.user_id == d).all()
        prof = User.query.get(id)
        ids = d
        if request.method == 'POST':

            allowed_ext = [".jpg",".jpeg",".png",".gif"]
            file = request.files.get("image")
            _,ext = os.path.splitext(file.filename)
            rand_str = secrets.token_hex(10)
            filename = ""

            if ext in allowed_ext:
                filename = f"{rand_str}{ext}"
                file.save(f"home/static/uploads/{filename}")

            else:
                flash ('feedback', 'Your cover image must be an image file')
                return redirect(f"/profile/{d}/edit/")
            
            prof.user_firstname = fname
            prof.user_lastname = lname
            prof.user_number = num
            prof.user_email = emai
            prof.user_picture = filename
            db.session.commit()
            flash('feedback',"Profile Edited successfully!")
            return redirect(f"/profile/{d}/")

    return render_template("user/profile_edit.html",user=user,ids=ids)

@app.route("/post/<post_id>/delete/")
def delete_post(post_id):
    email = session.get("email")

    ida = db.session.execute(db.text(f"SELECT user_id FROM `user` WHERE user_email = '{email}' "))
    ida=ida.fetchone()
    for d in ida:
        d=d
    post = Property_listing.query.get(post_id)
    db.session.delete(post)
    db.session.commit()

    flash('feedback',"Post Deleted successfully!")
    return redirect(f"/profile/{d}/")





@app.route("/message/<us>/", methods=["POST", "GET"])
def message_content(us):
    email = session.get("email")
    user_id = db.session.execute(db.text(f"SELECT user_id FROM `user` WHERE user_email = '{email}' ")).fetchone()
    
    if not user_id:
        return redirect("/login/")
    
    user_id = user_id[0]  

    user_profile = db.session.query(User).filter(User.user_id == us).one()
    
    
    messages = db.session.query(Message_table).filter(
        ((Message_table.sender_id == user_id) & (Message_table.reciever_id == us)) |
        ((Message_table.sender_id == us) & (Message_table.reciever_id == user_id))
    ).all()
    proz = 0
    for m in messages:
        if m.property_id:
            proz = db.session.query(Property_listing).filter(Property_listing.property_id == m.property_id).all()
            
       
       
    
    

    if request.method == "POST":
        message_content = request.form.get("mesor")
        if message_content:
            new_message = Message_table(sender_id=user_id, reciever_id=us, message_content=message_content)
            db.session.add(new_message)
            db.session.commit()
        
        return "", 204  

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        message_html = ""
        for m in messages:
            
            if m.property_id != None and m.sender_id == user_id:
                message_html += f'<div class="d-flex qws"><div><div class="k align-center mt-0"><li class="elio iled bafv"><img class="torq" src="/static/uploads/{proz[0].property_cover_picture}" alt=""> <br>{m.message_content} <br><a href="/info/{proz[0].property_id}/{user_id}/" class="pro btn  m-1" ><h6 class="navbar-brand ppo ">view property</h6></a></li></div></div></div>'
            elif m.property_id != None and m.sender_id != user_id:
                message_html += f'<div class="d-flex qws"><div><div class="k align-center mt-0"><li class="elio ledi bafv"><img class="torq" src="/static/uploads/{proz[0].property_cover_picture}" alt=""> <br>{m.message_content} <br><a href="/info/{proz[0].property_id}/{user_id}/" class="pro btn  m-1" ><h6 class="navbar-brand prof ">view property</h6></a></li></div></div></div>'
            elif m.sender_id == user_id:
                message_html += f'<div class="d-flex qws"><div class="k align-center me-3 ms-3"><li class="elio iled">{m.message_content}</li></div></div>'
            else:
                message_html += f'<div class="d-flex qwzs"><div class="k align-center me-3 ms-3"><li class="elio ledi">{m.message_content}</li></div></div>'
        
        return jsonify({"messages": message_html})  

    
    return render_template("user/message.html", mes=messages, use=user_profile, id=[user_id], ids=user_id, us=us, proz=proz)




@app.route("/property/<prop>/", methods=["POST", "GET"])
def property_image(prop):
    if request.method == "POST":
        allowed_ext = [".jpg", ".jpeg", ".png", ".gif"]
        uploaded_files = []

        for i in range(1, 6):  
            file = request.files.get(f"im{i}")
            if file:
                _, ext = os.path.splitext(file.filename)
                if ext.lower() in allowed_ext:
                    filename = f"{secrets.token_hex(10)}{ext}"
                    file.save(f"home/static/uploads/{filename}")
                    uploaded_files.append(filename)

        if uploaded_files:
            images = [
                Property_image(property_picture=file, property_id=prop)
                for file in uploaded_files
            ]
            db.session.add_all(images)  
            db.session.commit()  
            return redirect(f"/profile/{prop}/")
        else:
            return {"message": "No valid files uploaded"}, 400

    return render_template("user/image_upload.html")
