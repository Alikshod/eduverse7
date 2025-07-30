from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional
from flask_wtf.file import FileField, FileAllowed
from wtforms import TextAreaField, SubmitField

class RegisterForm(FlaskForm):
    name = StringField('Nama Lengkap', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(), Length(min=6)])
    confirm = PasswordField('Ulangi Password', validators=[
        DataRequired(), EqualTo('password')])
    submit = SubmitField('Daftar')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Masuk')

class UploadForm(FlaskForm):
    title = StringField('Judul Materi', validators=[DataRequired()])
    description = TextAreaField('Deskripsi', validators=[DataRequired()])
    file = FileField('Unggah File (PDF)', validators=[FileAllowed(['pdf'], 'PDF saja!')])
    submit = SubmitField('Unggah')

class AdminUserForm(FlaskForm):
    name = StringField('Nama', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password (opsional)', validators=[Optional()])
    role = SelectField('Role', choices=[('user', 'User'), ('admin', 'Admin')], validators=[DataRequired()])
    submit = SubmitField('Simpan')

class CommentForm(FlaskForm):
    content = TextAreaField('Komentar', validators=[DataRequired()])
    submit = SubmitField('Kirim')