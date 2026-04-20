# Installing Beacon for Multiple AI Assistants (Codex & Claude Code)

Enable Beacon's evidence-first product workflow across both Codex and Claude Code through native skill discovery.

## Prerequisites

- Git
- Python 3.8+
- Beacon CLI installed (`pip install -e .` from beacon repo)

## Multi-AI Installation

Beacon supports both Codex and Claude Code, but they have different skill discovery mechanisms:

- **Codex**: Supports nested skill directories (discovers sub-skills automatically)
- **Claude Code**: Only scans first-level directories (requires flat structure)

### Quick Install (Recommended)

Use the automated installation script:

```bash
cd ~/Developer/Personal/products/beacon
./scripts/install_claude_skills.sh
```

This script will:
1. Install the main `beacon` skill for both Codex and Claude Code
2. Create flat symlinks for all beacon sub-skills in `~/.claude/skills/`
3. Preserve the nested structure for Codex in `~/.agents/skills/`

### Manual Installation

#### 1. Clone or locate the beacon repository

```bash
# If not already cloned
git clone <beacon-repo-url> ~/Developer/Personal/products/beacon
cd ~/Developer/Personal/products/beacon
```

#### 2. Install for Codex (nested structure)

```bash
mkdir -p ~/.agents/skills
ln -sf ~/Developer/Personal/products/beacon/skills/beacon ~/.agents/skills/beacon
```

**Windows (PowerShell):**
```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills"
cmd /c mklink /J "$env:USERPROFILE\.agents\skills\beacon" "$env:USERPROFILE\Developer\Personal\products\beacon\skills\beacon"
```

#### 3. Install for Claude Code (flat structure)

Claude Code requires each sub-skill to be a separate first-level symlink:

```bash
cd ~/Developer/Personal/products/beacon
./scripts/install_claude_skills.sh
```

Or manually:
```bash
BEACON_SKILLS=~/Developer/Personal/products/beacon/skills/beacon
mkdir -p ~/.claude/skills

# Main beacon skill
ln -sf $BEACON_SKILLS ~/.claude/skills/beacon

# All sub-skills (flat structure required for Claude Code)
ln -sf $BEACON_SKILLS/beacon-doctor ~/.claude/skills/beacon-doctor
ln -sf $BEACON_SKILLS/beacon-help ~/.claude/skills/beacon-help
ln -sf $BEACON_SKILLS/beacon-implement ~/.claude/skills/beacon-implement
ln -sf $BEACON_SKILLS/beacon-prd ~/.claude/skills/beacon-prd
ln -sf $BEACON_SKILLS/beacon-user-story ~/.claude/skills/beacon-user-story
ln -sf $BEACON_SKILLS/beacon-test-case ~/.claude/skills/beacon-test-case
ln -sf $BEACON_SKILLS/beacon-qa ~/.claude/skills/beacon-qa
ln -sf $BEACON_SKILLS/beacon-release ~/.claude/skills/beacon-release
ln -sf $BEACON_SKILLS/beacon-status ~/.claude/skills/beacon-status
ln -sf $BEACON_SKILLS/beacon-prd-bootstrap ~/.claude/skills/beacon-prd-bootstrap
ln -sf $BEACON_SKILLS/beacon-toolkit-lighthouse ~/.claude/skills/beacon-toolkit-lighthouse
ln -sf $BEACON_SKILLS/beacon-real-project-validation ~/.claude/skills/beacon-real-project-validation
ln -sf $BEACON_SKILLS/beacon-memory-friction-evolution ~/.claude/skills/beacon-memory-friction-evolution
ln -sf $BEACON_SKILLS/using-beacon ~/.claude/skills/using-beacon
```

#### 4. Restart your AI assistant

- **Codex**: Quit and relaunch the CLI
- **Claude Code**: Restart the application (completely quit and relaunch)

## Verify Installation

Check that symlinks are correctly created:

