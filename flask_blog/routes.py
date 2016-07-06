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

if __name__ == '__main__':
	app.run(host='172.31.14.58', debug=True)
