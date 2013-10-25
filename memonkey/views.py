from datetime import datetime

from flask import render_template, flash, redirect
from flask import session, url_for, request, g, jsonify
from flask.ext.login import login_user, logout_user, current_user, login_required

from memonkey import app, db, lm, oid

from config import POSTS_PER_PAGE, MAX_SEARCH_RESULTS
from models import Users, Category, UserForm, PostForm, Post, SearchForm

@lm.user_loader
def load_user(id):
    return Users.query.get(id)

@app.before_request
def before_request():
    g.user = current_user
    g.search_form = SearchForm()

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = UserForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        password = form.password.data
        user = Users.query.filter_by(name=name).first()
        if user is None:
            flash("Invalid login")
        elif user.password != password:
                flash("Invalid password")    
        else:
            login_user(user)
            flash("Logged in successfully.")
            return redirect(request.args.get("next") or url_for("index"))
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/')
@app.route('/index')
@app.route('/index/<int:page>')
def index(page=1):
    posts = Post.query.order_by('pub_date DESC').paginate(page, POSTS_PER_PAGE, False)
    return render_template('index.html', posts=posts)

@app.route('/post/<int:post_id>')
def post(post_id=1):
    post = Post.query.get(post_id)
    return render_template('single_post.html', post=post)

@app.route('/search', methods=['GET', 'POST'])
def search(page = 1):
    form = SearchForm(request.form)
    if request.method == 'POST':
        print form.search.data

    if not form.validate():
        return redirect(url_for('index'))
    return redirect(url_for('search_results', query=form.search.data))


@app.route('/search_results/<query>')
def search_results(query):
    results = Post.query.whoosh_search(query, MAX_SEARCH_RESULTS).all()
    return render_template('search_results.html', query=query, posts=results)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = PostForm(request.form)
    if request.method == 'POST' and form.validate():
        post = Post(form.title.data, form.body.data, datetime.now())
        db.session.add(post)
        tags = [tag.strip() for tag in form.tags.data.split(',')]
        for tag in tags:
            category = Category.query.filter_by(name=tag).first()
            if not category:
                category = Category(tag.strip())
            post.categories.append(category)
        db.session.commit()
        flash("New post has added successfully")
        return redirect(url_for("index"))
    return render_template('add.html', form=form, edit_post=False)

@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit(post_id):
    post = Post.query.get(post_id)
    form = PostForm(request.form, post)
    if request.method == 'POST' and form.validate():
        tag_list = list(post.categories)
        tags = [tag.strip() for tag in form.tags.data.split(',')]
        for tag in tag_list:
            if tag.name in tags:
                tags.remove(tag.name)
            else:
                post.categories.remove(tag)
            
        if tags:
            for tag in tags:
                category = Category.query.filter_by(name=tag).first()
                if not category:
                    category = Category(tag.strip())
                post.categories.append(category)
        
        form.populate_obj(post)
        db.session.commit()
        flash("Post has edited successfully.")
        return redirect(url_for("post", post_id=post_id))
    else:
        tag_list = []
        for tag in post.categories:
            tag_list.append(tag.name)
        tags = ', '.join(tag_list)
        form.tags.data = tags
        
        
    return render_template('add.html', form=form, edit_post=True, post_id=post_id)

@app.route('/delete_post/<int:post_id>')
@login_required
def delete_post(post_id):
    post = Post.query.get(post_id)
    try:
        db.session.delete(post)
        db.session.commit()
        flash("Post has deleted successfully.")
    except:
        flash("Unfortunately post was not removed.")
        
    
    return redirect(url_for("index"))

@app.route('/tag/<tag>')
@app.route('/tag/<tag>/<int:page>')
def by_category(tag, page=1):
    # Display all posts related to given category
    posts = None
    category = Category.query.filter_by(name=tag).first()
    if category:
        posts = category.posts.order_by('pub_date DESC').paginate(page, POSTS_PER_PAGE, False)
    return render_template('by_category.html', tag=tag, posts=posts)

@app.route('/tags')
def all_categories():
    # Show all tags from db
    tags  = Category.query.order_by('name').all()
    return render_template('all_categories.html', tags=tags)

@app.route('/edit_tags')
@login_required
def edit_categories():
    tags  = Category.query.order_by('name').all()
    return render_template('edit_categories.html',
                            tags=tags)

@app.route('/update_tag/<int:tag_id>/<name>', methods = ['POST'])
@login_required
def update_category(tag_id, name):
    tag  = Category.query.get(tag_id)
    tag.name = name
    db.session.commit()
    return jsonify({'result': "OK", "id": tag_id, 'name': name})

@app.route('/delete_tag/<int:tag_id>', methods = ['POST'])
@login_required
def delete_category(tag_id):
    tag  = Category.query.get(tag_id)
    name = tag.name
    db.session.delete(tag)
    db.session.commit()
    return jsonify({'result': "OK", "id": tag_id, 'name': name})

@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500