```bash
# Verify Codex installation (nested structure)
ls -la ~/.agents/skills/beacon
find ~/.agents/skills/beacon -maxdepth 2 -name SKILL.md | sort

# Verify Claude Code installation (flat structure)
find ~/.claude/skills -maxdepth 1 -name 'beacon*' -type l
ls -la ~/.claude/skills/beacon-prd
ls -la ~/.claude/skills/beacon-implement
```

You should see 15 beacon skills in Claude Code (flat symlinks):
- `beacon` (umbrella skill)
- `using-beacon`
- `beacon-prd`
- `beacon-user-story`
- `beacon-test-case`
- `beacon-implement`
- `beacon-qa`
- `beacon-release`
- `beacon-help`
- `beacon-status`
- `beacon-doctor`
- `beacon-prd-bootstrap`
- `beacon-toolkit-lighthouse`
- `beacon-real-project-validation`

## Verify Beacon CLI

```bash
beacon --version
beacon --help
```

## Available Skills in AI Assistants

After installation, you can invoke beacon skills using:

**In Codex/Claude Code:**
```
/beacon
/beacon-prd
/beacon-implement
/beacon-qa
```

Or use the CLI directly:
```bash
beacon prd create "Feature Name" --version v1.3.3
beacon implement plan "Feature Name" --version v1.3.3
beacon qa run "Feature Name" --version v1.3.3
```

## Updating Beacon

```bash
cd ~/Developer/Personal/products/beacon
git pull
pip install -e . --upgrade
```

Skills update instantly through the symlinks - no need to restart AI assistants unless skill metadata changes.

## Troubleshooting

### Skills not showing up

1. **Check symlinks exist:**
   ```bash
   ls -la ~/.agents/skills/beacon
   ls -la ~/.claude/skills/beacon
   ```

2. **Verify SKILL.md files:**
   ```bash
   find ~/.agents/skills/beacon -name SKILL.md
   ```

3. **Check beacon CLI:**
   ```bash
   which beacon
   beacon --help
   ```

4. **Restart AI assistant** (quit and relaunch completely)

### Duplicate skills warning

If you see duplicate beacon skills, ensure you only have ONE symlink per AI assistant:
- Remove any `~/.codex/skills/beacon` (use `~/.agents/skills/beacon` instead)
- Keep only one symlink in `~/.claude/skills/beacon`

### Permission issues

```bash
# Fix symlink permissions
chmod -R u+rw ~/Developer/Personal/products/beacon/skills/beacon
```

## Uninstalling

```bash
# Remove Codex symlink
rm ~/.agents/skills/beacon

# Remove Claude Code symlink
rm ~/.claude/skills/beacon

# Optionally uninstall beacon CLI
pip uninstall beacon
```

## Architecture Notes

- **Canonical install root**: `~/Developer/Personal/products/beacon/skills/beacon`
- **Codex discovery**: `~/.agents/skills/beacon` → single symlink (nested structure supported)
- **Claude Code discovery**: `~/.claude/skills/beacon-*` → multiple flat symlinks (only scans first level)
- **Single source of truth**: All skills live in the beacon repo, symlinks enable multi-AI discovery
- **No duplication**: Both AI assistants read from the same skill files through symlinks
- **Key difference**: Codex supports nested directories, Claude Code requires flat structure

### Why Flat Structure for Claude Code?

Claude Code's skill discovery only scans the first level of `~/.claude/skills/`. It does not recursively discover skills in subdirectories like `~/.claude/skills/beacon/beacon-prd/`. 

To make all beacon sub-skills visible, we create individual symlinks:
```
~/.claude/skills/beacon → .../skills/beacon (main)
~/.claude/skills/beacon-prd → .../skills/beacon/beacon-prd
~/.claude/skills/beacon-implement → .../skills/beacon/beacon-implement
... (one symlink per sub-skill)
```

This is similar to how superpowers handles multi-AI compatibility.

## Current Release

- **Version**: v1.3.3
- **Theme**: Core slimming, external skill demotion, minimal HUD
- **Human surface**: 6+3 commands (prd, user-story, test-case, implement, qa, release + help, status, doctor)
