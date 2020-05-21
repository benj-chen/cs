import wsgiref.simple_server
import urllib.parse
import sqlite3
import http.cookies
import random

connection = sqlite3.connect('users.db')
stmt = "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
cursor = connection.cursor()
result = cursor.execute(stmt)
r = result.fetchall()
if (r == []):
    exp = 'CREATE TABLE users (username,password)'
    connection.execute(exp)


def application(environ, start_response):
    headers = [('Content-Type', 'text/html; charset=utf-8')]

    path = environ['PATH_INFO']
    params = urllib.parse.parse_qs(environ['QUERY_STRING'])
    un = params['username'][0] if 'username' in params else None
    pw = params['password'][0] if 'password' in params else None

    if path == '/register' and un and pw:
        user = cursor.execute('SELECT * FROM users WHERE username = ?', [un]).fetchall()
        if user:
            start_response('200 OK', headers)
            return ['Sorry, username {} is taken. <a href="/">Log in</a>'.format(un).encode()]
        else:
            start_response('200 OK', headers)
            connection.execute('INSERT INTO users VALUES (?,?)',[un,pw])
            headers.append(('Set-Cookie', 'session={}:{}'.format(un, pw)))
            connection.commit()
            return ['Username {} successfully registered. <a href="/account">Account</a>'.format(un).encode()]

    elif path == '/login' and un and pw:
        user = cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', [un, pw]).fetchall()
        if user:
            headers.append(('Set-Cookie', 'session={}:{}'.format(un, pw)))
            start_response('200 OK', headers)
            return ['User {} successfully logged in. <a href="/account">Account</a>'.format(un).encode()]
        else:
            start_response('200 OK', headers)
            return ['Incorrect username or password'.encode()]

    elif path == '/logout':
        headers.append(('Set-Cookie', 'session=0; expires=Thu, 01 Jan 1970 00:00:00 GMT'))
        start_response('200 OK', headers)
        return ['Logged out. <a href="/">Login</a>'.encode()]

    elif path == '/account':
        start_response('200 OK', headers)

        if 'HTTP_COOKIE' not in environ:
            return ['Not logged in <a href="/">Login</a>'.encode()]

        cookies = http.cookies.SimpleCookie()
        cookies.load(environ['HTTP_COOKIE'])
        if 'session' not in cookies:
            return ['Not logged in <a href="/">Login</a>'.encode()]

        [un, pw] = cookies['session'].value.split(':')
        user = cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', [un, pw]).fetchall()

        #This is where the game begins. This section of is code only executed if the login form works, and if the user is successfully logged in
        if user:
            correct = 0
            wrong = 0

            cookies = http.cookies.SimpleCookie()
            if 'HTTP_COOKIE' in environ:
                cookies.load(environ["HTTP_COOKIE"])

                if un in cookies:
                    correct = int(cookies[un].value.split(':')[0])
                    wrong = int(cookies[un].value.split(':')[1])
                    print("corrvalue initialized")
                else:
                    correct=0
                    wrong=0
                    print("reset initialized")


            page = '<!DOCTYPE html><html><head><title>Multiply with Score</title></head><body>'
            if 'factor1' in params and 'factor2' in params and 'answer' in params:
                f1 = params['factor1'][0]
                f2 = params['factor2'][0]
                ans = params['answer'][0]
                if int(ans)==(int(f1)*int(f2)):
                    page+='<h1 style="background-color: lightgreen">Correct! {}x{}={}</h1>'.format(f1,f2,ans)
                    correct=correct+1
                    print("Correct",correct)
                else:
                    wrong=wrong+1
                    print("Wrong", wrong)
                    page+='<h1 style="background-color: red">Wrong! {}x{}={}</h1>'.format(f1,f2,str(int(f1)*int(f2)))


            elif 'reset' in params:
                correct=0
                wrong=0
                headers.append(('Set-Cookie', '{}={}:{}'.format(un, correct, wrong)))

            headers.append(('Set-Cookie', '{}={}:{}'.format(un,correct,wrong)))

            f1 = random.randrange(10) + 1
            f2 = random.randrange(10) + 1

            hyperlink = '<a href="/account?username={}&amp;password={}&amp;factor1={}&amp;factor2={}&amp;answer={}">{}: {}</a><br>'



            page = page + '<h1>What is {} x {}</h1>'.format(f1, f2)

            corrplace=random.randint(1,4)
            for x in range(1,5):
                if x==corrplace:
                    page+=hyperlink.format(un,pw,f1,f2,f1*f2,str(x),f1*f2)
                else:
                    r1=random.randrange(10)+1
                    r2=random.randrange(10)+1
                    page+=hyperlink.format(un,pw,f1,f2,r1*r2,str(x),r1*r2)

            page += '''<h2>Score</h2>
            Correct: {}<br>
            Wrong: {}<br>
            <a href="/account?reset=true">Reset</a>
            </body></html>'''.format(correct, wrong)

            return [page.encode()]
        else:
            return ['Not logged in. <a href="/">Login</a>'.encode()]

    elif path == '/':
        start_response("200 OK", headers)
        page = '''<table>
                <form action="/login" style="background-color:blue">
                    <h1>Login</h1>
                    Username <input type="text" name="username"><br>
                    Password <input type="password" name="password"><br>
                    <input type="submit" value="Log in">
                </form>

                <form action="/register" style="background-color:pink">
                    <h1>Register</h1>
                    Username <input type="text" name="username" value=""><br>
                    Password <input type="password" name="password" value=""><br>
                    <input type="submit" value="Register">
                </form>
                </table>'''
        return [page.encode()]
    else:
        start_response('404 Not Found', headers)
        return ['Status 404: Resource not found'.encode()]


httpd = wsgiref.simple_server.make_server('', 8000, application)
httpd.serve_forever()