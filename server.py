"""
source: https://gist.github.com/mariocesar/6396104
"""

"""
Delegate the static serving to uwsgi

DOCUMENT_ROOT=/media/Datos/music  uwsgi --wsgi share:application --http :8000 --static-check /media/Datos/music --workers 8 --master
"""

import re
import os
#from cStringIO import StringIO
import mimetypes


def notfound(env, response):
    response('404 Not Found', [])
    return ['Not found']


def list_directory(env, response, path):

    try:
        list = os.listdir(path)
    except os.error:
        return notfound(env, response)

    list.sort(key=lambda a: a.lower())

    output = []
    output.append('<html>')
    output.append('<head><title>List of %s</title></head>' % path)
    output.append('<h2>Content of %s</h2>' % path)

    output.append('<ul>')

    for descriptor in list:
        output.append('<li>')
        output.append('<a href="%(full_path)s">%(name)s</a>' % {
            'name': descriptor,
            'full_path': os.path.join(env['PATH_INFO'], descriptor)
        })
        output.append('</li>')

    output.append('</ul>')

    output.append('</html>')

    response('200 OK', [('Content-Type', 'text/html')])

    return output

def index(env, response, path):
    new_path = os.path.abspath(os.path.join(env['DOCUMENT_ROOT'], path))

    if not new_path.startswith(env['DOCUMENT_ROOT']):
        return notfound(env, response)

    if not os.path.exists(new_path):
        return notfound(env, response)

    if os.path.isdir(new_path):
        return list_directory(env, response, new_path)
    else:
        file_type = mimetypes.guess_type(new_path)[0]
        if file_type is None:
            file_type = ""
        f = open(new_path, "rb")
        output = f.read()
        f.close()
        response('200 OK', [('Content-Type', file_type),('Content-Length', str(len(output))),
        ('Connection', 'close')])
        return(output)


urlpatterns = (
    (r'(?P<path>.*)', index),
)

def application(env, response):
    path = env.get('PATH_INFO')[1:]

    env['DOCUMENT_ROOT'] = os.environ.get('DOCUMENT_ROOT', os.path.abspath(os.path.curdir))

    for regex, callback in urlpatterns:
        match = re.search(regex, path)
        if match is not None:
            response('200 OK', [('Content-Type', 'text/html')])
            return callback(env, response, **match.groupdict())

    return '<h1>404</h1>'