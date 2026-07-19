//! Beacon v2 / Loom evolution CLI — Operator Spine + harness + goal surface.
//! Binary name: `beacon-v2` (does not replace production `beacon`).

use std::path::PathBuf;

use beacon_core::dual_track::{admit_path_set, Track};
use beacon_core::harness::HarnessSurface;
use beacon_core::branch_context::BranchContext;
use beacon_core::RunStatus;
use beacon_gate::harness_trace_gate::evaluate_harness_trace_gate;
use beacon_gate::{
    doctor_exit_code, evaluate_release_gate, evaluate_truth_integrity, sample_valid_adversarial,
    EvidenceRef, ReleaseGateInput, TigMode, TruthIntegrityInput,
};
use beacon_orchestrator::{
    admit_workspace, build_gitscope, build_skill_load_plan, collect_branch_context, map_agent_name,
    require_topology_gate, resolve_worktree, run_one_implement_iteration, verify_flow_order,
    AllowStopChecker, CodexBackend, CommandStopChecker, DenyStopChecker, GoalController,
    HarnessPathController, Orchestrator, StopWhen, SubprocessBackend, TopologyKind, WorktreeMode,
    WorktreeResolveRequest, WorkspaceAdmissionRequest, FLOW_STAGES,
};
use beacon_store::{BeaconStore, FeatureDao, ProjectDao, RunDao, SpineDao};
use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(
    name = "beacon-v2",
    version,
    about = "Beacon v2 Rust CLI / Loom kernel surface (dual-track; does not replace beacon)"
)]
struct Cli {
    /// Path to the global beacon.db (default: ~/.beacon/beacon.db).
    #[arg(long, env = "BEACON_STORE_PATH", global = true)]
    store_path: Option<PathBuf>,

    /// Explicit runtime track (v1|v2). Default v2 for this binary; never silent v1 fallback.
    #[arg(long, global = true, default_value = "v2")]
    runtime: String,

    #[command(subcommand)]
    command: Command,
}

#[derive(Subcommand)]
enum Command {
    /// AC-017..020 Operator Spine read surface.
    Spine {
        #[command(subcommand)]
        action: SpineAction,
    },
    /// AC-021 machine-level multi-project registry.
    Projects {
        #[command(subcommand)]
        action: ProjectsAction,
    },
    /// Six first-class harness abilities (AC-059/063/109).
    Harness {
        #[command(subcommand)]
        action: HarnessAction,
    },
    /// Goal run controller (P2-001).
    Goal {
        #[command(subcommand)]
        action: GoalAction,
    },
    /// Dual-track path admission check (TC-148).
    DualTrack {
        #[arg(long)]
        path: Vec<String>,
        #[arg(long)]
        admit_mixed: bool,
        #[arg(long)]
        json: bool,
    },
    /// Progressive skill load plan (AC-126).
    SkillLoad {
        #[arg(long)]
        stage: String,
        #[arg(long, default_value = "")]
        topic: String,
        #[arg(long)]
        json: bool,
    },
    /// Workspace admission → BranchContext.v1 (AC-128).
    Workspace {
        #[command(subcommand)]
        action: WorkspaceAction,
    },
    /// Standard execution flow verify (AC-138).
    Flow {
        #[command(subcommand)]
        action: FlowAction,
    },
    /// TraceSpine hard gate check for harness phase (AC-133).
    Trace {
        #[command(subcommand)]
        action: TraceAction,
    },
    /// Git worktree resolve/materialize (AC-099 / W1).
    Worktree {
        #[command(subcommand)]
        action: WorktreeAction,
    },
    /// Implement harness one iteration in admitted worktree (AC-100 / W1).
    Implement {
        #[command(subcommand)]
        action: ImplementAction,
    },
    /// In-process agent run (AC-105/106). No daemon.
    Run {
        #[arg(long)]
        agent: String,
        #[arg(long, default_value = ".")]
        project_root: PathBuf,
        #[arg(long, default_value = "iterate")]
        prompt: String,
        #[arg(long, default_value = "5")]
        max_iterations: u32,
        #[arg(long, default_value = "")]
        stop_check_cmd: String,
        #[arg(long)]
        stop_allow: bool,
        #[arg(long)]
        json: bool,
    },
    /// Doctor routes (AC-103).
    Doctor {
        #[command(subcommand)]
        action: DoctorAction,
    },
    /// Release adversarial gate (AC-166/167).
    Release {
        #[command(subcommand)]
        action: ReleaseAction,
    },
    /// GitScope topology (AC-171–173).
    Topology {
        #[command(subcommand)]
        action: TopologyAction,
    },
}

