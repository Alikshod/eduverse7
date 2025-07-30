from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import render_template, redirect, url_for, flash, request
from app.forms import RegisterForm, LoginForm
from app.forms import AdminUserForm
from app.models import Material, Comment
from app.forms import CommentForm

from app import db
from app.forms import RegisterForm, LoginForm
from app.models import User
from app.decorators import admin_required
from werkzeug.utils import secure_filename
from app.forms import UploadForm
from datetime import datetime
from app.models import Material
import os

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data)
        user = User(name=form.name.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Pendaftaran berhasil. Silakan login.')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Login berhasil', 'success')

            # ⬇️ Arahkan ke dashboard sesuai peran
            if user.role == 'admin':
                return redirect(url_for('main.admin_dashboard'))
            else:
                return redirect(url_for('main.user_dashboard'))

        flash('Email atau password salah', 'danger')
    return render_template('login.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Berhasil logout.')
    return redirect(url_for('main.login'))

@main.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return render_template('dashboard_admin.html', user=current_user)
    return render_template('dashboard_user.html', user=current_user.name)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'app', 'static', 'uploads')

@main.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        new_material = Material(
            title=form.title.data,
            description=form.description.data,
            filename=filename,
            uploader_id=current_user.id
        )
        db.session.add(new_material)
        db.session.commit()
        flash("Materi berhasil diunggah, menunggu persetujuan admin.", "success")
        return redirect(url_for('main.dashboard'))

    return render_template('upload.html', form=form)

@main.route('/dashboard/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        abort(403)
    return render_template('dashboard_admin.html')

@main.route('/dashboard/user')
@login_required
def user_dashboard():
    return render_template('dashboard_user.html')
    approved_materials = Material.query.filter_by(approved=True).all()
    return render_template('user_dashboard.html', materials=approved_materials)
    

@main.route('/materials/pending')
@login_required
def pending_materials():
    if current_user.role != 'admin':
        abort(403)

    materials = Material.query.filter_by(approved=False).all()
    return render_template('pending_materials.html', materials=materials)

@main.route('/materials/approve/<int:material_id>')
@login_required
def approve_material(material_id):
    if current_user.role != 'admin':
        abort(403)

    material = Material.query.get_or_404(material_id)
    material.approved = True
    db.session.commit()
    flash("Materi telah disetujui.", "success")
    return redirect(url_for('main.pending_materials'))

@main.route('/materials/reject/<int:material_id>')
@login_required
def reject_material(material_id):
    if current_user.role != 'admin':
        abort(403)

    material = Material.query.get_or_404(material_id)
    db.session.delete(material)
    db.session.commit()
    flash("Materi ditolak dan dihapus.", "warning")
    return redirect(url_for('main.pending_materials'))

@main.route('/admin/users')
@login_required
def manage_users():
    if current_user.role != 'admin':
        abort(403)
    
    users = User.query.all()
    return render_template('manage_users.html', users=users)

@main.route('/admin/users/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.role != 'admin':
        abort(403)
    
    form = AdminUserForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data) if form.password.data else None
        user = User(
            name=form.name.data,
            email=form.email.data,
            role=form.role.data,
            password=hashed_pw if hashed_pw else generate_password_hash("default123")
        )
        db.session.add(user)
        db.session.commit()
        flash("Pengguna berhasil ditambahkan.", "success")
        return redirect(url_for('main.manage_users'))
    
    return render_template('admin_add_user.html', form=form)

@main.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if current_user.role != 'admin':
        abort(403)
    
    user = User.query.get_or_404(user_id)
    form = AdminUserForm(obj=user)

    if form.validate_on_submit():
        user.name = form.name.data
        user.email = form.email.data
        user.role = form.role.data
        if form.password.data:
            user.password = generate_password_hash(form.password.data)
        db.session.commit()
        flash("Pengguna berhasil diperbarui.", "success")
        return redirect(url_for('main.manage_users'))
    
    return render_template('admin_edit_user.html', form=form, user=user)

@main.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        abort(403)

    user = User.query.get_or_404(user_id)

    # Jangan izinkan admin menghapus dirinya sendiri
    if user.id == current_user.id:
        flash("Anda tidak dapat menghapus akun Anda sendiri.", "warning")
        return redirect(url_for('main.manage_users'))

    db.session.delete(user)
    db.session.commit()
    flash(f"Pengguna {user.name} berhasil dihapus.", "success")
    return redirect(url_for('main.manage_users'))

@main.route('/materials')
def materials():
    approved_materials = Material.query.filter_by(approved=True).all()
    return render_template('materials.html', materials=approved_materials)

@main.route('/material/<int:material_id>', methods=['GET', 'POST'])
def material_detail(material_id):
    material = Material.query.get_or_404(material_id)
    comments = Comment.query.filter_by(material_id=material.id).order_by(Comment.timestamp.desc()).all()
    
    form = CommentForm()
    if form.validate_on_submit():
        new_comment = Comment(
            content=form.content.data,
            user_id=current_user.id,
            material_id=material.id,
            timestamp=datetime.utcnow()
        )
        db.session.add(new_comment)
        db.session.commit()
        flash('Komentar berhasil ditambahkan.')
        return redirect(url_for('main.material_detail', material_id=material.id))

    return render_template('material_detail.html', material=material, comments=comments, form=form)

# Edit materi
@main.route('/materials/edit/<int:material_id>', methods=['GET', 'POST'])
@login_required
def edit_material(material_id):
    if current_user.role != 'admin':
        abort(403)

    material = Material.query.get_or_404(material_id)
    form = UploadForm(obj=material)

    if form.validate_on_submit():
        material.title = form.title.data
        material.description = form.description.data
        db.session.commit()
        flash('Materi berhasil diperbarui.', 'success')
        return redirect(url_for('main.materials'))

    return render_template('edit_material.html', form=form, material=material)


# Hapus materi
@main.route('/materials/delete/<int:material_id>', methods=['POST'])
@login_required
def delete_material(material_id):
    if current_user.role != 'admin':
        abort(403)

    material = Material.query.get_or_404(material_id)
    db.session.delete(material)
    db.session.commit()
    flash('Materi berhasil dihapus.', 'danger')
    return redirect(url_for('main.materials'))
