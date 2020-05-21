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
            return['Sorry, username {} is taken'.format(un).encode()]
        else:
            connection.execute('INSERT INTO users VALUES (?, ?)', [un, pw])
            connection.commit()
            headers.append(('Set-Cookie', 'session={}:{}'.format(un, pw)))
            start_response('200 OK', headers)
            return ['Congratulations, username {} been successfully registered. <a href="/account">Account</a>'.format(
                un).encode()]
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

        if 'HTTP_COOKIE' not in environ:
            return ['Not logged in <a href="/">Login</a>'.encode()]
        cookies = http.cookies.SimpleCookie()
        cookies.load(environ['HTTP_COOKIE'])
        if 'session' not in cookies:
            return ['Not logged in <a href="/">Login</a>'.encode()]
        [un, pw] = cookies['session'].value.split(':')
        user = cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', [un, pw]).fetchall()

        if user:
            correct = 0
            wrong = 0
            cookies = http.cookies.SimpleCookie()
            if 'HTTP_COOKIE' in environ:
                cookies = http.cookies.SimpleCookie()
                cookies.load(environ['HTTP_COOKIE'])
                if 'counter' in cookies:
                    counter = int(cookies['counter'].value) + 1
                else:
                    counter = 0
            page = '<!DOCTYPE html><html><head><title>Multiply with Score</title></head><body>'

            cuser = str(user[0][0])
            print(cuser)
            print(un)
            if cuser in cookies:
                # print(user)
                print('correct-')
                correct = int(cookies[cuser].value.split(':')[0])
                print(correct)
                wrong = int(cookies[cuser].value.split(':')[1])
                print('wrong')
                print(wrong)

            if 'factor1' in params and 'factor2' in params and 'answer' in params:
                factor1 = params['factor1'][0]
                factor2 = params['factor2'][0]
                answer = params['answer'][0]
                # cuser = str(user[0][0])
                # print(cuser)

                if int(answer) == (int(factor1) * int(factor2)):
                    page = page + '<h1><p style="background-color: lightgreen">Correct, {} x {} = {}</p></h1>'.format(
                        factor1, factor2, answer)
                    correct = correct + 1
                else:
                    page = page + '<h1><p style="background-color: red">Wrong, {} x {} = {}</p></h1>'.format(factor1,
                                                                                                             factor2,
                                                                                                             answer)
                    wrong = wrong + 1
                print('what now' + cuser)
                print('correct' + str(correct))
                print('wrong' + str(wrong))
                headers = [
                    ('Content-Type', 'text/html; charset=utf-8'),
                    ('Set-Cookie', 'counter={}'.format(counter)),
                    ('Set-Cookie', '{}={}:{}'.format(cuser, correct, wrong))
                ]

            elif 'reset' in params:
                correct = 0
                wrong = 0
                headers.append(('Set-Cookie', '{}={}:{}'.format(cuser, correct, wrong)))

            f1 = random.randrange(10) + 1
            f2 = random.randrange(10) + 1
            page = page + '<h1>{} - What is {} x {}</h1>'.format(cuser, f1, f2)
            a1 = random.randint(1, 10)
            a2 = random.randint(1, 10)
            a3 = random.randint(1, 10)
            a4 = (f1 * f2)
            answer = [a1, a2, a3, a4]
            random.shuffle(answer)
            hyperlink = '<a href="/account?username={}&amp;password={}&amp;factor1={}&amp;factor2={}&amp;answer={}">{}: {}</a><br>'
            strlist = 'A: {}, B: {} C: {} D: {}'.format(a1, a2, a3, a4)
            page += hyperlink.format(un, pw, f1, f2, a1, "A", a1)
            page += hyperlink.format(un, pw, f1, f2, a2, "B", a2)
            page += hyperlink.format(un, pw, f1, f2, a3, "C", a3)
            page += hyperlink.format(un, pw, f1, f2, a4, "D", a4)
            page += '''<h2>Score</h2>
            Correct: {}<br>
            Wrong: {}<br>
            <a href="/account?reset=true">Reset</a>
            </body></html>'''.format(correct, wrong)
            start_response('200 OK', headers)
            return [page.encode()]
        else:
            return ['Not logged in. <a href="/">Login</a>'.encode()]
    elif path == '/':
        login_form = '''
        <table><tr><td>
        <form action="/login" style="background-color:blue">
            <h1>Login</h1>
            Username <input type="text" name="username"><br>
            Password <input type="password" name="password"><br>
            <input type="submit" value="Log in">
        </form>
        </td><td>
        <form action="/register" style="background-color:pink">
            <h1>Register</h1>
            Username <input type="text" name="username"><br>
            Password <input type="password" name="password"><br>
            <input type="submit" value="Register">
        </form>
        </td></tr></table>
        '''
        start_response('200 OK', headers)
        return [login_form.encode()]
    else:
        start_response('404 Not Found', headers)
        return ['Status 404: Resource not found'.encode()]


httpd = wsgiref.simple_server.make_server('', 8000, application)
httpd.serve_forever()

