from flask import render_template, request, redirect, session, flash

from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from home import app
from home.models import User, db, Property_listing, Admin, State, Property_type

@app.route("/admin/",methods=["POST","GET"])
def admin():
    
    posts = db.session.query(User).all()
    prop = db.session.query(Property_listing).all()
    result= posts
    set = [0]
    typ = [0]
    for p in prop:
        sst = db.session.query(State).filter(State.state_id == p.property_state_id).first()
        ty = db.session.query(Property_type).filter(Property_type.property_id == p.property_type_id).first()
        set.append(sst)
        typ.append(ty)

    
    email = session.get("e_mail")
    if email == None:
        return redirect("/admin_login/")
    else:
        if request.method == "POST":
            select = request.form.get("select")
            post_id = request.form.get("id")
            if select == "Inactive" or select == "Active":
                post = db.session.query(User).get(post_id)
                post.user_status = select
                db.session.commit()
                return render_template("admin/admin.html", result=result,select=select,post_id=post,prop=prop,set=set,typ=typ)
            elif select == "delete":
                user = User.query.get(post_id)
                db.session.delete(user)
                db.session.commit()
                return render_template("admin/admin.html", result=result,select=select,post_id=post,prop=prop,set=set,typ=typ)
            else:
                return render_template("admin/admin.html", result=result,prop=prop,set=set,typ=typ)
        else:
            return render_template("admin/admin.html", result=result,prop=prop,set=set,typ=typ)

@app.route("/user/<idd>/profile/")
def user_profile(idd):
    email = session.get("e_mail")
    id = db.session.execute(db.text(f"SELECT admin_id FROM `admin` WHERE admin_email = '{email}' "))
    id=id.fetchone()
    user = db.session.query(User).filter(User.user_id == idd).first()
    lent = db.session.query(Property_listing).filter(Property_listing.user_id == idd).all()
    lenn = len(lent)
    print(id)
    return render_template("admin/admin_user.html",user=user,lenn=lenn,id=id)

@app.route("/admin_login/",methods=["POST","GET"])
def admin_login():
    if request.method == "GET":
        return render_template("admin/admin_login.html")
    else:
        email = request.form.get("email")
        password = request.form.get("password")

        record = db.session.query(Admin).filter(Admin.admin_email==email).first()
        if record: 
            hashed_password = record.admin_password
            chk = check_password_hash(hashed_password,password)
            if chk:
                lo = db.session.query(Admin).get(record.admin_id)
                lo.admin_login = datetime.now()
                db.session.commit()
                session["e_mail"]= email
                return redirect("/admin/")
            else:
                flash('errormsg', 'Invalid Password')
                return redirect ('/admin_login/')
        else:
            flash('errormsg', 'Invalid Email')
            return redirect ('/admin_login/')
        
@app.route("/logout_admin/")
def logout_admin():
    session.pop("e_mail",None)
    flash("feedback","You have logged out")
    return redirect("/admin_login/")