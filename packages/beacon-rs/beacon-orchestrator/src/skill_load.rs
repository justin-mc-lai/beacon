//! Progressive disclosure skill loader — skill_load_plan.v1 (AC-126 / TC-126).
//! Loads public SKILL + selected references only; never bulk-loads historical skills.

use serde::{Deserialize, Serialize};

pub const SCHEMA: &str = "skill_load_plan.v1";

/// Stage → public skills (mirrors Python progressive_skills_for_stage intent).
pub fn skills_for_stage(stage: &str) -> Vec<&'static str> {
    match stage {
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
}

/// Build a progressive load plan for a stage/topic. Does not read the whole skill tree.
pub fn build_skill_load_plan(stage: &str, topic: &str) -> SkillLoadPlan {
    let skills = skills_for_stage(stage);
    let items: Vec<SkillLoadItem> = skills
        .iter()
        .map(|s| SkillLoadItem {
            skill: (*s).to_string(),
            load_skill_md: true,
            references: if topic.is_empty() {
                vec![]
            } else {
                vec![format!("references/{topic}.md")]
            },
            examples: vec![],
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
        // must not dump entire historical skill set
        assert!(plan.loaded_count < 30);
    }
}
