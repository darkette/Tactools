from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename
from werkzeug.datastructures import CombinedMultiDict
from wtforms import Form, TextField, SelectField, TextAreaField, validators, StringField,\
     SubmitField
import decode_text
import logging
from local_defs import mydefs
import os
import time
from logging.handlers import RotatingFileHandler
import form_classes
# App config.
DEBUG = True
baseurl = 'd7d445ee'
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
app.config['UPLOAD_FOLDER'] = mydefs.UPLOAD_FOLDER

@app.route("/", methods=['GET', 'POST'])
def base_page():
    return render_template('base_ngrok.html', baseurl=baseurl)

@app.route("/scriptgen", methods=['GET','POST'])
def script_gen():
    form = form_classes.gen_script(request.form)
    print('Form is: ', form)
    if request.method == 'POST':
        print('script 1')
        return render_template('results.html', form=form)
    return render_template('scriptgen_temp.html', form=form)

@app.route('/scriptgen_result', methods=['GET', 'POST'])
def s_result():
    if request.method == 'POST':
        result = request.form
        return render_template('results.html', form=form)
    else:
        return redirect('/')


@app.route("/<my_url>", methods=['GET', 'POST'])
def gen_decode(my_url):
    if my_url == 'text_decode':
        form = form_classes.text_decoder(request.form)
        my_template = 't_decode_ngrok.html'
    elif my_url == 'text_decode_nofile':
        form = form_classes.text_decoder_nofile(request.form)
        my_template = 't_decode_nofile_ngrok.html'
    # elif my_url == '':
    elif my_url == 'gdb_decoder':
        form = form_classes.text_decoder(CombinedMultiDict((request.form, request.files)))
        my_template = 'gdb_decoder_ngrok.html'
    else:
        my_url == 'icx_decoder'
        form = form_classes.text_decoder(CombinedMultiDict((request.form, request.files)))
        my_template = 'stack_decodenew_ngrok.html'
    # else:
    if request.method == 'POST':
        if my_url == 'text_decode':
            f = request.files['file']
            filename = secure_filename(f.filename)
            fs = f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            stackfile = mydefs.UPLOAD_FOLDER + '/' + filename
        elif my_url == 'text_decode_nofile':
            stack_output = request.form['stack_output']
            stack_output = stack_output.lower()
        else:
            my_url == 'icx_decoder'
            f = request.files['file']
            filename = secure_filename(f.filename)
            fs = f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            stackfile = mydefs.UPLOAD_FOLDER + '/' + filename
            # plat_override = request.form['plat_override']
        # elif my_url == '':
        # else:
        if request.form['mapFile_3'] == 'UNDEFINED':
            MAP_LETTER = request.form['mapFile_4']
        else:
            MAP_LETTER = request.form['mapFile_3']

        code_dir = mydefs.MAP_ROOT + request.form['mapFile_2'] + MAP_LETTER +\
        '/LATEST_BUILD/dist' + request.form['mapFile_1']
        mapfile = code_dir + 'prod.map'
        gdb_path = code_dir + 'bin/FastIron.debug'
        print('mapfile: ', mapfile)
        if not os.path.isfile(mapfile):
            flash('Sorry this code image is not supported yet!')
            return redirect('/' + my_url)
        map_timestamp = time.ctime(os.path.getmtime(mapfile))
        if my_url == 'gdb_decoder':
            temp_mappath =  request.form['mapFile_2'] + MAP_LETTER +\
                   '/LATEST_BUILD/dist' + request.form['mapFile_1'] +\
                   'bin/FastIron.debug'
        else:
            temp_mappath =  request.form['mapFile_2'] + MAP_LETTER +\
                   '/LATEST_BUILD/dist' + request.form['mapFile_1'] +\
                   'prod.map'
        if form.validate():
            flash('Okay now will decode')
            if request.form['do_jira'] == 'on':
                is_j = 1
            else:
                is_j = 0
            # Need to  account for FCX/SX/6610 different Information
            if 'FX' in mapfile:
                is_fx = 1
            else:
                is_fx = 0
            if my_url == 'text_decode':
                d_result = decode_text.decode_t(mapfile, stackfile, 1, map_timestamp, temp_mappath, is_fx, is_j)
            elif my_url == 'text_decode_nofile':
                d_result = decode_text.decode_t(mapfile, stack_output, 0, map_timestamp, temp_mappath, is_fx, is_j)
            elif my_url == 'gdb_decoder':
                print('The new way')
                im_type = request.form['mapFile_1']
                d_result = decode_text.decode_gdb(gdb_path, stackfile, map_timestamp, temp_mappath, im_type, is_j)
                return render_template('results.html', result=d_result)
            else:
                my_url == 'icx_decoder'
                d_result = decode_text.decode_corefile(mapfile, stackfile, map_timestamp, temp_mappath, is_fx, is_j)
            # elif my_url == '':
            # else:
            return render_template('results.html', result=d_result)

        else:
           flash('Error: All the form fields are required. ')
           return redirect('/' + my_url)
    return render_template(my_template, form=form, baseurl=baseurl)

@app.route('/result', methods=['GET', 'POST'])
def result():
    if request.method == 'POST':
        print('Resultform')
        result = request.form
        return render_template('results.html', result=d_result)
    else:
        return redirect('/')


if __name__ == "__main__":
    handler = RotatingFileHandler('web.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run(host='0.0.0.0', port=6000)
