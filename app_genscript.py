from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename
from werkzeug.datastructures import CombinedMultiDict
from wtforms import Form, TextField, SelectField, TextAreaField, validators, StringField,\
     SubmitField, RadioField
import decode_text
import logging
from local_defs import mydefs
import os
import time
from logging.handlers import RotatingFileHandler
# App config.
baseurl2 = 'doc.darkphoenix.net:5555'
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
app.config['UPLOAD_FOLDER'] = mydefs.UPLOAD_FOLDER


class text_decoder(Form):
    mapFile_1 = SelectField(u'Code Type', choices=mydefs.IMAGE_TYPE)
    mapFile_2 = SelectField(u'Version', choices=mydefs.RELEASE)
    mapFile_3 = SelectField(u'Version', choices=mydefs.PATCH_LETTER)
    mapFile_4 = SelectField(u'Version', choices=mydefs.PATCH_SPECIAL)
    # mapfile = TextField('Mapfile:', validators=[validators.required()])
    file = FileField('File:')


class text_decoder_nofile(Form):
    mapFile_1 = SelectField(u'Code Type', choices=mydefs.IMAGE_TYPE)
    mapFile_2 = SelectField(u'Version', choices=mydefs.RELEASE)
    mapFile_3 = SelectField(u'Version', choices=mydefs.PATCH_LETTER)
    mapFile_4 = SelectField(u'Version', choices=mydefs.PATCH_SPECIAL)
    stack_output = TextAreaField('stack_output', validators=[validators.Required()])

class gen_script(Form):
    # script_lan = SelectField(u'Script Language', choices=mydefs.SCRIPT_LANGUAGES)
    target_ip = TextField('Target IP', validators=[validators.Required()])
    access_type = RadioField('Access Type:', choices=[('ssh', 'ssh'),\
                        ('telnet','telnet')])
    authen_t = RadioField('Authentication:',choices=[\
    ('implicit','implicit'),('UserEnable','UserEnable'),\
    ('NoneEnable','NoneEnable'),('None','None')])
    command_trig = TextField('Trigger Command: ', validators=[validators.Required()])
    trig_type = RadioField('Trigger Type: ', choices=[\
    ('Text Pattern','Text Pattern'),('Conditional','Conditional')])
    trig_value = TextField('Trigger Value:')

@app.route("/", methods=['GET', 'POST'])
def base_page():
    return render_template('base.html')


@app.route("/text_decode", methods=['GET', 'POST'])
def text_decode():
    form = text_decoder(request.form)
    # print(form.errors)
    if request.method == 'POST':
        print('Got here 1')
        f = request.files['file']
        print('f is ', f)
        filename = secure_filename(f.filename)
        print('Got here 2')
        fs = f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        stackfile = mydefs.UPLOAD_FOLDER + '/' + filename
        mapfile = mydefs.MAP_ROOT + request.form['mapFile_2'] +\
                   '/LATEST_BUILD/dist' + request.form['mapFile_1'] +\
                   'prod.map'
        map_timestamp = time.ctime(os.path.getmtime(mapfile))
        temp_mappath =  request.form['mapFile_2'] +\
                   '/LATEST_BUILD/dist' + request.form['mapFile_1'] +\
                   'prod.map'
        print('Got here 3')
        print('Got here 3.5')
        print('Form Validation ', form.validate())
        print('Form errors ', form.errors)
        print('filename is ', filename)
        print('fs is', fs)
        print('stackfile is', stackfile)
        print('mapfile is', mapfile)
        if form.validate():
            flash('Okay now will decode')
            print('Got here 4')
            d_result = decode_text.decode_t(mapfile, stackfile, '1',\
                                            map_timestamp, temp_mappath)
            print("Result is ", d_result)
            return render_template('results.html', result=d_result)
        else:
            flash('Error: All the form fields are required. ')
            return redirect('/text_decode')
    return render_template('t_decode.html', form=form)

