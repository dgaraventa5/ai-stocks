/* Shared-password gate for the whole site (Cloudflare Pages advanced mode).
   SITE_PASSWORD is a Cloudflare Pages environment variable / secret. */

const COOKIE = 'gate';

async function token(env) {
  const data = new TextEncoder().encode(`${env.SITE_PASSWORD}|gate-v1`);
  const hash = await crypto.subtle.digest('SHA-256', data);
  return [...new Uint8Array(hash)].map(b => b.toString(16).padStart(2, '0')).join('');
}

function loginPage(msg) {
  return `<!DOCTYPE html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow"><title>AI Supply Chain</title>
<style>
body{margin:0;background:#0d1117;color:#e6edf3;font-family:Menlo,monospace;
display:flex;align-items:center;justify-content:center;min-height:100vh}
form{background:#161b22;border:1px solid #30363d;border-radius:6px;
padding:28px;width:300px}
h1{font-size:14px;letter-spacing:1px;margin:0 0 16px}
input{width:100%;box-sizing:border-box;background:#0d1117;color:#e6edf3;
border:1px solid #30363d;border-radius:6px;padding:8px;font-family:inherit}
button{margin-top:10px;width:100%;background:#238636;color:#fff;border:0;
border-radius:6px;padding:8px;font-family:inherit;cursor:pointer}
.err{color:#f85149;font-size:12px;margin-top:8px}
</style></head><body>
<form method="POST" action="/login">
<h1>AI SUPPLY CHAIN</h1>
<input type="password" name="password" placeholder="password" autofocus>
<button>enter</button>${msg ? `<div class="err">${msg}</div>` : ''}
</form></body></html>`;
}

export default {
  async fetch(request, env) {
    if (!env.SITE_PASSWORD) {
      return new Response('SITE_PASSWORD not configured', { status: 500 });
    }
    const url = new URL(request.url);
    const expected = await token(env);
    const cookies = request.headers.get('Cookie') || '';

    if (cookies.includes(`${COOKIE}=${expected}`)) {
      return env.ASSETS.fetch(request);
    }
    if (request.method === 'POST' && url.pathname === '/login') {
      const form = await request.formData();
      if (form.get('password') === env.SITE_PASSWORD) {
        return new Response(null, {
          status: 302,
          headers: {
            'Location': '/',
            'Set-Cookie': `${COOKIE}=${expected}; HttpOnly; Secure; ` +
                          'SameSite=Lax; Max-Age=31536000; Path=/',
          },
        });
      }
      return new Response(loginPage('wrong password'), {
        status: 401, headers: { 'Content-Type': 'text/html' } });
    }
    return new Response(loginPage(''), {
      status: 401, headers: { 'Content-Type': 'text/html' } });
  },
};
