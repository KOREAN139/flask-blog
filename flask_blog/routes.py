#!/usr/bin/python
#-*- coding:utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for
from config import (
		MAIL_SERVER,
		MAIL_PORT,
		MAIL_USE_TLS,
		MAIL_USE_SSL,
		MAIL_USERNAME,
		MAIL_PASSWORD
		)

app = Flask(__name__)

app.config["MAIL_SERVER"] = MAIL_SERVER
app.config["MAIL_PORT"] = MAIL_PORT
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = MAIL_USERNAME
app.config["MAIL_PASSWORD"] = MAIL_PASSWORD

from flask.ext.mail import Mail, Message
mail = Mail(app)
from decorators import async
from operator import itemgetter # for sort list of dictionary
import datetime # for get the current time
import os # for check whether the path exists
import commands # for create directory
import glob # for get filenames

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

def get_all_post_information(post_names):
	ret = []
	for post_name in post_names:
		d = {}
		with open(post_name, 'r') as fp:
			lines = fp.read().strip().split('\n')
		d['post_id'] = post_name.split('/')[-1].split('.')[0]
		d['post_name'] = lines[0]
		d['post_author'] = lines[1]
		d['post_date'] = lines[2]
		d['post_body'] = ''
		for body in lines[3:]:
			d['post_body'] += body
		ret.append(d)
	ret_sorted = sorted(ret, key=itemgetter('post_id'), reverse=True)
	return ret_sorted

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
: blog route
"""

@app.route('/')
def main():
	posts = get_all_posts()
	ret_posts = get_all_post_information(posts)
	return render_template('blog.html',ret_posts=ret_posts)

@app.route('/create_post')
def create_post():
	posts = get_all_posts()
	ret_posts = get_all_post_information(posts)
	return render_template('create_post.html',ret_posts=ret_posts)

@app.route('/save_post',methods=['POST'])
def save_post():
	if request.method == 'POST':
		post_name = request.form['post_name']
		post_author = request.form['post_author']
		post_body = request.form['post_body']
		post_date = datetime.datetime.now()
		post_tag = request.form['post_tag']
		s = '%s\n%s\n%s\n%s'%(post_name,post_author,str(post_date),post_body)
		print post_name, post_author, post_body, post_date
		post_names = get_all_posts()
		last_post_number = get_max_post_number(post_names)
		next_filename = '/var/www/flask_blog/flask_blog/post/%d.post'%(last_post_number+1)
		update_tag(post_tag, last_post_number+1)
		with open(next_filename, 'w') as fp:
			fp.write(s)
		return redirect(url_for('main'))

@app.route('/post/<post_id>')
def post_detail(post_id):
	posts = get_all_posts()
	ret_posts = get_all_post_information(posts)
	ret = {}
	for post in ret_posts:
		if post['post_id'].strip() == post_id.strip():
			ret = post
	return render_template('post.html',ret_posts=ret_posts,post=ret)

if __name__ == '__main__':
	app.run(host='172.31.14.58', debug=True)
