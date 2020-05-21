import wsgiref.simple_server
import urllib.parse
import http.cookies
import random
import sqlite3

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
            return ['Sorry, username {} is taken'.format(un).encode()]
        else:

            cursor.execute('INSERT INTO users VALUES (?,?)', [un,pw])
            connection.commit()
            headers.append(('Set-Cookie', 'session={}:{}'.format(un, pw)))
            start_response('200 OK', headers)
            return['Username successfully added'.encode()]

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

                cookies=http.cookies.SimpleCookie()
                cookies.load(environ['HTTP_COOKIE'])
                if 'correct' in cookies:
                    correct=int(cookies['correct'].value)
                if 'wrong' in cookies:
                    wrong=int(cookies['wrong'].value)

            page = '<!DOCTYPE html><html><head><title>Multiply with Score</title></head><body>'
            if 'factor1' in params and 'factor2' in params and 'answer' in params:
                factor1=int(params['factor1'][0])
                factor2=int(params['factor2'][0])
                ans=int(params['answer'][0])
                page+=str(factor1)+"\n"
                page+=str(factor2)+"\n"
                page+=str(ans)+"\n"

                if factor1*factor2==ans:
                    page+='<h3 style="color: green">You were correct!!</h3>'
                else:
                    page += '<h3 style="color: red">You were wrong!! Aiya!!</h3>'


            elif 'reset' in params:
                correct = 0
                wrong = 0

            headers.append(('Set-Cookie', 'score={}:{}'.format(correct, wrong)))

            f1 = random.randrange(10) + 1
            f2 = random.randrange(10) + 1

            page = page + '<h1>What is {} x {}</h1>'.format(f1, f2)



            hyperlink = '<a href="/account?username={}&amp;password={}&amp;factor1={}&amp;factor2={}&amp;answer={}">{}: {}</a><br>'


            correctplace=random.randint(1,4)

            for x in range(1,5):
                if x==correctplace:
                    page=page+(hyperlink.format(un, pw, f1, f2, f1 * f2, str(correctplace), f1 * f2))

                else:
                    v1=random.randint(1,12)
                    v2=random.randint(1,12)
                    page+=(hyperlink.format(un,pw,f1,f2,v1*v2,str(x),v1*v2))
            print(page)
            page = page + "<a href='/account></a><br>"
            page = page + '''<p>correct: {}</p>
            <p>wrong: {}</p><br>'''.format(correct, wrong)
            print(page)
            page+="</html>"






            return [page.encode()]
        else:
            return ['Not logged in. <a href="/">Login</a>'.encode()]

    elif path == '/':
        start_response("200 OK",headers)
        page='''<table>
        <form action="/login" style="background-color:blue">
            <h1>Login</h1>
            Username <input type="text" name="username"><br>
            Password <input type="password" name="password"><br>
            <input type="submit" value="Log in">
        </form>
        
        <form action="/register" style="background-color:pink">
            <h1>Register</h1>
            Username <input type="text" name="username"><br>
            Password <input type="password" name="password"><br>
            <input type="submit" value="Register">
        </form>
        </table>'''
        return[page.encode()]

    else:
        start_response('404 Not Found', headers)
        return ['Status 404: Resource not found'.encode()]


httpd = wsgiref.simple_server.make_server('', 8000, application)
httpd.serve_forever()