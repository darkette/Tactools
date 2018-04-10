from flask import Flask, render_template, flash, request, redirect
from wtforms import Form, TextField, TextAreaField, validators, StringField,\
     SubmitField
import decode
import logging
from logging.handlers import RotatingFileHandler
# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'


class decoder(Form):
    stack = TextField('Stack:', validators=[validators.required()])
    c_version = TextField('Code Version:', validators=[validators.required(),
                                                   validators.Length(min=6,
                                                                     max=35)])


@app.route("/", methods=['GET', 'POST'])
def stack_decode():
    form = decoder(request.form)
    # print(form.errors)
    if request.method == 'POST':
        stack = request.form['stack']
        mapfile = request.form['mapfile']
        c_version = request.form['c_version']
        if form.validate():
            flash('Okay now will decode')
            d_result = decode.decode_corefile(mapfile, stack)
            print("Result is ", d_result)
            return render_template('results.html', result=d_result)
        else:
            flash('Error: All the form fields are required. ')
            return redirect('/')
    return render_template('stack_decode.html', form=form)

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
    app.run(host='0.0.0.0')
