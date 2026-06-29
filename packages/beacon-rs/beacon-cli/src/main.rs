//! Beacon v2 CLI entry — P1 Operator Spine API (AC-017..021).
//!
//! Commands: `spine show|list|artifacts`, `projects register|list|show`.

use std::path::PathBuf;

use beacon_store::{BeaconStore, ProjectDao, SpineDao};
use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(name = "beacon-v2", version, about = "Beacon v2 Rust CLI (P1 spine/projects)")]
struct Cli {
    /// Path to the global beacon.db (default: ~/.beacon/beacon.db).
    #[arg(long, env = "BEACON_STORE_PATH", global = true)]
    store_path: Option<PathBuf>,

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
}

#[derive(Subcommand)]
enum SpineAction {
    /// AC-017 show the latest spine snapshot for a run.
    Show {
        run_id: i64,
        #[arg(long)]
        json: bool,
    },
    /// AC-018 list latest spine snapshots across all runs.
    List {
        #[arg(long)]
        json: bool,
    },
    /// AC-019 list artifact_refs for a run's latest snapshot.
    Artifacts {
        run_id: i64,
        #[arg(long)]
        json: bool,
    },
}

#[derive(Subcommand)]
enum ProjectsAction {
    /// AC-021 register a project by path.
    Register {
        #[arg(long)]
        path: PathBuf,
        #[arg(long, default_value = "")]
        name: String,
        #[arg(long)]
        json: bool,
    },
    /// AC-021 list registered projects.
    List {
        #[arg(long)]
        json: bool,
    },
    /// AC-021 show a project with versions[] and is_current.
    Show {
        #[arg(long)]
        project: PathBuf,
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
            Ok(BeaconStore::open(&default)?)
        }
    }
}

fn dirs_or_home() -> Result<PathBuf, Box<dyn std::error::Error>> {
    Ok(std::env::var_os("HOME")
        .map(PathBuf::from)
        .ok_or("HOME not set")?)
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let cli = Cli::parse();
    let store = open_store(cli.store_path)?;
    let conn = store.connection();
    match cli.command {
        Command::Spine { action } => match action {
            SpineAction::Show { run_id, json } => match SpineDao::latest_for_run(conn, run_id)? {
                Some(snap) => print_snapshot(&snap, json),
                None => {
                    println!("no spine snapshot for run {}", run_id);
                }
            },
            SpineAction::List { json } => {
                let snaps = SpineDao::list_latest(conn)?;
                if json {
                    println!("{}", serde_json::to_string_pretty(&snaps)?);
                } else {
                    for s in &snaps {
                        print_snapshot(s, false);
                    }
                }
            }
            SpineAction::Artifacts { run_id, json } => {
                let arts = SpineDao::artifacts_for_run(conn, run_id)?;
                if json {
                    println!("{}", serde_json::to_string_pretty(&arts)?);
                } else {
                    for a in &arts {
                        println!("{} {} stale={}", a.path, a.content_hash, a.stale);
                    }
                }
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
                if json {
                    println!("{}", serde_json::to_string_pretty(&row)?);
                } else {
                    println!("registered: {} -> {}", row.project_key, row.root_path);
                }
            }
            ProjectsAction::List { json } => {
                let rows = ProjectDao::list(conn)?;
                if json {
                    println!("{}", serde_json::to_string_pretty(&rows)?);
                } else {
                    for r in &rows {
                        println!("{} {} {}", r.project_key, r.root_path, r.name);
                    }
                }
            }
            ProjectsAction::Show { project, json } => {
                let abs = project.canonicalize().unwrap_or(project);
                let current_root = std::env::current_dir()
                    .map(|p| p.to_string_lossy().to_string())
                    .unwrap_or_default();
                match ProjectDao::show(conn, &abs.to_string_lossy(), &current_root)? {
                    Some(show) => {
                        if json {
                            println!("{}", serde_json::to_string_pretty(&show)?);
                        } else {
                            println!("project_key: {}", show.project_key);
                            println!("root_path: {}", show.root_path);
                            println!("name: {}", show.name);
                            println!("versions: {:?}", show.versions);
                            println!("is_current: {}", show.is_current);
                        }
                    }
                    None => {
                        println!("project not registered: {}", abs.display());
                    }
                }
            }
        },
    }
    Ok(())
}

fn print_snapshot(snap: &beacon_store::SpineSnapshot, json: bool) {
    if json {
        println!("{}", serde_json::to_string_pretty(snap).unwrap_or_default());
    } else {
        println!(
            "run={} stage={} status={} phase={} next={}",
            snap.run_id, snap.lifecycle_stage, snap.lifecycle_status, snap.phase, snap.next_action
        );
    }
}
