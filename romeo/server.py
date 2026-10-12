import base64, os, re, sys
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
USER, PW, ROOT = sys.argv[1], sys.argv[2], sys.argv[3]
TOKEN = None
class H(SimpleHTTPRequestHandler):
    def __init__(s,*a,**k): super().__init__(*a,directory=ROOT,**k)
    def end_headers(s):
        s.send_header("X-Robots-Tag","noindex"); s.send_header("Accept-Ranges","bytes"); super().end_headers()
    def auth(s):
        return True
        s.send_response(401); s.send_header("WWW-Authenticate",'Basic realm="ROMEO preview"'); s.send_header("Content-Length","0"); s.end_headers(); return False
    def do_HEAD(s):
        if s.auth(): super().do_HEAD()
    def do_GET(s):
        if not s.auth(): return
        r=s.headers.get("Range"); p=s.translate_path(s.path)
        m=re.match(r"bytes=(\d*)-(\d*)",r or "")
        if m and os.path.isfile(p):
            size=os.path.getsize(p)
            a=int(m.group(1)) if m.group(1) else max(0,size-int(m.group(2)))
            b=int(m.group(2)) if m.group(1) and m.group(2) else size-1
            b=min(b,size-1)
            s.send_response(206); s.send_header("Content-Type",s.guess_type(p))
            s.send_header("Content-Range",f"bytes {a}-{b}/{size}"); s.send_header("Content-Length",str(b-a+1)); s.end_headers()
            with open(p,"rb") as f:
                f.seek(a); n=b-a+1
                while n>0:
                    d=f.read(min(65536,n))
                    if not d: break
                    try: s.wfile.write(d)
                    except BrokenPipeError: break
                    n-=len(d)
            return
        super().do_GET()
ThreadingHTTPServer(("0.0.0.0",int(sys.argv[4])),H).serve_forever()
