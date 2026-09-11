mod commands;

use commands::{
    ai::ai_stream_message,
    auth::{auth_delete_token, auth_get_token, auth_store_token},
    project::{list_projects, read_project, write_project},
};

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![
            // AI
            ai_stream_message,
            // Auth / keychain
            auth_store_token,
            auth_get_token,
            auth_delete_token,
            // Project persistence
            read_project,
            write_project,
            list_projects,
        ])
        .run(tauri::generate_context!())
        .expect("error while running Omni");
}
