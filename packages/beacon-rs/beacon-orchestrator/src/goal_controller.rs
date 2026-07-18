//! Goal run controller on store — create/status/resume/stop (P2-001).
//! Never auto-completes or auto-releases (verifier + human release).

use beacon_core::trace_spine::{TraceContext, TraceSpine};
use beacon_core::RunStatus;
use beacon_store::{
    BeaconStore, FeatureDao, LifecycleEventDao, ProjectDao, RunDao, SpineDao, SpineSnapshot,
};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GoalRunHandle {
    pub run_id: i64,
    pub feature_package_id: i64,
    pub status: String,
    pub phase: String,
    pub blocked: bool,
    pub reason_code: String,
    pub release_human_gate: bool,
    pub verifier_required: bool,
}

pub struct GoalController<'a> {
    store: &'a BeaconStore,
}

impl<'a> GoalController<'a> {
    pub fn new(store: &'a BeaconStore) -> Self {
        Self { store }
    }

    pub fn create(
        &self,
        project_root: &str,
        project_name: &str,
        feature_slug: &str,
        version: &str,
        utterance: &str,
    ) -> Result<GoalRunHandle, String> {
        let conn = self.store.connection();
        let project = ProjectDao::register(conn, project_root, project_name)
            .map_err(|e| format!("project register: {e}"))?;
        let feature_id = match FeatureDao::find_by_slug_version(conn, feature_slug, version)
            .map_err(|e| format!("feature find: {e}"))?
        {
            Some(row) => row.id,
            None => FeatureDao::insert(conn, project.id, feature_slug, version, "draft", None)
                .map_err(|e| format!("feature insert: {e}"))?,
        };
        let run_id = RunDao::insert(conn, feature_id, "goal", RunStatus::Running)
            .map_err(|e| format!("run insert: {e}"))?;

        let mut spine = SpineSnapshot {
            run_id,
            project_key: project.project_key.clone(),
            project_root: project_root.into(),
            version: version.into(),
            feature_slug: feature_slug.into(),
            lifecycle_stage: "plan".into(),
            lifecycle_status: "running".into(),
            phase: "plan".into(),
            phases_completed: vec![],
            phase_promoted: false,
            next_harness: "truth".into(),
            next_action: utterance.chars().take(120).collect(),
            progress_status: "running".into(),
            active_run_id: run_id.to_string(),
            run_status: RunStatus::Running.as_str().into(),
            iteration: 0,
            gate_results: vec![],
            artifact_refs: vec![],
            blocking_reason_codes: vec![],
            updated_at: now_secs(),
        };
        // Seed TraceSpine authority (in-memory proof object; path storage is P3)
        let mut trace = TraceSpine::create(run_id.to_string(), TraceContext::new(run_id.to_string()));
        let _ = trace.append("decision", "goal_created", format!("run:{run_id}"));
        spine.artifact_refs.push(beacon_store::ArtifactRef {
            path: format!("trace://{run_id}"),
            content_hash: trace.head_hash.clone(),
            stale: false,
        });

        let json = serde_json::to_string(&spine).map_err(|e| e.to_string())?;
        SpineDao::save(conn, run_id, &json).map_err(|e| e.to_string())?;
        LifecycleEventDao::insert(
            conn,
            Some(run_id),
            feature_id,
            "GoalCreated",
            Some(&serde_json::json!({ "utterance": utterance }).to_string()),
        )
        .map_err(|e| e.to_string())?;

        Ok(GoalRunHandle {
            run_id,
            feature_package_id: feature_id,
            status: RunStatus::Running.as_str().into(),
            phase: "plan".into(),
            blocked: false,
            reason_code: String::new(),
            release_human_gate: true,
            verifier_required: true,
        })
    }

    pub fn status(&self, run_id: i64) -> Result<GoalRunHandle, String> {
        let conn = self.store.connection();
        let row = RunDao::get(conn, run_id)
            .map_err(|e| e.to_string())?
            .ok_or_else(|| format!("run {run_id} not found"))?;
        let snap = SpineDao::latest_for_run(conn, run_id).map_err(|e| e.to_string())?;
        Ok(GoalRunHandle {
            run_id,
            feature_package_id: row.feature_package_id,
            status: row.status,
            phase: snap.map(|s| s.phase).unwrap_or_else(|| "unknown".into()),
            blocked: false,
            reason_code: String::new(),
            release_human_gate: true,
            verifier_required: true,
        })
    }

    pub fn resume(&self, run_id: i64, next_action: &str) -> Result<GoalRunHandle, String> {
        let conn = self.store.connection();
        if let Some(mut snap) = SpineDao::latest_for_run(conn, run_id).map_err(|e| e.to_string())? {
            snap.next_action = next_action.into();
            snap.progress_status = "resumed".into();
            snap.updated_at = now_secs();
            let json = serde_json::to_string(&snap).map_err(|e| e.to_string())?;
            SpineDao::save(conn, run_id, &json).map_err(|e| e.to_string())?;
        }
        RunDao::update_status(conn, run_id, RunStatus::Running).map_err(|e| e.to_string())?;
        let mut handle = self.status(run_id)?;
        handle.status = RunStatus::Running.as_str().into();
        Ok(handle)
    }

    pub fn stop(&self, run_id: i64, force: bool) -> Result<GoalRunHandle, String> {
        let conn = self.store.connection();
        let status = if force {
            RunStatus::Failed
        } else {
            RunStatus::Stopped
        };
        RunDao::update_status(conn, run_id, status).map_err(|e| e.to_string())?;
        let mut handle = self.status(run_id)?;
        handle.status = status.as_str().into();
        Ok(handle)
    }
}

fn now_secs() -> String {
    std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map(|d| d.as_secs().to_string())
        .unwrap_or_else(|_| "0".into())
}