#[derive(Subcommand)]
enum WorkspaceAction {
    Admit {
        #[arg(long)]
        run_id: String,
        #[arg(long)]
        project_root: PathBuf,
        #[arg(long, default_value = "")]
        cwd: String,
        #[arg(long, default_value = "main")]
        branch: String,
        #[arg(long)]
        worktree: Option<PathBuf>,
        /// Probe real git for branch/root (AC-128/171).
        #[arg(long)]
        git: bool,
        #[arg(long)]
        json: bool,
    },
}

#[derive(Subcommand)]
enum FlowAction {
    Stages {
        #[arg(long)]
        json: bool,
    },
    Verify {
        #[arg(long, value_delimiter = ',')]
        completed: Vec<String>,
        #[arg(long)]
        current: String,
        #[arg(long)]
        json: bool,
    },
}

#[derive(Subcommand)]
enum TraceAction {
    Check {
        #[arg(long)]
        phase: String,
        #[arg(long)]
        missing: bool,
        #[arg(long)]
        json: bool,
    },
}

#[derive(Subcommand)]
enum WorktreeAction {
    /// Resolve (and optionally materialize) worktree/current-branch/run-branch.
    Resolve {
        #[arg(long)]
        project_root: PathBuf,
        #[arg(long, default_value = "worktree")]
        mode: String,
        #[arg(long, default_value = "run")]
        run_id: String,
        #[arg(long, default_value = "feature")]
        feature: String,
        /// Illegal with current-branch (fail-closed).
        #[arg(long)]
        isolated: bool,
        #[arg(long)]
        materialize: bool,
        #[arg(long)]
        json: bool,
    },
}

#[derive(Subcommand)]
enum ImplementAction {
    /// One real ImplementHarness iteration (not subprocess echo).
    Iterate {
        #[arg(long)]
        project_root: PathBuf,
        #[arg(long)]
        worktree: Option<PathBuf>,
        #[arg(long, default_value = "worktree")]
        mode: String,
        #[arg(long, default_value = "run")]
        run_id: String,
        #[arg(long, default_value = "feature")]
        feature: String,
        #[arg(long, default_value = "implement one round")]
        prompt: String,
        #[arg(long)]
        materialize: bool,
        #[arg(long)]
        json: bool,
    },
}

#[derive(Subcommand)]
enum DoctorAction {
    VerifyTruthIntegrity {
        #[arg(long, default_value = "block")]
        mode: String,
        #[arg(long, default_value = "draft")]
        status: String,
        #[arg(long, default_value = "true")]
        has_ac: String,
        #[arg(long, default_value = "1")]
        ac_count: u32,
        #[arg(long, default_value = "false")]
        soft_tc_only: String,
        #[arg(long, default_value = "false")]
        unapproved_deferral: String,
        #[arg(long, default_value = "false")]
        fake_delivery: String,
        #[arg(long, default_value = "true")]
        package_valid: String,
        #[arg(long)]
        json: bool,
    },
}

#[derive(Subcommand)]
enum ReleaseAction {
    Check {
        #[arg(long, default_value = "v2")]
        claim_track: String,
        #[arg(long, default_value = "")]
        evidence: String,
        #[arg(long)]
        with_adversarial: bool,
        #[arg(long)]
        skill_score_as_adversarial: bool,
        #[arg(long)]
        json: bool,
    },
}

