# HTTPS with Caddy

ExpertGPTs (Streamlit) serves plain HTTP on port 8501. To run it over HTTPS on a server,
put [Caddy](https://caddyserver.com/) in front of it as a reverse proxy: Caddy
terminates TLS for your domain, gets and renews the certificate itself, and forwards
requests (including Streamlit's websocket) to Streamlit, which then listens on
localhost only.

```
Browser ──HTTPS──▶ Caddy :443 (your domain) ──HTTP──▶ Streamlit 127.0.0.1:8501
```

The steps below use Debian/Ubuntu and systemd; on other systems the Caddy part is the
same, only the installation and service commands differ.

## Files in the repository

| File | Purpose |
|---|---|
| `deploy/caddy/Caddyfile` | Caddy configuration, installed as `/etc/caddy/Caddyfile`. Domain and upstream come from environment variables; the certificate method is chosen by enabling one `tls` block. |
| `deploy/caddy/acmedns.json.example` | Format of the acme-dns credentials file, only needed for the acme-dns method. The real file holds a password; `deploy/caddy/acmedns.json` is gitignored. |

The Caddyfile reads two environment variables:

| Variable | Meaning |
|---|---|
| `EXPERTGPTS_DOMAIN` | Domain the app is served on, e.g. `chat.example.com` (required) |
| `EXPERTGPTS_UPSTREAM` | Address of Streamlit (default `127.0.0.1:8501`) |

## Choose a certificate method

| Situation | Method | `tls` block in the Caddyfile |
|---|---|---|
| The domain is reachable from the internet on ports 80 and 443 | Let's Encrypt, HTTP challenge | none (default) |
| The name only exists in your local network, and your DNS provider has a Caddy plugin | Let's Encrypt, DNS challenge with the provider's API | `dns <provider> …` |
| Local network only, DNS provider without a Caddy plugin | Let's Encrypt, DNS challenge through [acme-dns](https://github.com/joohoi/acme-dns) | `dns acmedns …` |
| No public domain at all | Caddy's local CA | `tls internal` |

With the DNS challenge, Let's Encrypt never connects to the server: Caddy proves control
of the domain with a TXT record under `_acme-challenge.<domain>`. That is why it works
for names that only resolve inside a local network.

- **DNS provider plugin:** the plugins are listed at
  [github.com/caddy-dns](https://github.com/caddy-dns). Each README shows its
  `dns <provider>` options, usually an API token.
- **acme-dns:** for providers without a plugin. `_acme-challenge.<domain>` becomes a
  permanent CNAME to a subdomain on an acme-dns server (the public `auth.acme-dns.io` or
  your own), and Caddy writes the TXT record there with plugin
  [`caddy-dns/acmedns`](https://github.com/caddy-dns/acmedns). Your DNS zone only needs
  that one CNAME, once.
- **`tls internal`:** no DNS changes, but every client (computer, phone) has to trust
  Caddy's root certificate once, or the browser shows a warning. Caddy stores it under
  `/var/lib/caddy/.local/share/caddy/pki/authorities/local/root.crt`.

## Setup

### 1. Install Caddy

Install Caddy from the official repository (it brings the `caddy` user and the
`caddy.service` systemd unit):

```bash
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' \
  | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' \
  | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo chmod o+r /usr/share/keyrings/caddy-stable-archive-keyring.gpg /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy
```

### 2. Add a DNS plugin (DNS challenge only)

The packaged binary has no DNS plugins. Replace it with a build that includes the
plugin, and keep apt from overwriting it:

```bash
sudo caddy add-package github.com/caddy-dns/acmedns    # or e.g. github.com/caddy-dns/cloudflare
sudo apt-mark hold caddy
caddy list-modules | grep dns.providers
```

Update Caddy later with `sudo caddy upgrade`, which keeps the plugin. Alternatively,
build the binary with [xcaddy](https://github.com/caddyserver/xcaddy).

### 3. Set up the DNS challenge

Skip this for the HTTP challenge and `tls internal`.

**With a provider plugin:** create an API token as described in the plugin's README and
pass it to Caddy as an environment variable (step 4), for example
`CLOUDFLARE_API_TOKEN`.

**With acme-dns:**

1. Register:

   ```bash
   curl -s -X POST https://auth.acme-dns.io/register
   ```

   The answer contains `username`, `password`, `fulldomain` and `subdomain`. Keep it:
   the password can't be retrieved again.

2. At your DNS provider, add a CNAME record:

   | Type | Name | Value |
   |---|---|---|
   | CNAME | `_acme-challenge.<domain>` | `<fulldomain>` from the registration |

   Check it with `dig +short CNAME _acme-challenge.<domain>`.

3. Store the credentials in `/etc/caddy/acmedns.json`, in the format of
   `deploy/caddy/acmedns.json.example`, readable only by root and the `caddy` group:

   ```bash
   sudo nano /etc/caddy/acmedns.json
   sudo chown root:caddy /etc/caddy/acmedns.json
   sudo chmod 640 /etc/caddy/acmedns.json
   ```

### 4. Configure and start Caddy

Set the environment variables for the Caddy service:

```bash
sudo systemctl edit caddy
```

```ini
[Service]
Environment=EXPERTGPTS_DOMAIN=chat.example.com
# Environment=EXPERTGPTS_UPSTREAM=127.0.0.1:8501
# Environment=CLOUDFLARE_API_TOKEN=…   (DNS provider plugin only)
```

Install the Caddyfile and enable the `tls` block of your method (none for the HTTP
challenge):

```bash
sudo cp deploy/caddy/Caddyfile /etc/caddy/Caddyfile
sudo nano /etc/caddy/Caddyfile
sudo systemctl restart caddy
journalctl -u caddy -f      # until "certificate obtained successfully"
```

`caddy validate --config /etc/caddy/Caddyfile` checks the file before a restart; it
needs the same environment variables in the shell.

### 5. Bind Streamlit to localhost

So that ExpertGPTs is only reachable through Caddy, start Streamlit with
`--server.address 127.0.0.1`, for example in its systemd unit:

```
ExecStart=… uv run streamlit run app.py --server.address 127.0.0.1
```

```bash
sudo systemctl daemon-reload
sudo systemctl restart <your ExpertGPTs service>
curl -s localhost:8501/_stcore/health      # → ok
```

If Caddy runs on another machine, keep Streamlit on its network address instead and
set `EXPERTGPTS_UPSTREAM` to it.

### 6. Name resolution and firewall

- **Local network only:** the clients must resolve the domain to the server's local
  address, through a local DNS entry (router, Pi-hole, internal DNS) or `/etc/hosts`.
  If the domain also has a public DNS record, the local entry takes precedence for
  these clients.
- **Firewall:** allow ports 80 and 443 to the server (for example
  `sudo ufw allow 80,443/tcp`). Port 80 redirects to HTTPS and serves the HTTP challenge.

### 7. Verify

From a client:

```bash
curl -s https://<domain>/_stcore/health     # → ok, no certificate warning
```

Then open `https://<domain>` in the browser and send a chat message: the answer streams
through the websocket.

## Renewal

Caddy renews Let's Encrypt certificates automatically about 30 days before they expire,
with the same method. For the DNS challenge, the plugin credentials (and for acme-dns
the CNAME) have to stay in place.

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `module not registered: dns.providers.<name>` | The binary lacks the plugin. Repeat step 2; `caddy list-modules \| grep dns.providers` must list it. |
| `unrecognized global option: reverse_proxy` | `EXPERTGPTS_DOMAIN` isn't set, so the site block has no address. Set it for the service (step 4), and in the shell for `caddy validate`. |
| HTTP challenge fails | The domain must point to the server publicly and ports 80/443 must be reachable from the internet. Otherwise use a DNS challenge. |
| DNS challenge fails or times out | Check the provider token, or for acme-dns the CNAME (`dig +short CNAME _acme-challenge.<domain>`) and `/etc/caddy/acmedns.json` (owner `root:caddy`, mode `640`). |
| Browser reaches another server or shows a certificate for another name | The client resolves the domain to a different address. Check the local DNS entry (step 6). |
| `502 Bad Gateway` | Streamlit isn't running or listens on another address: `curl <upstream>/_stcore/health`. |

---

**Related**: [Configuration Overview](overview.md) · [API Keys](api-keys.md)