@app.route("/text_decode_nofile", methods=['GET', 'POST'])
def text_decode_nofile():
    form = text_decoder_nofile(request.form)

    print(form.errors)
    if request.method == 'POST':
        print('Got here 1')

        print('Got here 2')
        stack_output = request.form['stack_output']
        if request.form['mapFile_3'] is 'UNDEFINED':
            MAP_LETTER = request.form['mapFile_4']
        else:
            MAP_LETTER = request.form['mapFile_3']

        mapfile = mydefs.MAP_ROOT + request.form['mapFile_2'] + MAP_LETTER +\
                   '/LATEST_BUILD/dist' + request.form['mapFile_1'] +\
                   'prod.map'
        map_timestamp = time.ctime(os.path.getmtime(mapfile))
        temp_mappath =  request.form['mapFile_2'] +\
                   '/LATEST_BUILD/dist' + request.form['mapFile_1'] +\
                   'prod.map'
        print('timestamp is ',map_timestamp)
        print('mypath is', temp_mappath)
        print('Got here 3')
        print('Got here 3.5')
        print('Form Validation ', form.validate())
        print('Form errors ', form.errors)
        print('mapfile is', mapfile)
        if form.validate():
            flash('Okay now will decode')
            print('Got here 4')
            d_result = decode_text.decode_t(mapfile, stack_output, 0,\
                                            map_timestamp, temp_mappath)
            print("Result is ", d_result)
            return render_template('results.html', result=d_result)
        else:
            flash('Error: All the form fields are required. ')
            return redirect('/text_decode_nofile')
    return render_template('t_decode_nofile.html', form=form)

@app.route("/icx_decoder", methods=['GET', 'POST'])
def stack_decodenew():
    form = text_decoder(CombinedMultiDict((request.form, request.files)))
    # print(form.errors)
    if request.method == 'POST':
        print('Got here 1')
        f = request.files['file']
        print('f is ', f)
        filename = secure_filename(f.filename)
        print('Got here 2')
        fs = f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        stackfile = mydefs.UPLOAD_FOLDER + '/' + filename
        print('Got here 3')
        if request.form['mapFile_3'] is 'UNDEFINED':
            MAP_LETTER = request.form['mapFile_4']
        else:
            MAP_LETTER = request.form['mapFile_3']

        mapfile = mydefs.MAP_ROOT + request.form['mapFile_2'] + MAP_LETTER +\
                   '/LATEST_BUILD/dist' + request.form['mapFile_1'] +\
                   'prod.map'
        if not os.path.isfile(mapfile):
            flash('Sorry this code image is not supported yet!')
            return redirect('/icx_decoder')

        map_timestamp = time.ctime(os.path.getmtime(mapfile))
        temp_mappath =  request.form['mapFile_2'] +\
                   '/LATEST_BUILD/dist' + request.form['mapFile_1'] +\
                   'prod.map'
        print('Got here 3.5')
        print('Form Validation ', form.validate())
        print('Form errors ', form.errors)
        print('filename is ', filename)
        print('fs is', fs)
        print('stackfile is', stackfile)
        print('mapfile is', mapfile)
        if form.validate():
            flash('Okay now will decode')
            print('Got here 4')
            d_result = decode_text.decode_corefile(mapfile, stackfile,\
                                                   map_timestamp, temp_mappath)
            print("Result is ", d_result)
            return render_template('results.html', result=d_result)
        else:
            flash('Error: All the form fields are required. ')
            return redirect('/icx_decoder')
    return render_template('stack_decodenew.html', form=form)

@app.route('/result', methods=['GET', 'POST'])
def result():
    if request.method == 'POST':
        result = request.form
        return render_template('results.html', result=d_result)
    else:
        return redirect('/')


if __name__ == "__main__":
    handler = RotatingFileHandler('web.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run(host='0.0.0.0', port=5555)
