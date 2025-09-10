use scraper::{Html, Selector};
use tokio::runtime::{Builder, Runtime};

pub fn init_logging() {
    env_logger::Builder::from_default_env()
        .format(|buf, record| {
            use std::io::Write;
            writeln!(
                buf,
                "[{} {}:{}] {}",
                record.level(),
                record.file().unwrap_or("unknown"),
                record.line().unwrap_or(0),
                record.args()
            )
        })
        .filter_level(log::LevelFilter::Info)
        .init();
}

pub fn init_tokio_rt() -> anyhow::Result<Runtime> {
    let rt = Builder::new_multi_thread().enable_io().build()?;
    Ok(rt)
}

pub struct HtmlElement {
    href: Box<str>,
    tag: Box<str>,
}
pub fn collect_some_html_element(body: &str, tag: &str) -> Vec<HtmlElement> {
    let document = Html::parse_document(body);
    let selector = Selector::parse(tag).unwrap();

    let mut html_elements = Vec::new();

    document.select(&selector).for_each(|element| {
        if let Some(href) = element.value().attr("href") {
            let tag = element.text().collect::<Vec<_>>().join(" ").trim().into();
            html_elements.push(HtmlElement {
                href: href.into(),
                tag,
            });
        }
    });
    html_elements
}

pub async fn get_body(url: &str) -> anyhow::Result<String> {
    let body = reqwest::get(url).await?.text().await?;
    Ok(body)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_collect_some_html_element_with_links() {
        let html = r#"
        <html>
            <body>
                <a href="https://example.com">Example Site</a>
                <a href="https://rust-lang.org">Rust</a>
                <div>Not a link</div>
            </body>
        </html>
        "#;

        let elements = collect_some_html_element(html, "a");

        assert_eq!(elements.len(), 2);
        assert_eq!(elements[0].href.as_ref(), "https://example.com");
        assert_eq!(elements[0].tag.as_ref(), "Example Site");
        assert_eq!(elements[1].href.as_ref(), "https://rust-lang.org");
        assert_eq!(elements[1].tag.as_ref(), "Rust");
    }

    #[test]
    fn test_collect_some_html_element_no_links() {
        let html = r#"
        <html>
            <body>
                <div>No links here</div>
                <span>Just text</span>
            </body>
        </html>
        "#;

        let elements = collect_some_html_element(html, "a");
        assert_eq!(elements.len(), 0);
    }

    #[test]
    fn test_collect_some_html_element_malformed_html() {
        let html = r#"
        <html>
            <body>
                <a href="https://example.com">Unclosed tag
                <div>Missing closing tags
            </body>
        "#;

        let elements = collect_some_html_element(html, "a");
        assert_eq!(elements.len(), 1);
        assert_eq!(elements[0].href.as_ref(), "https://example.com");
    }

    #[test]
    fn test_collect_some_html_element_complex_selector() {
        let html = r#"
        <html>
            <body>
                <div class="container">
                    <a href="https://example.com" class="link">Example</a>
                </div>
                <a href="https://rust-lang.org">Rust</a>
            </body>
        </html>
        "#;

        // Test complex CSS selector
        let elements = collect_some_html_element(html, "div.container a.link");
        assert_eq!(elements.len(), 1);
        assert_eq!(elements[0].href.as_ref(), "https://example.com");
        assert_eq!(elements[0].tag.as_ref(), "Example");
    }

    #[test]
    fn test_collect_some_html_element_with_nested_content() {
        let html = r#"
        <html>
            <body>
                <a href="https://example.com">Example<span>with nested</span>content</a>
            </body>
        </html>
        "#;

        let elements = collect_some_html_element(html, "a");
        assert_eq!(elements.len(), 1);
        assert_eq!(elements[0].href.as_ref(), "https://example.com");
        assert_eq!(elements[0].tag.as_ref(), "Example with nested content");
    }

    #[tokio::test]
    async fn test_get_body_invalid_url() {
        let result = get_body("invalid://url").await;
        assert!(result.is_err());
    }
}
