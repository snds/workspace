# omni-fonts

A tiny HTTP server that exposes locally-installed fonts to the Omni design tool.

## Why?

Web apps can't read the OS font directory directly. `omni-fonts` bridges that gap by
scanning your system fonts (and any extra directories you point it at) and serving
them over a local HTTP API that Omni can reach via `localhost:37291`.

## Usage

```sh
# Download the pre-built binary for your platform, then run:
./omni-fonts

# Options
./omni-fonts --port 37291          # default port
./omni-fonts --dir ~/MyFonts       # add a custom font directory
./omni-fonts --no-system           # skip OS system fonts (only custom dirs)
./omni-fonts -d ~/A -d ~/B         # multiple custom directories
```

## API

| Endpoint        | Description                                      |
|-----------------|--------------------------------------------------|
| `GET /`         | Health check — `{ "status": "ok", "version": "…" }` |
| `GET /fonts`    | JSON array of all discovered font faces          |
| `GET /font/:id` | Serve the raw font bytes for the face with `id`  |

### Example `/fonts` response

```json
[
  { "id": 0, "family": "Helvetica Neue", "style": "Regular",     "weight": 400, "italic": false, "format": "truetype" },
  { "id": 1, "family": "Helvetica Neue", "style": "Bold",        "weight": 700, "italic": false, "format": "truetype" },
  { "id": 2, "family": "Helvetica Neue", "style": "Bold Italic", "weight": 700, "italic": true,  "format": "truetype" }
]
```

## Building from source

```sh
cargo build --release
# Binary at: target/release/omni-fonts
```

Cross-compilation targets:
```sh
# macOS (Apple Silicon)
cargo build --release --target aarch64-apple-darwin

# macOS (Intel)
cargo build --release --target x86_64-apple-darwin

# Windows
cargo build --release --target x86_64-pc-windows-gnu

# Linux
cargo build --release --target x86_64-unknown-linux-gnu
```

## System font directories scanned by default

| Platform | Directories                                                    |
|----------|----------------------------------------------------------------|
| macOS    | `/Library/Fonts`, `~/Library/Fonts`, `/System/Library/Fonts`  |
| Windows  | `C:\Windows\Fonts`, `%LOCALAPPDATA%\Microsoft\Windows\Fonts`   |
| Linux    | `/usr/share/fonts`, `/usr/local/share/fonts`, `~/.fonts`, `~/.local/share/fonts` |

(`fontdb` handles the platform detection automatically.)
