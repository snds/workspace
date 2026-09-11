use std::fs;
use std::path::PathBuf;
use tauri::AppHandle;
use tauri::Manager;

fn projects_dir(app: &AppHandle) -> Result<PathBuf, String> {
    let data_dir = app
        .path()
        .app_data_dir()
        .map_err(|e| e.to_string())?;
    let dir = data_dir.join("projects");
    fs::create_dir_all(&dir).map_err(|e| e.to_string())?;
    Ok(dir)
}

#[tauri::command]
pub fn read_project(app: AppHandle, id: String) -> Result<String, String> {
    let path = projects_dir(&app)?.join(format!("{}.json", id));
    fs::read_to_string(&path).map_err(|e| e.to_string())
}

#[tauri::command]
pub fn write_project(app: AppHandle, id: String, json: String) -> Result<(), String> {
    let path = projects_dir(&app)?.join(format!("{}.json", id));
    fs::write(&path, json).map_err(|e| e.to_string())
}

#[tauri::command]
pub fn list_projects(app: AppHandle) -> Result<Vec<String>, String> {
    let dir = projects_dir(&app)?;
    let mut ids = Vec::new();
    for entry in fs::read_dir(&dir).map_err(|e| e.to_string())? {
        let entry = entry.map_err(|e| e.to_string())?;
        let name = entry.file_name().to_string_lossy().to_string();
        if name.ends_with(".json") {
            ids.push(name.trim_end_matches(".json").to_string());
        }
    }
    Ok(ids)
}
