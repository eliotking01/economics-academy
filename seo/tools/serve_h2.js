// Serve a tree over HTTP/2 + TLS + gzip, the way GitHub Pages (Fastly) does,
// for a local Lighthouse A/B.
//
//   node seo/tools/serve_h2.js DIR PORT CERT KEY
//
// Why not python -m http.server: it is HTTP/1.0 with no keep-alive and no
// compression, and Lighthouse's simulator then charges a fresh connection per
// request and the uncompressed bytes. An HTTP/1.1 server fixes that but still
// models six connections per origin, so anything self-hosted contends with the
// page's own CSS and JS in a way it never does over HTTP/2 - which made the
// self-hosted fonts measure SLOWER than fetching them from fonts.gstatic.com
// (2026-08-23). Pages serves HTTP/2; so does this. Chrome needs TLS for h2,
// hence the self-signed certificate, and Lighthouse is run with
// --ignore-certificate-errors (run_lighthouse.py --insecure). Node built-ins
// only.
const http2 = require("http2");
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const [root, port, cert, key] = process.argv.slice(2);
const TYPES = {
  ".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8", ".json": "application/json",
  ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg", ".webp": "image/webp", ".gif": "image/gif",
  ".ico": "image/x-icon", ".woff2": "font/woff2", ".woff": "font/woff",
  ".xml": "application/xml", ".webmanifest": "application/manifest+json",
  ".txt": "text/plain; charset=utf-8", ".pdf": "application/pdf",
};
const COMPRESS = new Set([".html", ".css", ".js", ".json", ".svg", ".xml", ".webmanifest", ".txt"]);

const server = http2.createSecureServer({
  cert: fs.readFileSync(cert), key: fs.readFileSync(key), allowHTTP1: true,
});
server.on("stream", (stream, headers) => {
  const url = decodeURIComponent((headers[":path"] || "/").split("?")[0]);
  let file = path.join(root, url);
  if (!file.startsWith(path.resolve(root))) { stream.respond({ ":status": 403 }); stream.end(); return; }
  try { if (fs.statSync(file).isDirectory()) file = path.join(file, "index.html"); } catch (e) {}
  if (!fs.existsSync(file) || !fs.statSync(file).isFile()) { stream.respond({ ":status": 404 }); stream.end("not found"); return; }
  const ext = path.extname(file).toLowerCase();
  let body = fs.readFileSync(file);
  const h = { ":status": 200, "content-type": TYPES[ext] || "application/octet-stream", "cache-control": "max-age=600" };
  const ae = String(headers["accept-encoding"] || "");
  if (COMPRESS.has(ext) && ae.includes("gzip")) { body = zlib.gzipSync(body, { level: 6 }); h["content-encoding"] = "gzip"; h["vary"] = "Accept-Encoding"; }
  h["content-length"] = body.length;
  stream.respond(h);
  stream.end(body);
});
server.listen(Number(port), "127.0.0.1", () => console.log(`serving ${root} on https://127.0.0.1:${port} (h2, gzip)`));