#[derive(Subcommand)]
enum TopologyAction {
    Build {
        #[arg(long)]
        project_root: PathBuf,
        #[arg(long, default_value = "single_repo")]
        topology: String,
        #[arg(long)]
        json: bool,
    },
    Gate {
        #[arg(long)]
        project_root: PathBuf,
        #[arg(long, default_value = "single_repo")]
        topology: String,
        #[arg(long, default_value = "")]
        topology_gate_ref: String,
        #[arg(long)]
        missing: bool,
        #[arg(long)]
        json: bool,
    },
}

#[derive(Subcommand)]
enum SpineAction {
    Show {
        run_id: i64,
        #[arg(long)]
        json: bool,
    },
    List {
        #[arg(long)]
        json: bool,
    },
    Artifacts {
        run_id: i64,
        #[arg(long)]
        json: bool,
    },
}

#[derive(Subcommand)]
enum ProjectsAction {
    Register {
        #[arg(long)]
        path: PathBuf,
        #[arg(long, default_value = "")]
        name: String,
        #[arg(long)]
        json: bool,
    },
    List {
        #[arg(long)]
        json: bool,
    },
    Show {
        #[arg(long)]
        project: PathBuf,
        #[arg(long)]
        json: bool,
    },
}

#[derive(Subcommand)]
enum HarnessAction {
    /// List six public abilities for a version.
    List {
        #[arg(long, default_value = "v2.0.0")]
        version: String,
        #[arg(long)]
        json: bool,
    },
}

#[derive(Subcommand)]
enum GoalAction {
    Run {
        utterance: String,
        #[arg(long)]
        project: PathBuf,
        #[arg(long, default_value = "v2.0.0")]
        version: String,
        #[arg(long, default_value = "demo")]
        feature: String,
        #[arg(long)]
        json: bool,
    },
    Status {
        #[arg(long)]
        run_id: i64,
        #[arg(long)]
        json: bool,
    },
    Resume {
        #[arg(long)]
        run_id: i64,
        #[arg(long, default_value = "continue")]
        next_action: String,
        #[arg(long)]
        json: bool,
    },
    Stop {
        #[arg(long)]
        run_id: i64,
        #[arg(long)]
        force: bool,
        #[arg(long)]
        json: bool,
    },
}

fn open_store(path: Option<PathBuf>) -> Result<BeaconStore, Box<dyn std::error::Error>> {
    match path {
        Some(p) => Ok(BeaconStore::open(&p)?),
        None => {
            let home = dirs_or_home()?;
            let default = home.join(".beacon").join("beacon.db");
            if let Some(parent) = default.parent() {
                let _ = std::fs::create_dir_all(parent);
            }
            Ok(BeaconStore::open(&default)?)
        }
    }
}

fn dirs_or_home() -> Result<PathBuf, Box<dyn std::error::Error>> {
    Ok(std::env::var_os("HOME")
        .map(PathBuf::from)
        .ok_or("HOME not set")?)
}

