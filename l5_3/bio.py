"""
import wsgiref.simple_server


def application(environ, start_response):
    global page
    headers = [('Content-Type', 'text/html; charset=utf-8')]
    start_response('200 OK', headers)

    path = environ['PATH_INFO']
    if path == '/biography':
        page = '''<!DOCTYPE html>
        <html>
          <head>
            <meta charset="UTF-8">  
            <title>Page Title</title>
          </head>
          <body>
            <h1>h1 Big heading</h1>
            <h2>h2 Smaller heading</h2>
            <div>A div is a block of HTML content</div>
            <p>A paragraph of text. Often programmers will insert random Latin words to illustrate what things look like. If you want to have fun with it, you can use hipsum.co. Here is an example. Cold-pressed mlkshk mustache, umami keffiyeh everyday carry coloring book tousled whatever activated charcoal post-ironic gastropub synth succulents. Fap mustache godard austin. Chambray yuccie subway tile af poke. Slow-carb fam echo park artisan, narwhal synth PBR&B vexillologist godard biodiesel wayfarers pok pok jean shorts. Pitchfork chillwave ennui skateboard tote bag vaporware. Photo booth prism iPhone, 3 wolf moon forage subway tile organic fixie keytar blog franzen. Messenger bag forage literally, letterpress copper mug kickstarter food truck affogato paleo organic jianbing chartreuse meggings.</p>
            Row breaks<br>do not use<br>closing tags<br>
            <hr>
            Nor do horizontal lines
            <hr>
            Clickable <a href="./tags.html">hyperlinks</a> are really important
            <hr>
            <table>
              <tr><th>Table heading 1</th><th>Table heading 2</th></tr>
              <tr><td>Row 1, Col 1</td><td>Row 1, Col 2</td></tr>
              <tr><td>Row 2, Col 1</td><td>Row 2, Col 2</td></tr>
            </table>
            <hr>
            Forms are used for input. More on them in a later lesson.
            <form>
              <input type="text" name="lastname">
              <input type="submit" value="Log me in">
            </form>
            <hr>
            <img src="mountains.jpg" alt="Mountain">
          </body>
        </html>'''

    return [page.encode()]


httpd = wsgiref.simple_server.make_server('', 8000, application)
httpd.serve_forever()
"""