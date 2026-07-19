//! P1 CLI tests — TC-064 (help snapshot) + TC-065 (--json schema).

use assert_cmd::Command;

// ---- TC-064 / AC-064: CLI help snapshot — all subcommands present ----

#[test]
fn tc064_cli_help_lists_all_subcommands() {
    let output = Command::cargo_bin("loom").unwrap().arg("--help").unwrap();
    let stdout = String::from_utf8(output.stdout).unwrap();
    assert!(stdout.contains("spine"), "help must list spine");
    assert!(stdout.contains("projects"), "help must list projects");
    // spine subcommands
    let spine_help = Command::cargo_bin("loom").unwrap().args(["spine", "--help"]).unwrap();
    let s = String::from_utf8(spine_help.stdout).unwrap();
    assert!(s.contains("show") && s.contains("list") && s.contains("artifacts"));
    // projects subcommands
    let proj_help = Command::cargo_bin("loom").unwrap().args(["projects", "--help"]).unwrap();
    let p = String::from_utf8(proj_help.stdout).unwrap();
    assert!(p.contains("register") && p.contains("list") && p.contains("show"));
}

// ---- TC-065 / AC-065: --json schema for spine/projects ----

#[test]
fn tc065_projects_register_json_has_project_key() {
    let dir = tempfile::tempdir().unwrap();
    let db = dir.path().join("beacon.db");
    let proj = dir.path().join("myproj");
    std::fs::create_dir_all(&proj).unwrap();
    let abs = proj.canonicalize().unwrap();
    let output = Command::cargo_bin("loom")
        .unwrap()
        .args([
            "--store-path", db.to_str().unwrap(),
            "projects", "register", "--path", abs.to_str().unwrap(), "--json",
        ])
        .unwrap();
    let stdout = String::from_utf8(output.stdout).unwrap();
    let v: serde_json::Value = serde_json::from_str(&stdout).expect("valid json");
    assert!(v.get("project_key").is_some(), "register json must have project_key");
    assert!(v.get("root_path").is_some());
    assert!(v.get("id").is_some());
}

#[test]
fn tc065_spine_list_json_is_array() {
    let dir = tempfile::tempdir().unwrap();
    let db = dir.path().join("beacon.db");
    let output = Command::cargo_bin("loom")
        .unwrap()
        .args(["--store-path", db.to_str().unwrap(), "spine", "list", "--json"])
        .unwrap();
    let stdout = String::from_utf8(output.stdout).unwrap();
    let v: serde_json::Value = serde_json::from_str(&stdout).expect("valid json");
    assert!(v.is_array(), "spine list --json must be an array");
    assert!(v.as_array().unwrap().is_empty(), "empty db -> empty array");
}

#[test]
fn tc065_projects_show_json_has_versions_and_is_current() {
    let dir = tempfile::tempdir().unwrap();
    let db = dir.path().join("beacon.db");
    let proj = dir.path().join("myproj");
    std::fs::create_dir_all(&proj).unwrap();
    let abs = proj.canonicalize().unwrap();
    // register first
    let _ = Command::cargo_bin("loom")
        .unwrap()
        .args([
            "--store-path", db.to_str().unwrap(),
            "projects", "register", "--path", abs.to_str().unwrap(), "--json",
        ])
        .unwrap();
    // show
    let output = Command::cargo_bin("loom")
        .unwrap()
        .args([
            "--store-path", db.to_str().unwrap(),
            "projects", "show", "--project", abs.to_str().unwrap(), "--json",
        ])
        .unwrap();
    let stdout = String::from_utf8(output.stdout).unwrap();
    let v: serde_json::Value = serde_json::from_str(&stdout).expect("valid json");
    assert!(v.get("project_key").is_some());
    assert!(v.get("versions").is_some(), "show json must have versions[]");
    assert!(v.get("is_current").is_some(), "show json must have is_current");
}
