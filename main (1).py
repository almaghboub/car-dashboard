from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import pandas as pd
import os
from werkzeug.utils import secure_filename
from my_settings import APP_SETTINGS, DATABASE_SETTINGS, MESSAGES, get_setting, get_message

app = Flask(__name__)
app.secret_key = 'car_management_system_secret_key_2024_permanent_production_ready'
app.config['UPLOAD_FOLDER'] = APP_SETTINGS['upload_folder']
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour session timeout

# Allowed image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Make get_setting function available in templates
@app.context_processor
def inject_settings():
    return dict(get_setting=get_setting, get_message=get_message, APP_SETTINGS=APP_SETTINGS, DESIGN_SETTINGS=DATABASE_SETTINGS)

def load_data():
    # Check if Excel file exists, if not create it from CSV
    if os.path.exists('database.xlsx'):
        try:
            return pd.read_excel('database.xlsx', dtype=str)
        except Exception as e:
            print(f"Error reading Excel file: {e}")
            # If file is corrupted, remove it and create new one
            os.remove('database.xlsx')

    if os.path.exists('database.csv'):
        # Convert CSV to Excel for first time
        df = pd.read_csv('database.csv', dtype=str)
        df.to_excel('database.xlsx', index=False)
        return df
    else:
        # Create DataFrame with columns and sample data
        columns = ['الاسم', 'الرقم الخاص', 'شحن الخارجي', 'التاريخ', 'شحن الداخلي', 
                  'VIN', 'اللوت', 'رقم الهيكل', 'سنة الصنع', 'الباقي', 'المجموع', 
                  'رقم الحاوية', 'العمولة', 'قيمة الشراء', 'صورة السيارة']

        # Create sample data
        sample_data = {
            'الاسم': ['أحمد محمد', 'فاطمة أحمد'],
            'الرقم الخاص': ['123', '456'],
            'شحن الخارجي': ['1500', '1200'],
            'التاريخ': ['2024-01-15', '2024-01-20'],
            'شحن الداخلي': ['300', '250'],
            'VIN': ['1HGBH41JXMN109186', '2HGBH41JXMN109187'],
            'اللوت': ['LOT001', 'LOT002'],
            'رقم الهيكل': ['CH001', 'CH002'],
            'سنة الصنع': ['2020', '2021'],
            'الباقي': ['5000', '3000'],
            'المجموع': ['7800', '5450'],
            'رقم الحاوية': ['CONT001', 'CONT002'],
            'العمولة': ['200', '150'],
            'قيمة الشراء': ['6000', '4000'],
            'صورة السيارة': ['', '']
        }

        df = pd.DataFrame(sample_data)
        # Fill remaining columns with empty strings
        for col in columns:
            if col not in df.columns:
                df[col] = ''

        df = df.reindex(columns=columns)
        df.to_excel('database.xlsx', index=False)
        return df

def save_data(df):
    df.to_excel('database.xlsx', index=False)

@app.route('/', methods=['GET','POST'])
def login():
    error = None
    if request.method == 'POST':
        name = request.form['name']
        code = request.form['code']
        df = load_data()
        user = df[(df['الاسم']==name) & (df['الرقم الخاص']==code)]
        if not user.empty:
            session.permanent = True
            session['user'] = name
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        error = get_message('login_error')
    return render_template('login.html', error=error)

@app.route('/dashboard')
def dashboard():
    if 'user' not in session or not session.get('logged_in'):
        return redirect(url_for('login'))
    name = session['user']
    df = load_data()
    user_cars = df[(df['الاسم']==name)]
    return render_template('dashboard.html', cars=user_cars.to_dict(orient='records'), user_name=name)

@app.route('/test')
def test():
    return '<h1>Flask App is Working!</h1><p>Go to <a href="/">Login Page</a></p>'

@app.route('/logout')
def logout():
    session.clear()
    flash(get_message('logout_success') or 'تم تسجيل الخروج بنجاح', 'success')
    return redirect(url_for('login'))

@app.route('/admin', methods=['GET','POST'])
def admin():
    admin_password = APP_SETTINGS['admin_password']
    if request.method == 'POST':
        password = request.form.get('password')
        if password == admin_password:
            session.permanent = True
            session['admin_logged_in'] = True
            df = load_data()
            return render_template('admin.html', records=df.to_dict(orient='records'), message=None)
        else:
            return render_template('admin.html', records=[], message='كلمة مرور غير صحيحة')

    # Check if admin is already logged in
    if session.get('admin_logged_in'):
        df = load_data()
        return render_template('admin.html', records=df.to_dict(orient='records'), message=None)

    return render_template('admin.html', records=[], message=None)

