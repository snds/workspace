use serde::{Deserialize, Serialize};
use tauri::ipc::Channel;

#[derive(Debug, Serialize, Deserialize)]
pub struct MessageParam {
    pub role: String,
    pub content: String,
}

#[tauri::command]
pub async fn ai_stream_message(
    system_prompt: String,
    messages: Vec<MessageParam>,
    max_tokens: Option<u32>,
    model: Option<String>,
    channel: Channel<String>,
) -> Result<(), String> {
    // Read API key: try environment variable first, then OS keychain
    let api_key = std::env::var("ANTHROPIC_API_KEY").ok().or_else(|| {
        keyring::Entry::new("omni", "anthropic_api_key")
            .ok()
            .and_then(|e| e.get_password().ok())
    });

    let api_key = api_key.ok_or_else(|| {
        "No API key found. Set the ANTHROPIC_API_KEY environment variable or store it via Settings → AI.".to_string()
    })?;

    let model_str = model.unwrap_or_else(|| "claude-opus-4-6".to_string());

    // Build request body
    let body = serde_json::json!({
        "model": model_str,
        "max_tokens": max_tokens.unwrap_or(8096),
        "system": system_prompt,
        "messages": messages.iter().map(|m| serde_json::json!({
            "role": m.role,
            "content": m.content
        })).collect::<Vec<_>>(),
        "stream": true
    });

    let client = reqwest::Client::new();
    let response = client
        .post("https://api.anthropic.com/v1/messages")
        .header("x-api-key", &api_key)
        .header("anthropic-version", "2023-06-01")
        .header("content-type", "application/json")
        .json(&body)
        .send()
        .await
        .map_err(|e| format!("Request error: {e}"))?;

    if !response.status().is_success() {
        let status = response.status();
        let body_text = response.text().await.unwrap_or_default();
        channel
            .send(format!("__ERROR__:HTTP {status}: {body_text}"))
            .ok();
        return Err(format!("HTTP {status}"));
    }

    // Stream SSE events
    use futures_util::StreamExt;
    let mut stream = response.bytes_stream();

    while let Some(chunk) = stream.next().await {
        let chunk = chunk.map_err(|e| format!("Stream error: {e}"))?;
        let text = String::from_utf8_lossy(&chunk);

        for line in text.lines() {
            if let Some(data) = line.strip_prefix("data: ") {
                if data == "[DONE]" {
                    channel.send("__DONE__".to_string()).ok();
                    return Ok(());
                }
                if let Ok(json) = serde_json::from_str::<serde_json::Value>(data) {
                    if let Some(delta_text) = json
                        .get("delta")
                        .and_then(|d| d.get("text"))
                        .and_then(|t| t.as_str())
                    {
                        channel.send(delta_text.to_string()).ok();
                    }
                }
            }
        }
    }

    channel.send("__DONE__".to_string()).ok();
    Ok(())
}
