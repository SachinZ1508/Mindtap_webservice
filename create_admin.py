from flask_bcrypt import generate_password_hash

password = 'Admin@1234'  # Jo password aap use karna chahte hain
password_hash = generate_password_hash(password).decode('utf-8')
print("Password Hash:")
print(password_hash)
