#!/usr/bin/python
#-*- coding:utf-8 -*-
from flask import (
		Flask,
		render_template,
		request,
		redirect,
		url_for,
		session
		)
from config import (
		MAIL_SERVER,
		MAIL_PORT,
		MAIL_USE_TLS,
		MAIL_USE_SSL,
		MAIL_USERNAME,
		MAIL_PASSWORD
		)
from flask import (
		Flask,
		render_template,
		request,
		redirect,
		url_for,
		session
		)

app = Flask(__name__)

app.config["SECRET_KEY"] = 'SET T0 4NY SECRET KEY L1KE RAND0M H4SH'
app.config["MAIL_SERVER"] = MAIL_SERVER
app.config["MAIL_PORT"] = MAIL_PORT
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = MAIL_USERNAME
app.config["MAIL_PASSWORD"] = MAIL_PASSWORD

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

#from flask.ext.mail import Mail, Message
from flask_mail import Mail, Message
mail = Mail(app)
from decorators import async
from operator import itemgetter # for sort list of dictionary
import datetime # for get the current time
import os # for check whether the path exists
import commands # for create directory
import glob # for get filenames
from werkzeug import generate_password_hash, check_password_hash
import json

def set_password(password):
	return generate_password_hash(password)

def check_password(password, cur_password):
	return check_password_hash(password, cur_password)

@async
def send_async_email(app, msg):
	with app.app_context():
		mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
	msg = Message(subject, sender=sender, recipients=recipients)
	msg.body = text_body
	msg.html = html_body
	send_async_email(app,msg)

@app.route('/lend')
def lend():
	return render_template('lend_main.html')

@app.route('/lend/contact_mail',methods=['GET','POST'])
def contact_mail():
	if request.method == 'GET':
		return render_template('sub_main.html')
	elif request.method == 'POST':
		name = request.form['name']
		email = request.form['email']
		comments = request.form['comments']
		send_email(u'공학부 & 자연과학부 대여사업 건의사항 접수',
					MAIL_USERNAME, 
					['korean139@gmail.com'], 
					u'반갑습니다 바디입니다', 
					u'%s님께서 (%s) [ %s ] 의 내용을 보내셨습니다.'%(name, email, comments))
		send_email(u'공학부 & 자연과학부 대여사업 건의사항 접수 완료 안내',
					MAIL_USERNAME,
					[email],
					u'반갑습니다 바디입니다',
					u'%s님께서 보내신 건의는 정상적으로 접수되었습니다. 더욱 노력하는 학생회가 되겠습니다. 감사합니다.'%(name))
		return redirect(url_for('lend'))

"""
: blog util function
"""

def createDirectory(directoryName):
	if not os.path.exists(directoryName):
		command = 'mkdir %s'%directoryName
		ret = commands.getoutput(command)
		command = 'chmod 777 %s'%directoryName
		ret = commands.getoutput(command)

def get_max_post_number(filenames):
	ret = 0
	for filename in filenames:
		only_filename = filename.split('/')[-1]
		only_number = int(only_filename.split('.')[0])
		ret = max(ret, only_number)
	return ret

def get_all_posts():
	createDirectory('/var/www/flask_blog/flask_blog/post/')
	filenames = glob.glob('/var/www/flask_blog/flask_blog/post/*.post')
	return filenames

def get_all_tags():
	with open('/var/www/flask_blog/flask_blog/post/tag','r') as fp:
		lines = fp.read().strip().split('\n')
	d = {}
	for line in lines:
		if len(line) == 0:
			continue
		tag = line.split()[0]
		post_id = str(line.split()[1])
		if post_id in d:
			d[post_id].append(tag)
		else:
			d[post_id] = [tag]
	return d

def get_all_post_information(post_names):
    tags = get_all_tags()
    comments = get_all_comments()
    users = get_all_users()

    ret = []
    for post_name in post_names:
        d = {}
        with open(post_name,'r') as fp:
            lines = fp.read().strip().split('\n')
        post_id = post_name.split('/')[-1].split('.')[0]
        d['post_id'] = post_id
        d['post_name'] = lines[0]
        d['post_author'] = lines[1]
        d['post_date'] = lines[2]
        d['post_body'] = ''
        for body in lines[3:]:
            d['post_body'] += body+'\n'
        if post_id in tags:
            d['post_tags'] = tags[post_id]
        else:
            d['post_tags'] = []
        d['post_comments'] = []
        if post_id in comments:
            d['post_comments'] = comments[post_id]
        else:
            d['post_comments'] = []
        if 'logged_in' in session:
            d['post_liked'] = get_already_like(session['user_id'],post_id)

        ret.append(d)
    ret = sorted(ret, key=lambda k: int(k['post_id']), reverse=True)
    return ret


