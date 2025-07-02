
# ملف الإعدادات الخاص بك - يمكنك تعديل هذا الملف بسهولة
# Your Custom Settings File - You can easily edit this file

# إعدادات التطبيق
APP_SETTINGS = {
    'app_name': 'نظام إدارة السيارات',  # اسم التطبيق
    'admin_password': 'admin123',        # كلمة مرور المدير
    'company_name': 'شركة السيارات المحدودة',  # اسم الشركة
    'contact_phone': '+966-50-123-4567',   # رقم الهاتف
    'contact_email': 'info@carcompany.com', # البريد الإلكتروني
    'language': 'ar',                    # اللغة (ar للعربية، en للإنجليزية)
    'upload_folder': 'static/uploads'    # مجلد رفع الصور
}

# ألوان وتصميم الموقع
DESIGN_SETTINGS = {
    'primary_color': '#007bff',      # اللون الأساسي
    'secondary_color': '#28a745',    # اللون الثانوي
    'background_color': '#f8f9fa',   # لون الخلفية
    'text_color': '#333333'          # لون النص
}

# إعدادات قاعدة البيانات
DATABASE_SETTINGS = {
    'excel_file': 'database.xlsx',
    'backup_file': 'database_backup.csv',
    'auto_backup': True              # نسخة احتياطية تلقائية
}

# رسائل مخصصة
MESSAGES = {
    'ar': {
        'welcome': 'مرحباً بك في نظام إدارة السيارات',
        'login_error': 'بيانات دخول غير صحيحة',
        'success': 'تم بنجاح!',
        'error': 'حدث خطأ، يرجى المحاولة مرة أخرى',
        'car_added': 'تم إضافة السيارة بنجاح',
        'car_updated': 'تم تحديث السيارة بنجاح',
        'car_deleted': 'تم حذف السيارة بنجاح',
        'settings_updated': 'تم تحديث الإعدادات بنجاح',
        'logout_success': 'تم تسجيل الخروج بنجاح'
    },
    'en': {
        'welcome': 'Welcome to Car Management System',
        'login_error': 'Invalid login credentials',
        'success': 'Success!',
        'error': 'An error occurred, please try again',
        'car_added': 'Car added successfully',
        'car_updated': 'Car updated successfully',
        'car_deleted': 'Car deleted successfully',
        'settings_updated': 'Settings updated successfully',
        'logout_success': 'Logged out successfully'
    }
}

def get_setting(category, key, lang=None):
    """دالة للحصول على إعداد معين"""
    settings_map = {
        'app': APP_SETTINGS,
        'design': DESIGN_SETTINGS,
        'database': DATABASE_SETTINGS,
        'messages': MESSAGES
    }
    
    if category == 'messages':
        current_lang = lang or APP_SETTINGS.get('language', 'ar')
        return MESSAGES.get(current_lang, {}).get(key, '')
    
    return settings_map.get(category, {}).get(key, '')

def get_message(key, lang=None):
    """دالة للحصول على رسالة بلغة معينة"""
    return get_setting('messages', key, lang)
