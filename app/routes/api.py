from flask import Blueprint, request, jsonify, session
from app.models import User, Comment, Vote, Post
from app.db import get_db
import sys
from app.utils.auth import login_required

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/users', methods=['POST'])
def signup():
  data = request.get_json()
  db = get_db()

  try:
    # attempt creating a new user
    newUser = User(
      username = data['username'],
      email = data['email'],
      password = data['password']
    )

    db.add(newUser)
    db.commit()
  except:
    
    print(sys.exc_info()[0])
    # insert failed, so send error to front end
    db.rollback()
    return jsonify(message = 'Signup failed'), 500

  session.clear()
  session['user_id'] = newUser.id
  session['loggedIn'] = True

  return jsonify(id = newUser.id)

@bp.route('/users/login', methods=['POST'])
def login():
  data = request.get_json()
  db = get_db()

  try:
    user = db.query(User).filter(User.email == data['email']).one()
  except:
    print(sys.exc_info()[0])
  
  if user.verify_password(data['password']) == False:
    return jsonify(message = 'Incorrect credentials'), 400

  session.clear()
  session['user_id'] = user.id
  session['loggedIn'] = True

  return jsonify(id = user.id)

@bp.route('/users/logout', methods=['POST'])
def logout():
  # remove session variables
  session.clear()
  return '', 204

@bp.route('/comments', methods=['POST'])
@login_required
def comment():
  data = request.get_json()
  db = get_db()

  try:
    newComment = Comment(
      comment_text = data['comment_text'],
      user_id = session.get('user_id'),
      post_id = data['post_id']
    )

    db.add(newComment)
    db.commit()

  except:
    print(sys.exc_info()[0])
    db.rollback()

    return jsonify(message = 'Comment failed'), 500
  
  return jsonify(id = newComment.id)

@bp.route('/posts', methods=['POST'])
@login_required
def create():
  data = request.get_json()
  db = get_db()

  try:
    newPost = Post(
      user_id = session.get('user_id'),
      title = data['title'],
      post_url = data['post_url'],      
    )

    db.add(newPost)
    db.commit()

  except:
    print(sys.exc_info()[0])
    db.rollback()

    return jsonify(message = 'Post failed'), 500
  
  return jsonify(id = newPost.id)


@bp.route('/posts/upvote', methods=['PUT'])
@login_required
def upVote():
  data = request.get_json()
  db = get_db()

  try:
    newVote = Vote(
      user_id = session.get('user_id'),
      post_id = data['post_id']
    )

    db.add(newVote)
    db.commit()

  except:
    print(sys.exc_info()[0])
    db.rollback()

    return jsonify(message = 'Vote failed'), 500
  
  return jsonify(id = newVote.id)

@bp.route('/posts/<id>', methods=['PUT'])
@login_required
def update(id):
  data = request.get_json()
  db = get_db()

  try:
    post = db.query(Post).filter(Post.id == id).one()
    post.title = data['title']
    db.commit()
    
  except:
    print(sys.exc_info()[0])
    db.rollback()
    return jsonify(message = 'Post not found'), 404
  
  return '', 204

@bp.route('/posts/<id>', methods=['DELETE'])
@login_required
def delete(id):
  db = get_db()

  try:
    # delete post from db
    db.delete(db.query(Post).filter(Post.id == id).one())
    db.commit()
  except:
    print(sys.exc_info()[0])

    db.rollback()
    return jsonify(message = 'Post not found'), 404

  return '', 204