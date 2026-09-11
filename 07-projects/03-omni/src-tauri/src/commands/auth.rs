use keyring::Entry;

#[tauri::command]
pub fn auth_store_token(service: String, token: String) -> Result<(), String> {
    let entry = Entry::new("omni", &service).map_err(|e| e.to_string())?;
    entry.set_password(&token).map_err(|e| e.to_string())
}

#[tauri::command]
pub fn auth_get_token(service: String) -> Result<Option<String>, String> {
    let entry = Entry::new("omni", &service).map_err(|e| e.to_string())?;
    match entry.get_password() {
        Ok(token) => Ok(Some(token)),
        Err(keyring::Error::NoEntry) => Ok(None),
        Err(e) => Err(e.to_string()),
    }
}

#[tauri::command]
pub fn auth_delete_token(service: String) -> Result<(), String> {
    let entry = Entry::new("omni", &service).map_err(|e| e.to_string())?;
    match entry.delete_credential() {
        Ok(()) => Ok(()),
        Err(keyring::Error::NoEntry) => Ok(()), // Already gone — not an error
        Err(e) => Err(e.to_string()),
    }
}
