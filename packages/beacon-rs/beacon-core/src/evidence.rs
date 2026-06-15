use serde::{Deserialize, Serialize};

/// AC-037 evidence chain primitive.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct EvidenceChain {
    pub manifest_hash: String,
    pub signature_chain: Vec<String>,
    pub artifact_refs: Vec<String>,
}

impl EvidenceChain {
    pub fn verify_links(&self) -> Result<(), crate::error::BeaconError> {
        if self.manifest_hash.is_empty() {
            return Err(crate::error::BeaconError::EvidenceChainBroken);
        }
        Ok(())
    }
}
