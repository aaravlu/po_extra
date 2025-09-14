mod config;
mod utils;

use crate::config::Config;
use crate::utils::{collect_some_html_element, get_body, init_logging, init_tokio_rt};
use log::info;

const TARGET_URL: &str = "https://mp.weixin.qq.com/";
const TAG_TO_COLLECT: &str = "a";

pub fn run() -> anyhow::Result<()> {
    // Initialize logging
    init_logging();
    info!("logging initialized");

    // Initialize tokio runtime
    let rt = init_tokio_rt()?;
    info!("tokio rt initialized");

    // Load configuration
    let config = Config::load()?;
    info!("Config loaded");

    let body = rt.block_on(get_body(TARGET_URL))?;
    let html_elements = collect_some_html_element(&body, TAG_TO_COLLECT);
    let user_prompt = html_elements
        .into_iter()
        .map(|s| s.into())
        .collect::<Vec<String>>()
        .join("\n");

    Ok(())
}
