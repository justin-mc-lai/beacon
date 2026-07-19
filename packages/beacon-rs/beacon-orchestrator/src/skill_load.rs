//! Progressive disclosure skill loader — skill_load_plan.v1 (AC-126 / TC-126).
//! Loads public SKILL + selected references only; never bulk-loads historical skills.
//! Always mounts git-worktree-execution-flow for goal/implement/qa/release (AC-WT-SKILL).

use serde::{Deserialize, Serialize};

pub const SCHEMA: &str = "skill_load_plan.v1";
pub const WORKTREE_FLOW_REF: &str = "skills/beacon/references/git-worktree-execution-flow.md";
pub const WORKTREE_EXAMPLE_REF: &str =
    "skills/beacon/examples/git-worktree-process-correct-30s.md";

/// Stage → public skills (mirrors Python progressive_skills_for_stage intent).
pub fn skills_for_stage(stage: &str) -> Vec<&'static str> {
    match stage {
        "goal" => vec!["beacon-goal"],
        "plan" => vec!["beacon-pln-program", "beacon-pln-program-auto"],
        "truth" => vec!["beacon-gen-truth", "beacon-gen-change"],
        "design" => vec!["beacon-gen-design", "beacon-gen-design-system"],
        "implement" => vec!["beacon-gen-implement"],
        "qa" | "qa-evidence" => vec!["beacon-eval-qa"],
        "release" => vec!["beacon-eval-release"],
        "loop" => vec!["beacon-loop-goal"],
        _ => vec![],
    }
}

fn worktree_refs_for_stage(stage: &str) -> (Vec<String>, Vec<String>) {
    let st = stage.trim().to_ascii_lowercase();
    let always = matches!(
        st.as_str(),
        "goal"
            | "plan"
            | "truth"
            | "implement"
            | "qa"
            | "qa-evidence"
            | "release"
            | "loop"
            | "discover"
    );
    if !always {
        return (vec![], vec![]);
    }
    let refs = vec![WORKTREE_FLOW_REF.into()];
    let examples = if matches!(st.as_str(), "goal" | "implement" | "loop" | "discover") {
        vec![WORKTREE_EXAMPLE_REF.into()]
    } else {
        vec![]
    };
    (refs, examples)
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SkillLoadItem {
    pub skill: String,
    pub load_skill_md: bool,
    pub references: Vec<String>,
    pub examples: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SkillLoadPlan {
    pub schema: String,
    pub stage: String,
    pub topic: String,
    pub items: Vec<SkillLoadItem>,
    pub bulk_history_forbidden: bool,
    pub loaded_count: usize,
    /// Shared worktree process refs (AC-WT-SKILL).
    pub worktree_flow_refs: Vec<String>,
    pub worktree_flow_examples: Vec<String>,
}

/// Build a progressive load plan for a stage/topic. Does not read the whole skill tree.
pub fn build_skill_load_plan(stage: &str, topic: &str) -> SkillLoadPlan {
    let skills = skills_for_stage(stage);
    let (wt_refs, wt_examples) = worktree_refs_for_stage(stage);
    let items: Vec<SkillLoadItem> = skills
        .iter()
        .map(|s| {
            let mut references = wt_refs.clone();
            if !topic.is_empty() {
                references.push(format!("references/{topic}.md"));
            }
            SkillLoadItem {
                skill: (*s).to_string(),
                load_skill_md: true,
                references,
                examples: wt_examples.clone(),
            }
        })
        .collect();
    let loaded_count = items.len();
    SkillLoadPlan {
        schema: SCHEMA.into(),
        stage: stage.into(),
        topic: topic.into(),
        items,
        bulk_history_forbidden: true,
        loaded_count,
        worktree_flow_refs: wt_refs,
        worktree_flow_examples: wt_examples,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn progressive_not_all_skills() {
        let plan = build_skill_load_plan("implement", "ralph");
        assert_eq!(plan.loaded_count, 1);
        assert!(plan.bulk_history_forbidden);
        assert!(plan.items[0].skill.contains("implement"));
        assert!(plan.loaded_count < 30);
    }

    #[test]
    fn implement_mounts_worktree_flow() {
        let plan = build_skill_load_plan("implement", "");
        assert!(
            plan.worktree_flow_refs.iter().any(|r| r.contains("git-worktree-execution-flow")),
            "{:?}",
            plan.worktree_flow_refs
        );
        assert!(plan.items[0]
            .references
            .iter()
            .any(|r| r.contains("git-worktree-execution-flow")));
        assert!(plan
            .worktree_flow_examples
            .iter()
            .any(|e| e.contains("process-correct")));
    }

    #[test]
    fn goal_mounts_worktree_flow() {
        let plan = build_skill_load_plan("goal", "");
        assert_eq!(plan.items[0].skill, "beacon-goal");
        assert!(!plan.worktree_flow_refs.is_empty());
    }
}