fn ensure_runtime(runtime: &str) -> Result<Track, Box<dyn std::error::Error>> {
    let track = Track::parse(runtime).ok_or_else(|| format!("invalid --runtime {runtime}"))?;
    // This binary is v2 surface; refuse silent v1 fallback as default execution
    if track == Track::V1 {
        return Err("beacon-v2 binary refuses --runtime v1 (use production `beacon` CLI)".into());
    }
    Ok(track)
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let cli = Cli::parse();
    let _track = ensure_runtime(&cli.runtime)?;
    let store = open_store(cli.store_path)?;
    let conn = store.connection();
    match cli.command {
        Command::Spine { action } => match action {
            SpineAction::Show { run_id, json } => match SpineDao::latest_for_run(conn, run_id)? {
                Some(snap) => print_json_or_debug(&snap, json)?,
                None => println!("no spine snapshot for run {}", run_id),
            },
            SpineAction::List { json } => {
                let snaps = SpineDao::list_latest(conn)?;
                print_json_or_debug(&snaps, json)?;
            }
            SpineAction::Artifacts { run_id, json } => {
                let arts = SpineDao::artifacts_for_run(conn, run_id)?;
                print_json_or_debug(&arts, json)?;
            }
        },
        Command::Projects { action } => match action {
            ProjectsAction::Register { path, name, json } => {
                let abs = path.canonicalize().unwrap_or(path);
                let name = if name.is_empty() {
                    abs.file_name()
                        .map(|s| s.to_string_lossy().to_string())
                        .unwrap_or_else(|| "project".to_string())
                } else {
                    name
                };
                let row = ProjectDao::register(conn, &abs.to_string_lossy(), &name)?;
                print_json_or_debug(&row, json)?;
            }
            ProjectsAction::List { json } => {
                let rows = ProjectDao::list(conn)?;
                print_json_or_debug(&rows, json)?;
            }
            ProjectsAction::Show { project, json } => {
                let abs = project.canonicalize().unwrap_or(project);
                match ProjectDao::show(conn, &abs.to_string_lossy(), &abs.to_string_lossy())? {
                    Some(show) => print_json_or_debug(&show, json)?,
                    None => println!("project not registered: {}", abs.display()),
                }
            }
        },
        Command::Harness { action } => match action {
            HarnessAction::List { version, json } => {
                let mut surface = HarnessSurface::v2_default();
                surface.version = version;
                print_json_or_debug(&surface, json)?;
            }
        },
        Command::Goal { action } => {
            let ctrl = GoalController::new(&store);
            match action {
                GoalAction::Run {
                    utterance,
                    project,
                    version,
                    feature,
                    json,
                } => {
                    let abs = project.canonicalize().unwrap_or(project);
                    let name = abs
                        .file_name()
                        .map(|s| s.to_string_lossy().to_string())
                        .unwrap_or_else(|| "project".into());
                    let handle = ctrl.create(
                        &abs.to_string_lossy(),
                        &name,
                        &feature,
                        &version,
                        &utterance,
                    )?;
                    print_json_or_debug(&handle, json)?;
                }
                GoalAction::Status { run_id, json } => {
                    let handle = ctrl.status(run_id)?;
                    print_json_or_debug(&handle, json)?;
                }
                GoalAction::Resume {
                    run_id,
                    next_action,
                    json,
                } => {
                    let handle = ctrl.resume(run_id, &next_action)?;
                    print_json_or_debug(&handle, json)?;
                }
                GoalAction::Stop { run_id, force, json } => {
                    let handle = ctrl.stop(run_id, force)?;
                    print_json_or_debug(&handle, json)?;
                }
            }
        }
        Command::DualTrack {
            path,
            admit_mixed,
            json,
        } => {
            let refs: Vec<&str> = path.iter().map(|s| s.as_str()).collect();
            let result = admit_path_set(&refs, admit_mixed);
            print_json_or_debug(&result, json)?;
            if result.blocked {
                std::process::exit(2);
            }
        }
        Command::SkillLoad { stage, topic, json } => {
            let plan = build_skill_load_plan(&stage, &topic);
            print_json_or_debug(&plan, json)?;
        }
        Command::Workspace { action } => match action {
            WorkspaceAction::Admit {
                run_id,
                project_root,
                cwd,
                branch,
                worktree,
                git,
                json,
            } => {
                let abs = project_root.canonicalize().unwrap_or(project_root);
                let cwd_path = if cwd.is_empty() {
                    std::env::current_dir().unwrap_or_else(|_| abs.clone())
                } else {
                    PathBuf::from(cwd)
                };
                let result = if git {
                    collect_branch_context(
                        &run_id,
                        &cwd_path,
                        &abs,
                        worktree.as_deref(),
                    )
                } else {
                    let req = WorkspaceAdmissionRequest {
                        run_id,
                        caller_cwd: cwd_path.to_string_lossy().to_string(),
                        target_project_root: abs.to_string_lossy().to_string(),
                        worktree: worktree.map(|p| p.to_string_lossy().to_string()),
                        branch,
                        allow_cwd_as_root: true,
                    };
                    admit_workspace(&req)
                };
                print_json_or_debug(&result, json)?;
                if result.blocked {
                    std::process::exit(2);
                }
            }
        },
        Command::Flow { action } => match action {
            FlowAction::Stages { json } => {
                let stages: Vec<&str> = FLOW_STAGES.to_vec();
                print_json_or_debug(&stages, json)?;
            }
            FlowAction::Verify {
                completed,
                current,
                json,
            } => {
                let result = match verify_flow_order(&completed, &current) {
                    Ok(()) => serde_json::json!({"ok": true, "blocked": false, "completed": completed, "current": current}),
                    Err(code) => serde_json::json!({"ok": false, "blocked": true, "reason_code": code, "completed": completed, "current": current}),
                };
                print_json_or_debug(&result, json)?;
                if result.get("blocked").and_then(|v| v.as_bool()).unwrap_or(false) {
                    std::process::exit(2);
                }
            }
        },
        Command::Trace { action } => match action {
            TraceAction::Check { phase, missing, json } => {
                let gate = if missing {
                    evaluate_harness_trace_gate(&phase, None, None, true)
                } else {
                    let mut ctrl = HarnessPathController::new();
                    let bc = BranchContext::new("cli-check", "/tmp", "/tmp", "/tmp", "main").mark_admitted();
                    ctrl.admission.truth_map_verify = true;
                    ctrl.admission.verify_materials_strict = true;
                    ctrl.admission.diff_check = true;
                    ctrl.admission.branch_governance_verify = true;
                    ctrl.admission.workspace_admission = true;
                    ctrl.admission.truth_baseline_commit = "deadbeef".into();
                    ctrl.admission.baseline_merged_into_feature = true;
                    let _ = ctrl.start_loop("cli-check", bc, "dp", "is", "th", "des");
                    let _ = ctrl.append_iteration("iter", "ev/1");
                    evaluate_harness_trace_gate(
                        &phase,
                        ctrl.spine.as_ref(),
                        ctrl.branch.as_ref(),
                        false,
                    )
                };
                print_json_or_debug(&gate, json)?;
                if gate.blocked {
                    std::process::exit(2);
                }
            }
        },
        Command::Worktree { action } => match action {
            WorktreeAction::Resolve {
                project_root,
                mode,
                run_id,
                feature,
                isolated,
                materialize,
                json,
            } => {
                let mode = WorktreeMode::parse(&mode).ok_or_else(|| format!("unknown mode: {mode}"))?;
                let abs = project_root.canonicalize().unwrap_or(project_root);
                let result = resolve_worktree(&WorktreeResolveRequest {
                    project_root: abs,
                    mode,
                    run_id,
                    feature_slug: feature,
                    isolated,
                    materialize,
                    base_ref: None,
                });
                print_json_or_debug(&result, json)?;
                if result.blocked {
                    std::process::exit(2);
                }
            }
        },
        Command::Implement { action } => match action {
            ImplementAction::Iterate {
                project_root,
                worktree,
                mode,
                run_id,
                feature,
                prompt,
                materialize,
                json,
            } => {
                let mode = WorktreeMode::parse(&mode).ok_or_else(|| format!("unknown mode: {mode}"))?;
                let abs = project_root.canonicalize().unwrap_or(project_root);
                let wt = if let Some(w) = worktree {
                    let path = w.canonicalize().unwrap_or(w);
                    beacon_orchestrator::WorktreeResolveResult {
                        blocked: false,
                        status: "pass".into(),
                        reason_code: String::new(),
                        mode: mode.as_str().into(),
                        admitted_worktree: path.to_string_lossy().to_string(),
                        branch: "HEAD".into(),
                        project_root: abs.to_string_lossy().to_string(),
                        git_worktree_added: false,
                        git_dir_is_file: path.join(".git").is_file(),
                        materialize_requested: false,
                    }
                } else {
                    resolve_worktree(&WorktreeResolveRequest {
                        project_root: abs.clone(),
                        mode,
                        run_id: run_id.clone(),
                        feature_slug: feature.clone(),
                        isolated: false,
                        materialize,
                        base_ref: None,
                    })
                };
                if wt.blocked {
                    print_json_or_debug(&wt, json)?;
                    std::process::exit(2);
                }
                let admit = admit_workspace(&WorkspaceAdmissionRequest {
                    run_id: run_id.clone(),
                    caller_cwd: wt.admitted_worktree.clone(),
                    target_project_root: abs.to_string_lossy().to_string(),
                    worktree: Some(wt.admitted_worktree.clone()),
                    branch: wt.branch.clone(),
                    allow_cwd_as_root: true,
                });
                if admit.blocked {
                    print_json_or_debug(&admit, json)?;
                    std::process::exit(2);
                }
                let bc = admit.branch_context.ok_or("branch_context_missing")?;
                let (result, refs) = run_one_implement_iteration(bc, &prompt)?;
                let payload = serde_json::json!({
                    "iteration_result": result,
                    "artifact_refs": refs,
                    "admitted_worktree": wt.admitted_worktree,
                    "branch": wt.branch,
                    "backend": "implement-harness",
                });
                print_json_or_debug(&payload, json)?;
            }
        },
        Command::Run {
            agent,
            project_root,
            prompt,
            max_iterations,
            stop_check_cmd,
            stop_allow,
            json,
        } => {
            let _mapped = map_agent_name(&agent)?;
            let abs = project_root.canonicalize().unwrap_or(project_root);
            let pid = ProjectDao::insert(conn, &abs.to_string_lossy(), "run-proj")?;
            let fid = FeatureDao::insert(conn, pid, "run-feature", "v2.0.0", "draft", None)?;
            let run_id = RunDao::insert(conn, fid, &agent, RunStatus::Running)?;
            let mut orch =
                Orchestrator::new(&store, run_id, StopWhen::MaxIterations(max_iterations));
            let steps = if agent == "subprocess" {
                let script = abs.join(".loom").join("run-echo.sh");
                if let Some(parent) = script.parent() {
                    let _ = std::fs::create_dir_all(parent);
                }
                let body = r#"#!/bin/sh
echo '{"success":true,"summary":"subprocess-iter","key_changes_made":[],"key_learnings":[],"stop_signal":"gate_pass","token_usage":{"input_tokens":1,"output_tokens":1},"agent_name":"subprocess"}'
"#;
                std::fs::write(&script, body)?;
                #[cfg(unix)]
                {
                    use std::os::unix::fs::PermissionsExt;
                    let mut perms = std::fs::metadata(&script)?.permissions();
                    perms.set_mode(0o755);
                    std::fs::set_permissions(&script, perms)?;
                }
                let mut backend = SubprocessBackend::new(
                    "subprocess",
                    vec![script.to_string_lossy().to_string()],
                    max_iterations,
                );
                if stop_allow {
                    let mut chk = AllowStopChecker {
                        label: "cli".into(),
                    };
                    orch.run_with_external_stop(&mut backend, &prompt, &mut chk)?
                } else if !stop_check_cmd.is_empty() {
                    let parts: Vec<String> = stop_check_cmd
                        .split_whitespace()
                        .map(|s| s.to_string())
                        .collect();
                    let mut chk = CommandStopChecker {
                        command: parts,
                        cwd: Some(abs.clone()),
                    };
                    orch.run_with_external_stop(&mut backend, &prompt, &mut chk)?
                } else {
                    let mut chk = DenyStopChecker;
                    orch.run_with_external_stop(&mut backend, &prompt, &mut chk)?
                }
            } else {
                let art = abs.join(".loom").join("run-artifacts");
                let mut backend = CodexBackend::new(&art, max_iterations);
                if stop_allow {
                    let mut chk = AllowStopChecker {
                        label: "cli".into(),
                    };
                    orch.run_with_external_stop(&mut backend, &prompt, &mut chk)?
                } else if !stop_check_cmd.is_empty() {
                    let parts: Vec<String> = stop_check_cmd
                        .split_whitespace()
                        .map(|s| s.to_string())
                        .collect();
                    let mut chk = CommandStopChecker {
                        command: parts,
                        cwd: Some(abs.clone()),
                    };
                    orch.run_with_external_stop(&mut backend, &prompt, &mut chk)?
                } else {
                    let mut chk = DenyStopChecker;
                    orch.run_with_external_stop(&mut backend, &prompt, &mut chk)?
                }
            };
            let payload = serde_json::json!({
                "run_id": run_id,
                "agent": agent,
                "daemon": false,
                "steps": steps.iter().map(|s| serde_json::json!({
                    "iteration": s.iteration,
                    "stopped": s.stopped,
                    "stop_reason": s.stop_reason,
                    "stop_unverified": s.stop_unverified,
                    "success": s.result.success,
                    "agent_name": s.result.agent_name,
                })).collect::<Vec<_>>(),
            });
            print_json_or_debug(&payload, json)?;
        },
        Command::Doctor { action } => match action {
            DoctorAction::VerifyTruthIntegrity {
                mode,
                status,
                has_ac,
                ac_count,
                soft_tc_only,
                unapproved_deferral,
                fake_delivery,
                package_valid,
                json,
            } => {
                let parse_bool =
                    |s: &str| matches!(s.to_ascii_lowercase().as_str(), "1" | "true" | "yes");
                let input = TruthIntegrityInput {
                    status,
                    has_acceptance_criteria: parse_bool(&has_ac),
                    soft_tc_only: parse_bool(&soft_tc_only),
                    unapproved_deferral: parse_bool(&unapproved_deferral),
                    fake_delivery_claim: parse_bool(&fake_delivery),
                    package_valid: parse_bool(&package_valid),
                    ac_count,
                };
                let result = evaluate_truth_integrity(&input, TigMode::parse(&mode));
                print_json_or_debug(&result, json)?;
                std::process::exit(doctor_exit_code(&result));
            }
        },
        Command::Release { action } => match action {
            ReleaseAction::Check {
                claim_track,
                evidence,
                with_adversarial,
                skill_score_as_adversarial,
                json,
            } => {
                let mut evs = Vec::new();
                if !evidence.is_empty() {
                    for part in evidence.split(',') {
                        let bits: Vec<&str> = part.splitn(3, ':').collect();
                        if bits.len() == 3 {
                            evs.push(EvidenceRef {
                                path: bits[2].into(),
                                track: bits[0].into(),
                                kind: bits[1].into(),
                            });
                        }
                    }
                }
                let input = ReleaseGateInput {
                    claim_track,
                    evidence: evs,
                    adversarial: if with_adversarial {
                        Some(sample_valid_adversarial())
                    } else {
                        None
                    },
                    skill_score_as_adversarial,
                };
                let result = evaluate_release_gate(&input);
                print_json_or_debug(&result, json)?;
                if result.blocked {
                    std::process::exit(2);
                }
            }
        },
        Command::Topology { action } => match action {
            TopologyAction::Build {
                project_root,
                topology,
                json,
            } => {
                let abs = project_root.canonicalize().unwrap_or(project_root);
                let t = TopologyKind::parse(&topology)
                    .ok_or_else(|| format!("unknown topology: {topology}"))?;
                let g = build_gitscope(&abs, t);
                print_json_or_debug(&g, json)?;
            }
            TopologyAction::Gate {
                project_root,
                topology,
                topology_gate_ref,
                missing,
                json,
            } => {
                if missing {
                    let r = require_topology_gate(None, None);
                    print_json_or_debug(&r, json)?;
                    std::process::exit(2);
                }
                let abs = project_root.canonicalize().unwrap_or(project_root);
                let t = TopologyKind::parse(&topology)
                    .ok_or_else(|| format!("unknown topology: {topology}"))?;
                let g = build_gitscope(&abs, t);
                let pref = if topology_gate_ref.is_empty() {
                    None
                } else {
                    Some(topology_gate_ref.as_str())
                };
                let r = require_topology_gate(Some(&g), pref);
                print_json_or_debug(&r, json)?;
                if r.blocked {
                    std::process::exit(2);
                }
            }
        },
    }
    Ok(())
}

fn print_json_or_debug<T: serde::Serialize + std::fmt::Debug>(
    value: &T,
    json: bool,
) -> Result<(), Box<dyn std::error::Error>> {
    if json {
        println!("{}", serde_json::to_string_pretty(value)?);
    } else {
        println!("{value:?}");
    }
    Ok(())
}
