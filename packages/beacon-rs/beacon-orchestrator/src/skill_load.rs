//! Progressive disclosure skill loader — skill_load_plan.v1 (AC-126 / TC-126).
//! v2 / Loom track prefers loom-* skill names (full brand surface).

use serde::{Deserialize, Serialize};

pub const SCHEMA: &str = "skill_load_plan.v1";

/// Stage → public skills for **Loom / v2** track.
pub fn skills_for_stage(stage: &str) -> Vec<&'static str> {
    skills_for_stage_brand(stage, "loom")
}

/// brand: "loom" | "beacon"
pub fn skills_for_stage_brand(stage: &str, brand: &str) -> Vec<&'static str> {
    let loom = brand != "beacon";
    let map = |b: &'static str, l: &'static str| if loom { l } else { b };
    match stage {
        "plan" => vec![
            map("beacon-pln-program", "loom-pln-program"),
            map("beacon-pln-program-auto", "loom-pln-program-auto"),
        ],
        "truth" => vec![
            map("beacon-gen-truth", "loom-gen-truth"),
            map("beacon-gen-change", "loom-gen-change"),
        ],
        "design" => vec![
            map("beacon-gen-design", "loom-gen-design"),
            map("beacon-gen-design-system", "loom-gen-design-system"),
        ],
        "implement" => vec![map("beacon-gen-implement", "loom-gen-implement")],
        "qa" | "qa-evidence" => vec![map("beacon-eval-qa", "loom-eval-qa")],
        "release" => vec![map("beacon-eval-release", "loom-eval-release")],
        "loop" => vec![map("beacon-loop-goal", "loom-loop-goal")],
        _ => vec![],
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SkillLoadItem {
    pub skill: String,
    pub load_skill_md: bool,
    pub references: Vec<String>,
    pub examples: Vec<String>,
    pub content_source: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SkillLoadPlan {
    pub schema: String,
    pub stage: String,
    pub topic: String,
    pub brand: String,
    pub items: Vec<SkillLoadItem>,
    pub bulk_history_forbidden: bool,
    pub loaded_count: usize,
}

pub fn build_skill_load_plan(stage: &str, topic: &str) -> SkillLoadPlan {
    build_skill_load_plan_brand(stage, topic, "loom")
}

pub fn build_skill_load_plan_brand(stage: &str, topic: &str, brand: &str) -> SkillLoadPlan {
    let skills = skills_for_stage_brand(stage, brand);
    let items: Vec<SkillLoadItem> = skills
        .iter()
        .map(|s| {
            let content_source = if s.starts_with("loom-") {
                format!("skills/beacon/beacon-{}", &s[5..])
            } else {
                format!("skills/beacon/{s}")
            };
            SkillLoadItem {
                skill: (*s).to_string(),
                load_skill_md: true,
                references: if topic.is_empty() {
                    vec![]
                } else {
                    vec![format!("references/{topic}.md")]
                },
                examples: vec![],
                content_source,
            }
        })
        .collect();
    let loaded_count = items.len();
    SkillLoadPlan {
        schema: SCHEMA.into(),
        stage: stage.into(),
        topic: topic.into(),
        brand: brand.into(),
        items,
        bulk_history_forbidden: true,
        loaded_count,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn progressive_loom_brand() {
        let plan = build_skill_load_plan("implement", "ralph");
        assert_eq!(plan.brand, "loom");
        assert_eq!(plan.loaded_count, 1);
        assert!(plan.items[0].skill.starts_with("loom-"));
        assert!(plan.items[0].content_source.contains("beacon-gen-implement"));
        assert!(plan.bulk_history_forbidden);
    }

    #[test]
    fn beacon_brand_still_available() {
        let plan = build_skill_load_plan_brand("qa", "", "beacon");
        assert!(plan.items[0].skill.contains("beacon-eval-qa"));
    }
}
