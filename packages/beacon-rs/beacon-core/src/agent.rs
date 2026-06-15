use serde::{Deserialize, Serialize};

/// AC-042 iteration output contract.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct IterationResult {
    pub success: bool,
    pub summary: String,
    pub key_changes_made: Vec<String>,
    pub key_learnings: Vec<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub stop_signal: Option<String>,
    pub token_usage: TokenUsage,
    pub agent_name: String,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Default, Serialize, Deserialize)]
pub struct TokenUsage {
    pub input_tokens: u64,
    pub output_tokens: u64,
}

/// AC-042 agent backend trait (implementations in beacon-orchestrator P2+).
pub trait AgentBackend: Send + Sync {
    fn name(&self) -> &str;
    fn health_check(&self) -> Result<(), String>;
    fn iterate(&mut self, prompt: &str) -> Result<IterationResult, String>;
    fn abort(&mut self) -> Result<(), String>;
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn iteration_result_schema_fields() {
        let result = IterationResult {
            success: true,
            summary: "done".into(),
            key_changes_made: vec!["a".into()],
            key_learnings: vec![],
            stop_signal: None,
            token_usage: TokenUsage {
                input_tokens: 1,
                output_tokens: 2,
            },
            agent_name: "test".into(),
        };
        let json = serde_json::to_value(&result).unwrap();
        for key in [
            "success",
            "summary",
            "key_changes_made",
            "key_learnings",
            "token_usage",
            "agent_name",
        ] {
            assert!(json.get(key).is_some(), "missing field {key}");
        }
    }
}
