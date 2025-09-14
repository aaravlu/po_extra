use crate::utils::get_config_content;
use serde::{Deserialize, Serialize};

/// Configuration structure that holds application settings
#[derive(Debug, Serialize, Deserialize, Clone, PartialEq)]
pub struct Config {
    /// Base URL for API requests
    base_url: String,

    /// Model name to use for requests
    model_id: String,

    /// API key for authentication
    api_key: String,
}

impl Config {
    /// Load the configuration from the default path.
    /// Creates a default config file if one doesn't exist.
    pub fn load() -> anyhow::Result<Self> {
        let config_content = get_config_content()?;
        let config = toml::from_str(&config_content)?;

        Ok(config)
    }

    pub fn base_url(&self) -> &str {
        &self.base_url
    }
    pub fn model_id(&self) -> &str {
        &self.model_id
    }
    pub fn api_key(&self) -> &str {
        &self.api_key
    }
}
