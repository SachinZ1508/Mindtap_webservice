import os
import pyodbc
import psycopg2
from flask_bcrypt import generate_password_hash, check_password_hash
from datetime import datetime

class Database:
    def __init__(self):
        # MSSQL ODBC connection string (keeps your local setup)
        self.mssql_connection_string = (
            "Driver={ODBC Driver 17 for SQL Server};"
            "Server=DESKTOP-T5URVUA;"
            "Database=TechMarketerDB;"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
        )

        # If a DATABASE_URL is provided (Render Postgres), we'll use it
        self.postgres_url = os.getenv("DATABASE_URL")

        # normalize postgres URL if necessary (some libs expect postgresql://)
        if self.postgres_url and self.postgres_url.startswith("postgres://"):
            # keep original string but also convert for psycopg2 if needed
            # psycopg2 accepts postgres://, but normalizing to postgresql:// is safe
            self.postgres_url = self.postgres_url.replace("postgres://", "postgresql://", 1)

        self.connection = None
        self.cursor = None
        # flag to know which DB type we're using
        self.is_postgres = bool(self.postgres_url)

    def connect(self):
        if self.connection is None:
            try:
                if self.is_postgres:
                    # Connect to Postgres using psycopg2
                    # psycopg2 accepts a full DATABASE_URL (postgresql://...)
                    self.connection = psycopg2.connect(self.postgres_url)
                    self.cursor = self.connection.cursor()
                    print("Connected to Postgres (DATABASE_URL) successfully")
                else:
                    # Fallback to your existing MSSQL ODBC connection
                    self.connection = pyodbc.connect(self.mssql_connection_string)
                    self.cursor = self.connection.cursor()
                    print("Connected to MSSQL (pyodbc) successfully")
            except Exception as e:
                print("Database connection error:", e)

    def close(self):
        if self.cursor:
            try:
                self.cursor.close()
            except Exception:
                pass
        if self.connection:
            try:
                # psycopg2 connection .close(), pyodbc connection .close() both exist
                self.connection.close()
            except Exception:
                pass

    # Contact methods
    def insert_contact(self, name, email, message):
        self.connect()
        try:
            sql = "INSERT INTO Contacts (Name, Email, Message) VALUES (%s, %s, %s)" if self.is_postgres else "INSERT INTO Contacts (Name, Email, Message) VALUES (?, ?, ?)"
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
            sql = "SELECT * FROM BlogPosts WHERE Slug = %s" if self.is_postgres else "SELECT * FROM BlogPosts WHERE Slug = ?"
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
            sql = "INSERT INTO Users (Username, Email, PasswordHash) VALUES (%s, %s, %s)" if self.is_postgres else "INSERT INTO Users (Username, Email, PasswordHash) VALUES (?, ?, ?)"
            self.cursor.execute(sql, (username, email, password_hash))
            self.connection.commit()
            return True
        except Exception as e:
            print("Error creating user:", e)
            return False

    def get_user_by_username(self, username):
        self.connect()
        try:
            sql = "SELECT * FROM Users WHERE Username = %s" if self.is_postgres else "SELECT * FROM Users WHERE Username = ?"
            self.cursor.execute(sql, (username,))
            return self.cursor.fetchone()
        except Exception as e:
            print("Error fetching user:", e)
            return None

    def insert_blog_post(self, title, slug, summary, content, featured_image, author):
        """
        Use Python to set PublishedDate (UTC) so SQL dialect differences (GETDATE vs NOW) don't break.
        """
        self.connect()
        try:
            published_at = datetime.utcnow()
            if self.is_postgres:
                sql = """
                INSERT INTO BlogPosts (Title, Slug, Summary, Content, FeaturedImage, Author, PublishedDate)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                params = (title, slug, summary, content, featured_image, author, published_at)
            else:
                # MSSQL + pyodbc: use ? placeholders
                sql = """
                INSERT INTO BlogPosts (Title, Slug, Summary, Content, FeaturedImage, Author, PublishedDate)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                params = (title, slug, summary, content, featured_image, author, published_at)
            self.cursor.execute(sql, params)
            self.connection.commit()
            return True
        except Exception as e:
            print("Error inserting blog post:", e)
            return False

    def fetch_blog_post_by_id(self, post_id):
        self.connect()
        try:
            sql = "SELECT * FROM BlogPosts WHERE BlogPostID = %s" if self.is_postgres else "SELECT * FROM BlogPosts WHERE BlogPostID = ?"
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
            SET Title = %s, Slug = %s, Summary = %s, Content = %s, FeaturedImage = %s
            WHERE BlogPostID = %s
            """ if self.is_postgres else """
            UPDATE BlogPosts
            SET Title = ?, Slug = ?, Summary = ?, Content = ?, FeaturedImage = ?
            WHERE BlogPostID = ?
            """
            params = (title, slug, summary, content, featured_image, post_id)
            self.cursor.execute(sql, params)
            self.connection.commit()
            return True
        except Exception as e:
            print("Error updating blog post:", e)
            return False

    def delete_blog_post(self, post_id):
        self.connect()
        try:
            sql = "DELETE FROM BlogPosts WHERE BlogPostID = %s" if self.is_postgres else "DELETE FROM BlogPosts WHERE BlogPostID = ?"
            self.cursor.execute(sql, (post_id,))
            self.connection.commit()
            return True
        except Exception as e:
            print("Error deleting blog post:", e)
            return False

    def insert_user_campaign(self, name, email, idea):
        self.connect()
        try:
            sql = "INSERT INTO UserCampaigns (Name, Email, CampaignIdea) VALUES (%s, %s, %s)" if self.is_postgres else "INSERT INTO UserCampaigns (Name, Email, CampaignIdea) VALUES (?, ?, ?)"
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
            # fetchone() shape differs between psycopg2 and pyodbc: psycopg2 returns tuple, pyodbc returns tuple as well
            res = self.cursor.fetchone()
            return res[0] if res else 0
        except Exception as e:
            print("Error fetching contact count:", e)
            return 0

    def get_total_blog_posts(self):
        self.connect()
        try:
            query = "SELECT COUNT(*) FROM BlogPosts"
            self.cursor.execute(query)
            res = self.cursor.fetchone()
            return res[0] if res else 0
        except Exception as e:
            print("Error fetching blog post count:", e)
            return 0

    def get_total_user_campaigns(self):
        self.connect()
        try:
            sql = "SELECT COUNT(*) FROM UserCampaigns"
            self.cursor.execute(sql)
            res = self.cursor.fetchone()
            return res[0] if res else 0
        except Exception as e:
            print("Error fetching user campaign count:", e)
            return 0

    def fetch_blog_posts_with_limit_offset(self, limit, offset):
        """
        Use MSSQL pagination when using MSSQL, and LIMIT/OFFSET for Postgres.
        """
        self.connect()
        try:
            if self.is_postgres:
                query = """
                    SELECT * FROM BlogPosts
                    ORDER BY PublishedDate DESC
                    LIMIT %s OFFSET %s;
                """
                self.cursor.execute(query, (limit, offset))
            else:
                # SQL Server style using OFFSET ... FETCH NEXT ... ROWS ONLY
                query = """
                    SELECT * FROM BlogPosts
                    ORDER BY PublishedDate DESC
                    OFFSET ? ROWS FETCH NEXT ? ROWS ONLY;
                """
                self.cursor.execute(query, (offset, limit))
            return self.cursor.fetchall()
        except Exception as e:
            print("Error fetching paginated blog posts:", e)
            return []
