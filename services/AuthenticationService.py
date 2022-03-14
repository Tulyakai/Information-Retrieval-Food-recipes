import bcrypt

def addUser(data, mysql):
    cur = mysql.connection.cursor()
    try:
        password_salt = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt(10))
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (data['username'], password_salt.decode('utf-8')))
        mysql.connection.commit()
    except:
        return 'Something went wrong!', 400
    cur.close()
    return 'Register successfully', 200

def login(data, mysql):
    cur = mysql.connection.cursor()
    try:
        cur.execute("SELECT * FROM users WHERE username = %s", (data['username'],))
        response = cur.fetchall()
        if (bcrypt.checkpw(data['password'].encode('utf-8'), bytes(response[0][2], 'utf-8'))):
            result = {'id': response[0][0], 'username': response[0][1]}
        else:
            raise ValueError
    except:
        return 'Username or password is incorrect', 400
    cur.close()

    return result, 200
