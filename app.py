from flask import Flask, render_template, request, redirect, url_for, flash, abort, session
from flask_bcrypt import check_password_hash
from flask_mail import Mail, Message
from database import Database
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a secure random key

# Email configuration - update with your real SMTP details
app.config.update(
    MAIL_SERVER='smtp.example.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='you@example.com',
    MAIL_PASSWORD='yourpassword'
)
mail = Mail(app)

db = Database()

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' not in session:
                flash('Please login first.', 'error')
                return redirect(url_for('login'))
            if session['role'] != role:
                flash('You do not have permission to access this page.', 'error')
                if role == 'Admin':
                    return redirect(url_for('home'))
                else:
                    return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/contact', methods=['GET'])
def contact():
    return render_template('contact.html')

@app.route('/contact_send', methods=['POST'])
def contact_send():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    message = request.form.get('message', '').strip()
    if len(name) < 3:
        flash('Name must be at least 3 characters.', 'error')
        return redirect(url_for('contact'))
    if '@' not in email or '.' not in email:
        flash('Invalid email address.', 'error')
        return redirect(url_for('contact'))
    if len(message) < 10:
        flash('Message must be at least 10 characters.', 'error')
        return redirect(url_for('contact'))
    if db.insert_contact(name, email, message):
        try:
            msg = Message(
                subject="Thank you for contacting us",
                sender=app.config['MAIL_USERNAME'],
                recipients=[email]
            )
            msg.body = f"Hi {name},\n\nThank you for your message. We will get back to you shortly."
            mail.send(msg)
        except Exception as e:
            print("Error sending confirmation email:", e)
        flash('Message sent successfully! Confirmation email sent.', 'success')
    else:
        flash('Error sending message. Try again later.', 'error')
    return redirect(url_for('contact'))

@app.route('/blog')
def blog():
    page = request.args.get('page', 1, type=int)  # Default page 1
    per_page = 5  # Ek page par 5 blog posts dikhayenge
    offset = (page - 1) * per_page
    
    posts = db.fetch_blog_posts_with_limit_offset(per_page, offset)
    total_posts = db.get_total_blog_posts()
    total_pages = (total_posts + per_page - 1) // per_page
    
    return render_template('blog.html', posts=posts, page=page, total_pages=total_pages)

@app.route('/blog/<slug>')
def blog_post(slug):
    post = db.fetch_blog_post_by_slug(slug)
    if post is None:
        abort(404)
    return render_template('post_detail.html', post=post)

@app.route('/services')
def services():
    services_list = db.fetch_all_services()
    return render_template('services.html', services=services_list)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = db.get_user_by_username(username)
        if user and check_password_hash(user.PasswordHash, password):
            session['user_id'] = user.UserID
            session['username'] = user.Username
            session['role'] = user.Role  # Important to save role here
            flash('Logged in successfully.', 'success')
            if user.Role == 'Admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('home'))
        else:
            flash('Invalid username or password.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('home'))

@app.route('/admin')
@role_required('Admin')
def admin_dashboard():
    try:
        db.connect()
        db.cursor.execute("SELECT ContactID, Name, Email, Message, SubmittedAt FROM Contacts ORDER BY SubmittedAt DESC")
        contacts = db.cursor.fetchall()
        contact_count = db.get_total_contacts()
        blog_count = db.get_total_blog_posts()
        campaign_count = db.get_total_user_campaigns()
    except Exception as e:
        flash('Error fetching data.', 'error')
        contacts = []
        contact_count = 0
        blog_count = 0
        campaign_count = 0
    return render_template('admin_dashboard.html', contacts=contacts, contact_count=contact_count, blog_count=blog_count, campaign_count=campaign_count)


@app.route('/admin/blog/new', methods=['GET', 'POST'])
@role_required('Admin')
def new_blog_post():
    if request.method == 'POST':
        title = request.form.get('title')
        slug = request.form.get('slug')
        summary = request.form.get('summary')
        content = request.form.get('content')
        featured_image = request.form.get('featured_image')
        author = session.get('username')
        if not title or not slug or not content:
            flash('Title, Slug, and Content are required', 'error')
            return redirect(url_for('new_blog_post'))
        if db.insert_blog_post(title, slug, summary, content, featured_image, author):
            flash('Blog post added successfully', 'success')
            return redirect(url_for('blog'))
        else:
            flash('Error adding blog post', 'error')
    return render_template('new_blog_post.html')

@app.route('/admin/blog/edit/<int:post_id>', methods=['GET', 'POST'])
@role_required('Admin')
def edit_blog_post(post_id):
    post = db.fetch_blog_post_by_id(post_id)
    if not post:
        flash('Blog post not found', 'error')
        return redirect(url_for('blog'))
    if request.method == 'POST':
        title = request.form.get('title')
        slug = request.form.get('slug')
        summary = request.form.get('summary')
        content = request.form.get('content')
        featured_image = request.form.get('featured_image')
        if not title or not slug or not content:
            flash('Title, Slug, and Content are required', 'error')
            return redirect(url_for('edit_blog_post', post_id=post_id))
        if db.update_blog_post(post_id, title, slug, summary, content, featured_image):
            flash('Blog post updated successfully', 'success')
            return redirect(url_for('blog'))
        else:
            flash('Error updating blog post', 'error')
    return render_template('edit_blog_post.html', post=post)

@app.route('/admin/blog/delete/<int:post_id>', methods=['POST'])
@role_required('Admin')
def delete_blog_post(post_id):
    if db.delete_blog_post(post_id):
        flash('Blog post deleted successfully', 'success')
    else:
        flash('Error deleting blog post', 'error')
    return redirect(url_for('blog'))

@app.route('/campaign_submit', methods=['GET', 'POST'])
def campaign_submit():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        campaign_idea = request.form.get('campaign_idea', '').strip()

        if len(name) < 3 or '@' not in email or len(campaign_idea) < 10:
            flash('Please provide a valid name, email, and campaign idea (min 10 chars).', 'error')
            return redirect(url_for('campaign_submit'))

        if db.insert_user_campaign(name, email, campaign_idea):
            flash('Campaign idea submitted successfully. Thank you!', 'success')
        else:
            flash('Error submitting your idea. Please try again later.', 'error')
        return redirect(url_for('campaign_submit'))

    return render_template('campaign_submit.html')


@app.route('/admin/campaigns')
@role_required('Admin')
def admin_view_campaigns():
    campaigns = db.fetch_all_user_campaigns()
    return render_template('admin_campaigns.html', campaigns=campaigns)


if __name__ == '__main__':
    app.run(debug=True)