"""
def update_tag(post_tag, post_id):
	filename = "/var/www/flask_blog/flask_blog/post/tag"
	new_tags = post_tag.strip().split('#')[1:]
	if not new_tags:
		return
	new_len = len(new_tags)
	s = ''
	old_tags = []
	curr_id = str(post_id)
	itr = 0
	new_tags.sort()
	if os.path.isfile(filename):
		with open(filename, 'r') as fp:
			old_tags = fp.read().strip().split('\n')
	if old_tags:
		for tag in old_tags:
			while itr < new_len and tag.split()[0] > new_tags[itr].strip():
				s = s + new_tags[itr].strip() + ' ' + curr_id + '\n'
				itr += 1
			if itr < new_len and tag.split()[0] == new_tags[itr].strip():
				s = s + tag + ' ' + curr_id + '\n'
				itr += 1
			else:
				s = s + tag + '\n'
	while itr < new_len:
		s = s + new_tags[itr].strip() + ' ' + curr_id + '\n'
		itr += 1
	with open(filename, 'w') as fp:
		fp.write(s)
	return
"""

def get_all_comments():
	with open('/var/www/flask_blog/flask_blog/post/comment','r') as fp:
		lines = fp.read().strip().split('\n')
	d = {}
	for line in lines:
		if len(line.strip()) == 0:
			continue
		l = line.split()
		comment_body = l[0].strip()
		user_id = l[1].strip()
		post_id = l[2].strip()
		created_at = l[3].strip()
		if post_id in d:
			d[post_id].append({
				'comment_body': comment_body,
				'user_id': user_id,
				'post_id': post_id,
				'created_at': created_at,
				})
		else :
			d[post_id] = [{
				'comment_body': comment_body,
				'user_id': user_id,
				'post_id': post_id,
				'created_at': created_at,
				}]
	return d

def get_all_users():
	with open('/var/www/flask_blog/flask_blog/post/user','r') as fp:
		lines = fp.read().strip().split('\n')
	d = {}
	for line in lines:
		if len(line.strip()) == 0:
			continue
		l = line.split()
		user_id = l[0].strip()
		user_name = l[1].strip()
		user_password = l[2].strip()
		user_created_at = l[3].strip()
		d[user_id] = {
                'user_id': user_id,
                'username': user_name,
                'password': user_password,
                'created_at': user_created_at
                }
	return d

def get_all_like():
    with open('/var/www/flask_blog/flask_blog/post/like','r') as fp:
        lines = fp.read().strip().split('\n')
    l = []
    for line in lines:
        if len(line) == 0 :
            continue
        cur = line.split()
        user_id = cur[0].strip()
        post_id = cur[1].strip()
        l.append({
            'user_id': user_id,
            'post_id': post_id
            })
    return l

def get_already_like(user_id,post_id):
    likes = get_all_like()
    for like in likes:
        if str(user_id) == str(like['user_id']) and str(post_id) == str(like['post_id']):
            return True
    return False

"""
: blog route
"""

@app.route('/')
def main():
	posts = get_all_posts()
	ret_posts = get_all_post_information(posts)
	if not 'logged_in' in session:
		return render_template('signup.html',ret_posts=ret_posts)
	return render_template('blog.html',ret_posts=ret_posts)

@app.route('/create_post')
def create_post():
	posts = get_all_posts()
	ret_posts = get_all_post_information(posts)
	if not 'logged_in' in session:
		return render_template('signup.html',ret_posts=ret_posts)
	return render_template('create_post.html',ret_posts=ret_posts)

@app.route('/save_post',methods=['POST'])
def save_post():
	if request.method == 'POST':
		post_name = request.form['post_name']
		post_author = request.form['post_author']
		post_body = request.form['post_body']
		post_date = datetime.datetime.now()
		s = '%s\n%s\n%s\n%s'%(post_name,post_author,str(post_date),post_body)
		print post_name, post_author, post_body, post_date
		post_names = get_all_posts()
		last_post_number = get_max_post_number(post_names)
		post_id = last_post_number + 1
		next_filename = '/var/www/flask_blog/flask_blog/post/%d.post'%(post_id)
