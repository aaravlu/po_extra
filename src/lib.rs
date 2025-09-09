mod utils;

use crate::utils::{collect_some_html_element, get_body, init_logging, init_tokio_rt};
use log::info;

const BASE_URL: &str = "https://mp.weixin.qq.com/";
const TAG_TO_COLLECT: &str = "a";

pub fn run() -> anyhow::Result<()> {
    init_logging();
    info!("logging initialized");

    let rt = init_tokio_rt()?;
    info!("tokio rt initialized");

    let body = rt.block_on(get_body(BASE_URL))?;
    let _html_elements = collect_some_html_element(&body, TAG_TO_COLLECT);
    Ok(())
}
