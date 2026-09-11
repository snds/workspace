use axum::{
    extract::{Path, State},
    http::{header, HeaderMap, StatusCode},
    response::{IntoResponse, Json, Response},
    routing::get,
    Router,
};
use clap::Parser;
use fontdb::{Database, Source, Style};
use serde::{Deserialize, Serialize};
use std::{
    net::SocketAddr,
    path::PathBuf,
    sync::Arc,
};
use tower_http::cors::{Any, CorsLayer};

// ─── CLI ─────────────────────────────────────────────────────────────────────

#[derive(Parser, Debug)]
#[command(
    name = "omni-fonts",
    about = "Local font server for the Omni design tool",
    long_about = "Scans system fonts (and optional custom directories) and serves them \
                  over HTTP so that Omni can use locally-installed fonts in the canvas."
)]
struct Args {
    /// Port to listen on
    #[arg(short, long, default_value_t = 37291)]
    port: u16,

    /// Additional font directories to scan (can be specified multiple times)
    #[arg(short = 'd', long = "dir", value_name = "PATH")]
    dirs: Vec<PathBuf>,

    /// Skip scanning the OS system font directories
    #[arg(long)]
    no_system: bool,
}

// ─── Data model ───────────────────────────────────────────────────────────────

#[derive(Serialize, Clone)]
struct FontInfo {
    /// Stable integer ID used to request the font bytes
    id: usize,
    family: String,
    style: String,
    weight: u16,
    italic: bool,
    format: String,
}

struct FontEntry {
    info: FontInfo,
    /// Raw font bytes (always in memory — makes serving trivial and avoids
    /// path traversal by never exposing file system paths to callers)
    bytes: Arc<Vec<u8>>,
}

struct AppState {
    fonts: Vec<FontEntry>,
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

/// Detect the font format from the first four magic bytes.
fn detect_format(bytes: &[u8]) -> (&'static str, &'static str) {
    if bytes.len() < 4 {
        return ("truetype", "font/ttf");
    }
    match bytes[..4] {
        [0x4F, 0x54, 0x54, 0x4F] => ("opentype",  "font/otf"),
        [0x77, 0x4F, 0x46, 0x46] => ("woff",      "font/woff"),
        [0x77, 0x4F, 0x46, 0x32] => ("woff2",     "font/woff2"),
        _                         => ("truetype",  "font/ttf"),
    }
}

/// Human-readable style name from weight + italic flag.
fn style_name(weight: u16, italic: bool) -> String {
    let weight_name = match weight {
        100 => "Thin",
        200 => "ExtraLight",
        300 => "Light",
        400 => "Regular",
        500 => "Medium",
        600 => "SemiBold",
        700 => "Bold",
        800 => "ExtraBold",
        900 => "Black",
        w   => return format!("{}{}", w, if italic { " Italic" } else { "" }),
    };
    if italic {
        if weight == 400 {
            "Italic".to_string()
        } else {
            format!("{} Italic", weight_name)
        }
    } else {
        weight_name.to_string()
    }
}

// ─── Font loading ─────────────────────────────────────────────────────────────

fn collect_fonts(db: &Database) -> Vec<FontEntry> {
    let mut entries: Vec<FontEntry> = Vec::new();

    for face in db.faces() {
        // Pick the English family name, or the first available one.
        let family = face
            .families
            .iter()
            .find(|(_, lang)| *lang == fontdb::Language::English_UnitedStates)
            .or_else(|| face.families.first())
            .map(|(name, _)| name.clone())
            .unwrap_or_default();

        if family.is_empty() {
            continue;
        }

        let weight = face.weight.0;
        let italic = face.style == Style::Italic;

        // Extract raw bytes from the font source.
        let bytes: Option<Vec<u8>> = match &face.source {
            Source::File(path) => std::fs::read(path).ok(),
            Source::SharedFile(_, data) => Some(data.as_ref().to_vec()),
            Source::Binary(data) => Some(data.as_ref().as_ref().to_vec()),
        };

        let Some(bytes) = bytes else { continue };
        if bytes.is_empty() {
            continue;
        }

        let (format, _) = detect_format(&bytes);
        let id = entries.len();

        entries.push(FontEntry {
            info: FontInfo {
                id,
                family,
                style: style_name(weight, italic),
                weight,
                italic,
                format: format.to_string(),
            },
            bytes: Arc::new(bytes),
        });
    }

    // Sort by family name then weight for nicer output
    entries.sort_by(|a, b| {
        a.info.family.cmp(&b.info.family)
            .then(a.info.weight.cmp(&b.info.weight))
            .then(a.info.italic.cmp(&b.info.italic))
    });

    // Re-assign IDs after sorting so they match the Vec index
    for (i, entry) in entries.iter_mut().enumerate() {
        entry.info.id = i;
    }

    entries
}

// ─── Handlers ─────────────────────────────────────────────────────────────────

async fn health() -> Json<serde_json::Value> {
    Json(serde_json::json!({ "status": "ok", "version": env!("CARGO_PKG_VERSION") }))
}

async fn list_fonts(State(state): State<Arc<AppState>>) -> Json<Vec<FontInfo>> {
    Json(state.fonts.iter().map(|e| e.info.clone()).collect())
}

async fn serve_font(
    State(state): State<Arc<AppState>>,
    Path(id): Path<usize>,
) -> Response {
    let Some(entry) = state.fonts.get(id) else {
        return (StatusCode::NOT_FOUND, "Font not found").into_response();
    };

    let (_, content_type) = detect_format(&entry.bytes);
    let bytes = entry.bytes.as_ref().clone();

    let mut headers = HeaderMap::new();
    headers.insert(header::CONTENT_TYPE, content_type.parse().unwrap());
    // Allow browsers to cache the font for 7 days
    headers.insert(
        header::CACHE_CONTROL,
        "public, max-age=604800, immutable".parse().unwrap(),
    );

    (StatusCode::OK, headers, bytes).into_response()
}

// ─── Main ─────────────────────────────────────────────────────────────────────

#[tokio::main]
async fn main() {
    let args = Args::parse();

    println!("omni-fonts v{}", env!("CARGO_PKG_VERSION"));
    println!("Scanning fonts…");

    let mut db = Database::new();

    if !args.no_system {
        db.load_system_fonts();
        println!("  ✓ System fonts loaded");
    }

    for dir in &args.dirs {
        if dir.is_dir() {
            db.load_fonts_dir(dir);
            println!("  ✓ Custom dir: {}", dir.display());
        } else {
            eprintln!("  ✗ Not a directory (skipped): {}", dir.display());
        }
    }

    let fonts = collect_fonts(&db);
    let count = fonts.len();
    let state = Arc::new(AppState { fonts });

    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods(Any)
        .allow_headers(Any);

    let app = Router::new()
        .route("/",          get(health))
        .route("/fonts",     get(list_fonts))
        .route("/font/:id",  get(serve_font))
        .layer(cors)
        .with_state(state);

    let addr: SocketAddr = format!("127.0.0.1:{}", args.port).parse().unwrap();
    let listener = tokio::net::TcpListener::bind(addr).await.unwrap_or_else(|e| {
        eprintln!("Failed to bind to {addr}: {e}");
        std::process::exit(1);
    });

    println!("  ✓ {count} font faces indexed");
    println!();
    println!("Listening on http://127.0.0.1:{}", args.port);
    println!("  GET /           health check");
    println!("  GET /fonts      JSON list of all font faces");
    println!("  GET /font/:id   serve font bytes by ID");
    println!();
    println!("Run with --help for options (--port, --dir, --no-system)");

    axum::serve(listener, app).await.unwrap();
}
