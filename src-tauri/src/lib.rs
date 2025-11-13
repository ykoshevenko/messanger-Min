// #[cfg_attr(mobile, tauri::mobile_entry_point)]
// pub fn run() {
//   tauri::Builder::default()
//     .setup(|app| {
//       if cfg!(debug_assertions) {
//         app.handle().plugin(
//           tauri_plugin_log::Builder::default()
//             .level(log::LevelFilter::Info)
//             .build(),
//         )?;
//       }
//       Ok(())
//     })
//     .run(tauri::generate_context!())
//     .expect("error while running tauri application");
// }

use tauri::{plugin::Plugin, AppHandle, Runtime};
use std::process::Command;
use std::thread;
use std::time::Duration;
use serde_json::Value;

pub struct FastApiPlugin;

impl<R: Runtime> Plugin<R> for FastApiPlugin {
    fn name(&self) -> &'static str {
        "fastapi"
    }

    // Исправленная сигнатура - убрал & перед Value
    fn initialize(&mut self, _app: &AppHandle<R>, _config: Value) -> Result<(), Box<dyn std::error::Error>> {
        start_fastapi_server();
        Ok(())
    }

    fn initialization_script(&self) -> Option<String> {
        None
    }
}

fn start_fastapi_server() {
    thread::spawn(move || {
        thread::sleep(Duration::from_secs(2));
        
        let python_cmd = if cfg!(target_os = "windows") {
            "python"
        } else {
            "python3"
        };
        
        println!("Starting FastAPI server...");
        
        match Command::new(python_cmd)
            .arg("-m")
            .arg("uvicorn")
            .arg("main:app")
            .arg("--host")
            .arg("127.0.0.1")
            .arg("--port")
            .arg("8000")
            .current_dir("../backend")
            .spawn() {
                Ok(_) => println!("FastAPI server started successfully"),
                Err(e) => println!("Failed to start FastAPI server: {}", e),
            };
    });
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .setup(|app| {
            if cfg!(debug_assertions) {
                app.handle().plugin(
                    tauri_plugin_log::Builder::default()
                        .level(log::LevelFilter::Info)
                        .build(),
                )?;
            }
            Ok(())
        })
        .plugin(FastApiPlugin)
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}