#		update_tag(post_tag, last_post_number+1)
		with open(next_filename, 'w') as fp:
			fp.write(s)
		post_tags = request.form['tags'].split('#')
		if not os.path.exists('/var/www/flask_blog/flask_blog/post/tag'):
			commands.getoutput('touch /var/www/flask_blog/flask_blog/post/tag')
		with open('/var/www/flask_blog/flask_blog/post/tag', 'a') as fp:
			for post_tag in post_tags:
				cur_tag = post_tag.strip()
				if len(cur_tag) == 0:
					continue
				fp.write(cur_tag+' '+str(post_id)+'\n')
		return redirect(url_for('main'))

@app.route('/<post_id>/save_comment',methods=['POST'])
def save_comment(post_id):
	if request.method == 'POST':
		comment_body = request.form['comment_body']
		if len(comment_body.strip()) == 0:
			return redirect('/post/%s'%post_id)
		user_id = session['user_id']
		created_at = datetime.datetime.now()
		s = '%s %s %d %s\n'%(comment_body, user_id, int(post_id), str(created_at).split()[0])

		base_path = '/var/www/flask_blog/flask_blog/post/'
		comment_path = base_path + 'comment'
		with open(comment_path, 'a') as fp:
			fp.write(s)
		return redirect('/post/%s'%post_id)

def get_user_with_id(user_id):
    users = get_all_users()
    if not user_id in users:
        return {}
    return users[user_id]

def get_user_with_username(username):
    users = get_all_users()
    for key in users:
        user = users[key]
        if user['username'] == username:
            return user
    return {}

@app.route('/post/<post_id>')
def post_detail(post_id):
	posts = get_all_posts()
	ret_posts = get_all_post_information(posts)
	if not 'logged_in' in session:
		return render_template('signup.html',ret_posts=ret_posts)
	ret = {}
	for post in ret_posts:
		if post['post_id'].strip() == post_id.strip():
			ret = post
	return render_template('post.html',ret_posts=ret_posts,post=ret)

@app.route('/save_user',methods=['POST'])
def save_user():
    users = get_all_users()
    if request.method == 'POST':
        next_user_id = len(users) + 1
        username = request.form['username']
        password = request.form['password']
        input_password = password
        password = set_password(password)
        found_user = get_user_with_username(username)
        if len(found_user) != 0:
            ans_password = found_user['password']
            if check_password_hash(ans_password, input_password):
                session['logged_in'] = True
                session['user_id'] = str(next_user_id)
                session['username'] = username
                return redirect('/')
            else :
                posts = get_all_posts()
                ret_posts = get_all_post_information(posts)
                return render_template('/signup.html',ret_posts=ret_posts,error_message=u'비밀번호가 틀리셨어요!')

        created_at = datetime.datetime.now()
        s = '%d %s %s %s\n'%(next_user_id,username,password,str(created_at))
        base_path = '/var/www/flask_blog/flask_blog/post/'
        user_path = base_path + 'user'
        with open(user_path,'a') as fp:
            fp.write(s)
        session['logged_in'] = True
        session['user_id'] = str(next_user_id)
        session['username'] = username

        return redirect('/')

@app.route('/login')
def login():
    posts = get_all_posts()
    ret_posts = get_all_post_information(posts)
    return render_template('/signup.html',ret_posts=ret_posts)

@app.route('/logout')
def logout():
    if 'logged_in' not in session:
        return redirect('/')
    session.pop('username', None)
    session.pop('logged_in', None)
    session.pop('user_id', None)
    return redirect('/')

@app.route('/user_like_post/<post_id>',methods=['POST'])
def user_like_post(post_id):
    if not 'user_id' in session:
        return json.dumps({'status':'error','message':u'user_id not exists'})
    user_id = session['user_id']
    likes = get_all_like()
    if get_already_like(str(user_id),str(post_id)):
        with open('/var/www/flask_blog/flask_blog/post/like','w') as fp:
            for like in likes:
                if str(user_id) == str(like['user_id']) and str(post_id) == str(like['post_id']):
                    continue
                fp.write('%s %s\n'%(str(like['user_id']),str(like['post_id'])))
        return json.dumps({'status':'OK','message':u'remove','is_liked':False})
    with open('/var/www/flask_blog/flask_blog/post/like','a') as fp:
        fp.write('%s %s\n'%(str(user_id),str(post_id)))
    return json.dumps({'status':'OK','message':u'success','is_liked':True})

if __name__ == '__main__':
	app.run(host='172.31.14.58', debug=True)