@app.route('/convert_to_excel')
def convert_to_excel():
    """Convert existing CSV to Excel format"""
    if os.path.exists('database.csv'):
        df = pd.read_csv('database.csv', dtype=str)
        df.to_excel('database.xlsx', index=False)
        return f'<h2>✅ تم تحويل البيانات إلى Excel بنجاح!</h2><p>يمكنك الآن تعديل ملف database.xlsx مباشرة</p><p>أي تغيير في الملف سيظهر للعملاء فوراً</p><a href="/admin">العودة لوحة التحكم</a>'
    else:
        return '<h2>❌ لم يتم العثور على ملف CSV</h2><a href="/admin">العودة لوحة التحكم</a>'

@app.route('/add_car', methods=['GET','POST'])
def add_car():
    if request.method == 'POST':
        # Handle image upload
        image_filename = ''
        if 'car_image' in request.files:
            file = request.files['car_image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Create unique filename
                import time
                filename = f"{int(time.time())}_{filename}"
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename

        # Get form data
        new_car = {
            'الاسم': request.form['name'],
            'الرقم الخاص': request.form['code'],
            'شحن الخارجي': request.form['external_shipping'],
            'التاريخ': request.form['date'],
            'شحن الداخلي': request.form['internal_shipping'],
            'VIN': request.form['vin'],
            'اللوت': request.form['lot'],
            'رقم الهيكل': request.form['chassis'],
            'سنة الصنع': request.form['year'],
            'الباقي': request.form['remaining'],
            'المجموع': request.form['total'],
            'رقم الحاوية': request.form['container'],
            'العمولة': request.form['commission'],
            'قيمة الشراء': request.form['purchase_value'],
            'صورة السيارة': image_filename
        }

        # Load existing data and add new car
        df = load_data()
        new_df = pd.concat([df, pd.DataFrame([new_car])], ignore_index=True)
        save_data(new_df)
        
        flash(get_message('car_added'), 'success')
        return redirect(url_for('admin'))

    return render_template('add_car.html')

@app.route('/edit_car/<int:car_id>', methods=['GET','POST'])
def edit_car(car_id):
    df = load_data()
    
    if car_id >= len(df):
        flash(get_message('error'), 'error')
        return redirect(url_for('admin'))
    
    if request.method == 'POST':
        # Handle image upload
        image_filename = df.iloc[car_id]['صورة السيارة'] if 'صورة السيارة' in df.columns else ''
        if 'car_image' in request.files:
            file = request.files['car_image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                import time
                filename = f"{int(time.time())}_{filename}"
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename

        # Update car data
        df.iloc[car_id] = {
            'الاسم': request.form['name'],
            'الرقم الخاص': request.form['code'],
            'شحن الخارجي': request.form['external_shipping'],
            'التاريخ': request.form['date'],
            'شحن الداخلي': request.form['internal_shipping'],
            'VIN': request.form['vin'],
            'اللوت': request.form['lot'],
            'رقم الهيكل': request.form['chassis'],
            'سنة الصنع': request.form['year'],
            'الباقي': request.form['remaining'],
            'المجموع': request.form['total'],
            'رقم الحاوية': request.form['container'],
            'العمولة': request.form['commission'],
            'قيمة الشراء': request.form['purchase_value'],
            'صورة السيارة': image_filename
        }
        
        save_data(df)
        flash(get_message('car_updated'), 'success')
        return redirect(url_for('admin'))
    
    car = df.iloc[car_id].to_dict()
    return render_template('edit_car.html', car=car, car_id=car_id)

@app.route('/delete_car/<int:car_id>')
def delete_car(car_id):
    df = load_data()
    
    if car_id >= len(df):
        flash(get_message('error'), 'error')
        return redirect(url_for('admin'))
    
    # Delete image file if exists
    if 'صورة السيارة' in df.columns and df.iloc[car_id]['صورة السيارة']:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], df.iloc[car_id]['صورة السيارة'])
        if os.path.exists(image_path):
            os.remove(image_path)
    
    # Remove car from dataframe
    df = df.drop(df.index[car_id]).reset_index(drop=True)
    save_data(df)
    
    flash(get_message('car_deleted'), 'success')
    return redirect(url_for('admin'))

@app.route('/settings', methods=['GET','POST'])
def settings():
    if request.method == 'POST':
        # Update settings in the file
        new_settings = {
            'app_name': request.form.get('app_name'),
            'company_name': request.form.get('company_name'),
            'language': request.form.get('language'),
            'contact_phone': request.form.get('contact_phone'),
            'contact_email': request.form.get('contact_email'),
            'admin_password': request.form.get('admin_password')
        }
        
        # Update APP_SETTINGS
        for key, value in new_settings.items():
            if value:  # Only update if value is provided
                APP_SETTINGS[key] = value
        
        # Write changes to file
        with open('my_settings.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Simple replacement for settings
        for key, value in new_settings.items():
            if value:
                old_pattern = f"'{key}': '[^']*'"
                new_pattern = f"'{key}': '{value}'"
                import re
                content = re.sub(old_pattern, new_pattern, content)
        
        with open('my_settings.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        flash(get_message('settings_updated'), 'success')
        return redirect(url_for('settings'))
    
    return render_template('settings.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)