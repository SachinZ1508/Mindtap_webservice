import pyodbc
from flask_bcrypt import generate_password_hash, check_password_hash



class Database:
    def __init__(self):
        self.connection_string = (
            "Driver={ODBC Driver 17 for SQL Server};"
            "Server=DESKTOP-T5URVUA;"
            "Database=TechMarketerDB;"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
        )
        self.connection = None
        self.cursor = None

    def connect(self):
        if self.connection is None:
            try:
                self.connection = pyodbc.connect(self.connection_string)
                self.cursor = self.connection.cursor()
                print("Database connected successfully")
            except Exception as e:
                print("Database connection error:", e)

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    # Contact methods
    def insert_contact(self, name, email, message):
        self.connect()
        try:
            sql = "INSERT INTO Contacts (Name, Email, Message) VALUES (?, ?, ?)"
            self.cursor.execute(sql, (name, email, message))
            self.connection.commit()
            return True
        except Exception as e:
            print("Error inserting contact:", e)
            return False

    # Blog methods
    def fetch_all_blog_posts(self):
        self.connect()
        try:
            sql = "SELECT BlogPostID, Title, Slug, Summary, PublishedDate, Author, FeaturedImage FROM BlogPosts ORDER BY PublishedDate DESC"
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except Exception as e:
            print("Error fetching blog posts:", e)
            return []

    def fetch_blog_post_by_slug(self, slug):
        self.connect()
        try:
            sql = "SELECT * FROM BlogPosts WHERE Slug = ?"
            self.cursor.execute(sql, (slug,))
            return self.cursor.fetchone()
        except Exception as e:
            print("Error fetching blog post:", e)
            return None

    # Services methods
    def fetch_all_services(self):
        self.connect()
        try:
            sql = "SELECT ServiceID, Name, Description, Image FROM Services ORDER BY Name"
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except Exception as e:
            print("Error fetching services:", e)
            return []
    def create_user(self, username, email, password):
        self.connect()
        try:
            password_hash = generate_password_hash(password).decode('utf-8')
            sql = "INSERT INTO Users (Username, Email, PasswordHash) VALUES (?, ?, ?)"
            self.cursor.execute(sql, (username, email, password_hash))
            self.connection.commit()
            return True
        except Exception as e:
            print("Error creating user:", e)
            return False

    def get_user_by_username(self, username):
        self.connect()
        try:
            sql = "SELECT * FROM Users WHERE Username = ?"
            self.cursor.execute(sql, (username,))
            return self.cursor.fetchone()
        except Exception as e:
            print("Error fetching user:", e)
            return None
    def insert_blog_post(self, title, slug, summary, content, featured_image, author):
        self.connect()
        try:
            sql = """
            INSERT INTO BlogPosts (Title, Slug, Summary, Content, FeaturedImage, Author, PublishedDate)
            VALUES (?, ?, ?, ?, ?, ?, GETDATE())
            """
            self.cursor.execute(sql, (title, slug, summary, content, featured_image, author))
            self.connection.commit()
            return True
        except Exception as e:
            print("Error inserting blog post:", e)
            return False

    def fetch_blog_post_by_id(self, post_id):
        self.connect()
        try:
            sql = "SELECT * FROM BlogPosts WHERE BlogPostID = ?"
            self.cursor.execute(sql, (post_id,))
            return self.cursor.fetchone()
        except Exception as e:
            print("Error fetching blog post by id:", e)
            return None

    def update_blog_post(self, post_id, title, slug, summary, content, featured_image):
        self.connect()
        try:
            sql = """
            UPDATE BlogPosts
            SET Title = ?, Slug = ?, Summary = ?, Content = ?, FeaturedImage = ?
            WHERE BlogPostID = ?
            """
            self.cursor.execute(sql, (title, slug, summary, content, featured_image, post_id))
            self.connection.commit()
            return True
        except Exception as e:
            print("Error updating blog post:", e)
            return False

    def delete_blog_post(self, post_id):
        self.connect()
        try:
            sql = "DELETE FROM BlogPosts WHERE BlogPostID = ?"
            self.cursor.execute(sql, (post_id,))
            self.connection.commit()
            return True
        except Exception as e:
            print("Error deleting blog post:", e)
            return False
    def insert_user_campaign(self, name, email, idea):
        self.connect()
        try:
            sql = "INSERT INTO UserCampaigns (Name, Email, CampaignIdea) VALUES (?, ?, ?)"
            self.cursor.execute(sql, (name, email, idea))
            self.connection.commit()
            return True
        except Exception as e:
            print("Error inserting user campaign:", e)
            return False

    def fetch_all_user_campaigns(self):
        self.connect()
        try:
            sql = "SELECT CampaignID, Name, Email, CampaignIdea, SubmittedAt FROM UserCampaigns ORDER BY SubmittedAt DESC"
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except Exception as e:
            print("Error fetching user campaigns:", e)
            return []
    def get_total_contacts(self):
        self.connect()
        try:
            sql = "SELECT COUNT(*) FROM Contacts"
            self.cursor.execute(sql)
            return self.cursor.fetchone()[0]
        except Exception as e:
            print("Error fetching contact count:", e)
            return 0

    def get_total_blog_posts(self):
        self.connect()
        try:
            sql = "SELECT COUNT(*) FROM BlogPosts"
            self.cursor.execute(sql)
            return self.cursor.fetchone()[0]
        except Exception as e:
            print("Error fetching blog post count:", e)
            return 0

    def get_total_user_campaigns(self):
        self.connect()
        try:
            sql = "SELECT COUNT(*) FROM UserCampaigns"
            self.cursor.execute(sql)
            return self.cursor.fetchone()[0]
        except Exception as e:
            print("Error fetching user campaign count:", e)
            return 0
    def fetch_blog_posts_with_limit_offset(self, limit, offset):
        query = """
            SELECT * FROM BlogPosts
            ORDER BY PublishedDate DESC
            OFFSET ? ROWS FETCH NEXT ? ROWS ONLY;
        """
        self.cursor.execute(query, (offset, limit))
        return self.cursor.fetchall()

    def get_total_blog_posts(self):
        query = "SELECT COUNT(*) FROM BlogPosts"
        self.cursor.execute(query)
        return self.cursor.fetchone()[0]
                        