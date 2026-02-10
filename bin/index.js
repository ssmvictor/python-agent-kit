#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import readline from "node:readline";
import { fileURLToPath } from "node:url";

import chalk from "chalk";
import { Command } from "commander";
import { downloadTemplate } from "giget";
import ora from "ora";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const pkg = JSON.parse(
  fs.readFileSync(path.resolve(__dirname, "..", "package.json"), "utf8")
);

const REPOSITORY_SOURCE = "github:ssmvictor/python-agent-kit";
const AGENT_FOLDER_NAME = ".agent";
const OPENCODE_FOLDER_NAME = ".opencode";
const TEMP_FOLDER_NAME = ".temp_python_agent_kit";
const VALID_TARGETS = ["antigravity", "opencode", "both"];

// ---------------------------------------------------------------------------
// Tool name mapping: Antigravity tool names -> OpenCode tool names
// OpenCode supports: bash, edit, write, read, grep, glob, list, patch, skill,
//                    webfetch, todotask, todowrite, google_search, task
// ---------------------------------------------------------------------------
const TOOL_NAME_MAP = {
  read: "read",
  grep: "grep",
  glob: "glob",
  bash: "bash",
  edit: "edit",
  write: "write",
  agent: "task",
  // Tools that exist in Antigravity but have no direct OpenCode equivalent;
  // map them to the closest match.
  viewcodeitem: "read",
  findbyname: "glob",
};

// All tools we enable by default when an agent has no explicit tools list
const DEFAULT_OPENCODE_TOOLS = {
  read: true,
  grep: true,
  glob: true,
  bash: true,
  edit: true,
  write: true,
};

// ---------------------------------------------------------------------------
// Utility helpers
// ---------------------------------------------------------------------------

const normalizeOptions = (rawOptions) => {
  if (rawOptions && typeof rawOptions.opts === "function") {
    return rawOptions.opts();
  }
  return rawOptions ?? {};
};

const showBanner = (quiet) => {
  if (quiet) return;
  console.log(
    chalk.cyan(`
========================================
        PYTHON AGENT KIT CLI
========================================
`)
  );
};

const confirm = (question) =>
  new Promise((resolve) => {
    const interfaceInstance = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
    });
    interfaceInstance.question(chalk.yellow(`${question} (y/N): `), (answer) => {
      interfaceInstance.close();
      const normalized = answer.trim().toLowerCase();
      resolve(normalized === "y" || normalized === "yes");
    });
  });

const cleanupTemp = (tempDir) => {
  if (fs.existsSync(tempDir)) {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
};

const countEntries = (dirPath) => {
  let total = 0;
  const entries = fs.readdirSync(dirPath, { withFileTypes: true });
  for (const entry of entries) {
    total += 1;
    if (entry.isDirectory()) {
      total += countEntries(path.join(dirPath, entry.name));
    }
  }
  return total;
};

const ensureDirectoryExists = (dirPath) => {
  if (!fs.existsSync(dirPath) || !fs.statSync(dirPath).isDirectory()) {
    throw new Error(`Directory not found: ${dirPath}`);
  }
};

const printInitDryRun = (repoSource, agentDir, target) => {
  console.log(chalk.cyan("\n[Dry Run] No changes will be made\n"));
  console.log(chalk.white("Actions:"));
  console.log(chalk.gray("----------------------------------------"));
  console.log(`1) Download source:  ${chalk.cyan(repoSource)}`);
  console.log(`2) Install folder:   ${chalk.cyan(agentDir)}`);
  console.log(`3) Target platform:  ${chalk.cyan(target)}`);
  if (target === "opencode" || target === "both") {
    const opencodeDir = path.join(path.dirname(agentDir), OPENCODE_FOLDER_NAME);
    console.log(`4) OpenCode folder:  ${chalk.cyan(opencodeDir)}`);
    console.log(`5) Generate:         ${chalk.cyan("AGENTS.md (project root)")}`);
  }
  console.log(chalk.gray("----------------------------------------\n"));
};

// ---------------------------------------------------------------------------
// Frontmatter parser / serializer (lightweight, no external YAML dependency)
// ---------------------------------------------------------------------------

/**
 * Parse a markdown file with YAML frontmatter.
 * Returns { frontmatter: Record<string, string>, body: string }
 */
const parseFrontmatter = (content) => {
  const match = content.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?([\s\S]*)$/);
  if (!match) {
    return { frontmatter: {}, body: content };
  }

  const rawYaml = match[1];
  const body = match[2];
  const frontmatter = {};

  for (const line of rawYaml.split(/\r?\n/)) {
    const colonIndex = line.indexOf(":");
    if (colonIndex === -1) continue;
    const key = line.slice(0, colonIndex).trim();
    const value = line.slice(colonIndex + 1).trim();
    if (key) {
      frontmatter[key] = value;
    }
  }

  return { frontmatter, body };
};

/**
 * Serialize frontmatter + body back to a markdown string.
 * `fields` is an array of { key, value } where value can be a string or
 * a multi-line block (for YAML maps like tools).
 */
const serializeFrontmatter = (fields, body) => {
  let yaml = "---\n";
  for (const { key, value } of fields) {
    if (typeof value === "string") {
      yaml += `${key}: ${value}\n`;
    } else {
      // value is already a pre-formatted multi-line string
      yaml += value;
    }
  }
  yaml += "---\n";
  return yaml + body;
};

// ---------------------------------------------------------------------------
// OpenCode transformation functions
// ---------------------------------------------------------------------------

/**
 * Convert a comma-separated Antigravity tools string to an OpenCode tools
 * YAML map object. E.g. "Read, Grep, Glob, Bash" -> { read: true, grep: true, ... }
 */
const convertToolsList = (toolsString) => {
  if (!toolsString || !toolsString.trim()) {
    return { ...DEFAULT_OPENCODE_TOOLS };
  }

  const tools = {};
  const items = toolsString.split(",").map((t) => t.trim().toLowerCase());

  for (const item of items) {
    if (!item) continue;
    const mapped = TOOL_NAME_MAP[item] || item;
    tools[mapped] = true;
  }

  return tools;
};

/**
 * Format a tools object as a YAML block string for OpenCode frontmatter.
 */
const formatToolsYaml = (toolsObj) => {
  let result = "tools:\n";
  for (const [name, enabled] of Object.entries(toolsObj)) {
    result += `  ${name}: ${enabled}\n`;
  }
  return result;
};

/**
 * Transform an Antigravity agent .md file into OpenCode agent format.
 *
 * Antigravity format:
 *   name, description, tools (csv), model, skills (csv)
 *
 * OpenCode format:
 *   description, mode: subagent, tools: { read: true, ... }
 *   (name, model, skills are dropped from frontmatter; skills info goes into body)
 */
const transformAgentFile = (content) => {
  const { frontmatter, body } = parseFrontmatter(content);

  const description = frontmatter.description || "Specialist agent";
  const toolsObj = convertToolsList(frontmatter.tools);
  const skills = frontmatter.skills || "";
  const name = frontmatter.name || "";

  const fields = [
    { key: "description", value: description },
    { key: "mode", value: "subagent" },
    { key: "tools", value: formatToolsYaml(toolsObj) },
  ];

  // Preserve skills reference as a comment block at the top of the body
  let newBody = body;
  if (skills) {
    const skillsNote = `<!-- Antigravity skills: ${skills} -->\n`;
    // Only add if not already present
    if (!newBody.includes("Antigravity skills:")) {
      newBody = skillsNote + newBody;
    }
  }

  return serializeFrontmatter(fields, newBody);
};

/**
 * Transform an Antigravity workflow .md into an OpenCode command .md.
 *
 * Antigravity format:
 *   description
 *
 * OpenCode format:
 *   description, agent (optional)
 */
const transformWorkflowToCommand = (content, workflowName) => {
  const { frontmatter, body } = parseFrontmatter(content);

  const description = frontmatter.description || `${workflowName} workflow`;

  // Map certain workflows to a suggested default agent
  const agentMap = {
    test: "test-engineer",
    deploy: "devops-engineer",
    strict: "orchestrator",
    orchestrate: "orchestrator",
  };

  const agent = agentMap[workflowName] || "";

  const fields = [{ key: "description", value: description }];
  if (agent) {
    fields.push({ key: "agent", value: agent });
  }

  return serializeFrontmatter(fields, body);
};

/**
 * Transform an Antigravity skill SKILL.md into OpenCode skill format.
 *
 * Antigravity format:
 *   name, description, tier, allowed-tools, version, priority
 *
 * OpenCode format:
 *   name, description  (other fields kept as-is, they're harmless)
 *
 * Mostly compatible already - we just ensure name + description exist.
 */
const transformSkillFile = (content) => {
  const { frontmatter, body } = parseFrontmatter(content);

  // Skills are already compatible. Just pass through with minimal cleanup.
  const fields = [];

  if (frontmatter.name) {
    fields.push({ key: "name", value: frontmatter.name });
  }
  if (frontmatter.description) {
    fields.push({ key: "description", value: frontmatter.description });
  }

  return serializeFrontmatter(fields, body);
};

/**
 * Replace all occurrences of `.agent/` with `.opencode/` in text content.
 * Also replaces `\.agent\` for Windows-style paths in documentation.
 */
const replaceAgentPaths = (content) => {
  return content
    .replace(/\.agent\//g, `.opencode/`)
    .replace(/\.agent\\/g, `.opencode\\`);
};

/**
 * Check if a file is a text file (by extension) that we should process
 * for path replacement.
 */
const isTextFile = (filePath) => {
  const textExtensions = [
    ".md",
    ".txt",
    ".py",
    ".js",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".cfg",
    ".ini",
    ".sh",
    ".bat",
    ".ps1",
  ];
  const ext = path.extname(filePath).toLowerCase();
  return textExtensions.includes(ext);
};

/**
 * Recursively copy a directory, applying path replacements to text files.
 */
const copyWithPathReplacement = (srcDir, destDir) => {
  fs.mkdirSync(destDir, { recursive: true });

  const entries = fs.readdirSync(srcDir, { withFileTypes: true });
  for (const entry of entries) {
    const srcPath = path.join(srcDir, entry.name);
    const destPath = path.join(destDir, entry.name);

    if (entry.isDirectory()) {
      copyWithPathReplacement(srcPath, destPath);
    } else {
      if (isTextFile(srcPath)) {
        let content = fs.readFileSync(srcPath, "utf8");
        content = replaceAgentPaths(content);
        fs.writeFileSync(destPath, content, "utf8");
      } else {
        fs.copyFileSync(srcPath, destPath);
      }
    }
  }
};

/**
 * Generate the AGENTS.md root file for OpenCode.
 * This file acts as the "system prompt" / rules file for the project.
 */
const generateAgentsMd = (targetDir, agentDir) => {
  // Try to read the existing rules content from .agent/rules/GEMINI.md
  const geminiRulesPath = path.join(agentDir, "rules", "GEMINI.md");
  let rulesContent = "";
  if (fs.existsSync(geminiRulesPath)) {
    const { body } = parseFrontmatter(
      fs.readFileSync(geminiRulesPath, "utf8")
    );
    rulesContent = body.trim();
  }

  const content = `# Project Agent Instructions

> Auto-generated by Python Agent Kit CLI (target: opencode).
> Source of truth: \`.agent/\` folder. Re-run \`python-agent-kit init --target opencode\` to regenerate.

## Overview

This project uses the **Python Agent Kit** — a modular AI agent capability expansion kit.
Specialized agents, skills, and commands are available in the \`.opencode/\` directory.

## Available Agents

Check \`.opencode/agents/\` for specialist agents you can delegate to:
- **orchestrator** — Multi-agent coordination
- **backend-specialist** — Python APIs and integrations
- **frontend-specialist** — React/Next.js/Tailwind
- **test-engineer** — Testing and TDD
- **debugger** — Root cause analysis
- **security-auditor** — Security and OWASP
- **devops-engineer** — Deployment and CI/CD
- **database-architect** — Schema design and queries

## Available Commands

Check \`.opencode/commands/\` for workflow commands:
- **/test** — Run, generate, or improve tests
- **/deploy** — Production deployment workflow
- **/strict** — Enterprise-grade validation
- **/orchestrate** — Multi-agent coordination

## Available Skills

Check \`.opencode/skills/\` for domain-specific knowledge modules.

${rulesContent ? "## Operating Rules\n\n" + rulesContent : ""}
`;

  const agentsMdPath = path.join(targetDir, "AGENTS.md");
  fs.writeFileSync(agentsMdPath, content, "utf8");
  return agentsMdPath;
};

/**
 * Main OpenCode transformation pipeline.
 * Takes the installed .agent/ folder and generates .opencode/ alongside it.
 */
const transformToOpenCode = (targetDir, agentDir, spinner) => {
  const opencodeDir = path.join(targetDir, OPENCODE_FOLDER_NAME);

  // Clean existing .opencode/ if present
  if (fs.existsSync(opencodeDir)) {
    fs.rmSync(opencodeDir, { recursive: true, force: true });
  }
  fs.mkdirSync(opencodeDir, { recursive: true });

  // 1. Transform agents
  const agentsSrcDir = path.join(agentDir, "agents");
  const agentsDestDir = path.join(opencodeDir, "agents");
  if (fs.existsSync(agentsSrcDir)) {
    if (spinner) spinner.text = "Transforming agents...";
    fs.mkdirSync(agentsDestDir, { recursive: true });

    const agentFiles = fs.readdirSync(agentsSrcDir).filter((f) => f.endsWith(".md"));
    for (const file of agentFiles) {
      const srcPath = path.join(agentsSrcDir, file);
      let content = fs.readFileSync(srcPath, "utf8");
      content = transformAgentFile(content);
      content = replaceAgentPaths(content);
      fs.writeFileSync(path.join(agentsDestDir, file), content, "utf8");
    }
  }

  // 2. Transform workflows -> commands
  const workflowsSrcDir = path.join(agentDir, "workflows");
  const commandsDestDir = path.join(opencodeDir, "commands");
  if (fs.existsSync(workflowsSrcDir)) {
    if (spinner) spinner.text = "Transforming workflows to commands...";
    fs.mkdirSync(commandsDestDir, { recursive: true });

    const workflowFiles = fs
      .readdirSync(workflowsSrcDir)
      .filter((f) => f.endsWith(".md"));
    for (const file of workflowFiles) {
      const srcPath = path.join(workflowsSrcDir, file);
      const workflowName = path.basename(file, ".md");
      let content = fs.readFileSync(srcPath, "utf8");
      content = transformWorkflowToCommand(content, workflowName);
      content = replaceAgentPaths(content);
      fs.writeFileSync(path.join(commandsDestDir, file), content, "utf8");
    }
  }

  // 3. Transform skills
  const skillsSrcDir = path.join(agentDir, "skills");
  const skillsDestDir = path.join(opencodeDir, "skills");
  if (fs.existsSync(skillsSrcDir)) {
    if (spinner) spinner.text = "Transforming skills...";

    // Skills are nested: .agent/skills/<name>/SKILL.md
    // Some may have subdirectories (e.g., app-builder/templates/SKILL.md)
    const copySkillsRecursive = (src, dest) => {
      fs.mkdirSync(dest, { recursive: true });
      const entries = fs.readdirSync(src, { withFileTypes: true });

      for (const entry of entries) {
        const srcPath = path.join(src, entry.name);
        const destPath = path.join(dest, entry.name);

        if (entry.isDirectory()) {
          copySkillsRecursive(srcPath, destPath);
        } else if (entry.name === "SKILL.md") {
          let content = fs.readFileSync(srcPath, "utf8");
          content = transformSkillFile(content);
          content = replaceAgentPaths(content);
          fs.writeFileSync(destPath, content, "utf8");
        } else if (isTextFile(srcPath)) {
          let content = fs.readFileSync(srcPath, "utf8");
          content = replaceAgentPaths(content);
          fs.writeFileSync(destPath, content, "utf8");
        } else {
          fs.copyFileSync(srcPath, destPath);
        }
      }
    };

    copySkillsRecursive(skillsSrcDir, skillsDestDir);
  }

  // 4. Copy scripts (as-is, with path replacement in text files)
  const scriptsSrcDir = path.join(agentDir, "scripts");
  const scriptsDestDir = path.join(opencodeDir, "scripts");
  if (fs.existsSync(scriptsSrcDir)) {
    if (spinner) spinner.text = "Copying scripts...";
    copyWithPathReplacement(scriptsSrcDir, scriptsDestDir);
  }

  // 5. Copy rules (as-is, with path replacement)
  const rulesSrcDir = path.join(agentDir, "rules");
  const rulesDestDir = path.join(opencodeDir, "rules");
  if (fs.existsSync(rulesSrcDir)) {
    if (spinner) spinner.text = "Copying rules...";
    copyWithPathReplacement(rulesSrcDir, rulesDestDir);
  }

  // 6. Copy .shared (as-is, with path replacement)
  const sharedSrcDir = path.join(agentDir, ".shared");
  const sharedDestDir = path.join(opencodeDir, ".shared");
  if (fs.existsSync(sharedSrcDir)) {
    if (spinner) spinner.text = "Copying shared resources...";
    copyWithPathReplacement(sharedSrcDir, sharedDestDir);
  }

  // 7. Copy root-level .md files (ARCHITECTURE.md, STYLE-GUIDE.md, etc.)
  const rootFiles = fs
    .readdirSync(agentDir, { withFileTypes: true })
    .filter((e) => !e.isDirectory() && isTextFile(e.name));
  for (const entry of rootFiles) {
    const srcPath = path.join(agentDir, entry.name);
    const destPath = path.join(opencodeDir, entry.name);
    let content = fs.readFileSync(srcPath, "utf8");
    content = replaceAgentPaths(content);
    fs.writeFileSync(destPath, content, "utf8");
  }

  // 8. Generate AGENTS.md at project root
  if (spinner) spinner.text = "Generating AGENTS.md...";
  const agentsMdPath = generateAgentsMd(targetDir, agentDir);

  return { opencodeDir, agentsMdPath };
};

// ---------------------------------------------------------------------------
// Core install logic
// ---------------------------------------------------------------------------

const validateTarget = (target) => {
  if (!VALID_TARGETS.includes(target)) {
    console.error(
      chalk.red(
        `Invalid target: "${target}". Valid targets: ${VALID_TARGETS.join(", ")}`
      )
    );
    process.exit(1);
  }
};

const performInstall = async (rawOptions) => {
  const options = normalizeOptions(rawOptions);
  const quiet = Boolean(options.quiet);
  const dryRun = Boolean(options.dryRun);
  const force = Boolean(options.force);
  const target = options.target || "antigravity";

  validateTarget(target);

  if (!options.skipBanner) {
    showBanner(quiet);
  }

  const targetDir = path.resolve(options.path ?? process.cwd());
  ensureDirectoryExists(targetDir);

  const branchSuffix = options.branch ? `#${options.branch}` : "";
  const repoSource = `${REPOSITORY_SOURCE}${branchSuffix}`;
  const tempDir = path.join(targetDir, TEMP_FOLDER_NAME);
  const agentDir = path.join(targetDir, AGENT_FOLDER_NAME);
  const opencodeDir = path.join(targetDir, OPENCODE_FOLDER_NAME);

  if (dryRun) {
    printInitDryRun(repoSource, agentDir, target);
    return;
  }

  // Check which directories already exist based on the chosen target
  if (!force) {
    const existing = [];
    if ((target === "antigravity" || target === "both") && fs.existsSync(agentDir)) {
      existing.push(AGENT_FOLDER_NAME);
    }
    if ((target === "opencode" || target === "both") && fs.existsSync(opencodeDir)) {
      existing.push(OPENCODE_FOLDER_NAME);
    }

    if (existing.length > 0) {
      const shouldOverwrite = await confirm(
        `${existing.join(" and ")} already exist${existing.length === 1 ? "s" : ""}. Overwrite?`
      );
      if (!shouldOverwrite) {
        if (!quiet) console.log(chalk.gray("Operation cancelled."));
        return;
      }
    }
  }

  const spinner = quiet
    ? null
    : ora({ text: "Downloading repository...", color: "cyan" }).start();

  try {
    cleanupTemp(tempDir);

    await downloadTemplate(repoSource, {
      dir: tempDir,
      force: true,
    });

    if (spinner) spinner.text = "Installing .agent folder...";

    const sourceAgentDir = path.join(tempDir, AGENT_FOLDER_NAME);
    if (!fs.existsSync(sourceAgentDir)) {
      throw new Error(
        `Could not find ${AGENT_FOLDER_NAME} in downloaded repository.`
      );
    }

    // Always install .agent/ first (it's the source of truth)
    if (target === "antigravity" || target === "both") {
      if (fs.existsSync(agentDir)) {
        fs.rmSync(agentDir, { recursive: true, force: true });
      }
      fs.cpSync(sourceAgentDir, agentDir, { recursive: true });
    }

    // For opencode-only target, we still need .agent/ temporarily to transform
    // If the user chose "opencode" only, install to a temp location
    let agentSourceForTransform = agentDir;
    if (target === "opencode") {
      // Use the downloaded source directly for transformation
      agentSourceForTransform = sourceAgentDir;
    }

    // Run OpenCode transformation if needed
    if (target === "opencode" || target === "both") {
      if (spinner) spinner.text = "Generating OpenCode format (.opencode/)...";

      const { opencodeDir, agentsMdPath } = transformToOpenCode(
        targetDir,
        agentSourceForTransform,
        spinner
      );

      cleanupTemp(tempDir);

      if (spinner) spinner.succeed(chalk.green("Installation completed."));

      if (!quiet) {
        console.log(chalk.gray("----------------------------------------"));
        if (target === "both") {
          console.log(`Installed: ${chalk.cyan(agentDir)}`);
        }
        console.log(`Generated: ${chalk.cyan(opencodeDir)}`);
        console.log(`Generated: ${chalk.cyan(agentsMdPath)}`);
        console.log(chalk.gray("----------------------------------------"));
        console.log(
          chalk.gray(
            `Target: ${chalk.white(target)} | Source of truth: ${chalk.white(AGENT_FOLDER_NAME)}`
          )
        );
        console.log(chalk.green("Done."));
      }
    } else {
      // antigravity only
      cleanupTemp(tempDir);

      if (spinner) spinner.succeed(chalk.green("Installation completed."));

      if (!quiet) {
        console.log(chalk.gray("----------------------------------------"));
        console.log(`Installed: ${chalk.cyan(agentDir)}`);
        console.log(chalk.gray("----------------------------------------"));
        console.log(chalk.green("Done."));
      }
    }
  } catch (error) {
    cleanupTemp(tempDir);
    const message = error instanceof Error ? error.message : String(error);
    if (spinner) {
      spinner.fail(chalk.red(`Installation failed: ${message}`));
    } else {
      console.error(chalk.red(`Installation failed: ${message}`));
    }
    process.exit(1);
  }
};

// ---------------------------------------------------------------------------
// Commands
// ---------------------------------------------------------------------------

const initCommand = async (rawOptions) => {
  await performInstall(rawOptions);
};

const updateCommand = async (rawOptions) => {
  const options = normalizeOptions(rawOptions);
  const quiet = Boolean(options.quiet);
  const target = options.target || "antigravity";

  validateTarget(target);

  showBanner(quiet);

  const targetDir = path.resolve(options.path ?? process.cwd());
  ensureDirectoryExists(targetDir);

  // Check that something is already installed
  const agentDir = path.join(targetDir, AGENT_FOLDER_NAME);
  const opencodeDir = path.join(targetDir, OPENCODE_FOLDER_NAME);
  const hasAgent = fs.existsSync(agentDir);
  const hasOpencode = fs.existsSync(opencodeDir);

  if (!hasAgent && !hasOpencode) {
    console.error(
      chalk.red(
        `No installation found in: ${targetDir}. Run python-agent-kit init first.`
      )
    );
    process.exit(1);
  }

  if (!options.force && !options.dryRun) {
    const folders = [];
    if ((target === "antigravity" || target === "both") && hasAgent)
      folders.push(AGENT_FOLDER_NAME);
    if ((target === "opencode" || target === "both") && hasOpencode)
      folders.push(OPENCODE_FOLDER_NAME);

    const folderList = folders.join(" and ") || "installation";
    const shouldUpdate = await confirm(
      `Update will overwrite ${folderList}. Continue?`
    );
    if (!shouldUpdate) {
      if (!quiet) console.log(chalk.gray("Operation cancelled."));
      return;
    }
  }

  await performInstall({
    ...options,
    force: true,
    skipBanner: true,
  });
};

const statusCommand = (rawOptions) => {
  const options = normalizeOptions(rawOptions);
  const targetDir = path.resolve(options.path ?? process.cwd());

  ensureDirectoryExists(targetDir);

  const agentDir = path.join(targetDir, AGENT_FOLDER_NAME);
  const opencodeDir = path.join(targetDir, OPENCODE_FOLDER_NAME);
  const agentsMdPath = path.join(targetDir, "AGENTS.md");

  const hasAgent = fs.existsSync(agentDir);
  const hasOpencode = fs.existsSync(opencodeDir);
  const hasAgentsMd = fs.existsSync(agentsMdPath);

  console.log(chalk.cyan("\nPython Agent Kit status\n"));

  if (!hasAgent && !hasOpencode) {
    console.log(chalk.red("Status: not installed"));
    console.log(chalk.yellow("Run `python-agent-kit init` to install.\n"));
    return;
  }

  console.log(chalk.green("Status: installed"));
  console.log(chalk.gray("----------------------------------------"));

  if (hasAgent) {
    const stats = fs.statSync(agentDir);
    const totalEntries = countEntries(agentDir);
    console.log(chalk.white("\n  .agent/ (Antigravity)"));
    console.log(`  Path:     ${chalk.cyan(agentDir)}`);
    console.log(`  Modified: ${chalk.gray(stats.mtime.toLocaleString("en-US"))}`);
    console.log(`  Entries:  ${chalk.yellow(totalEntries)}`);
  }

  if (hasOpencode) {
    const stats = fs.statSync(opencodeDir);
    const totalEntries = countEntries(opencodeDir);
    console.log(chalk.white("\n  .opencode/ (OpenCode)"));
    console.log(`  Path:     ${chalk.cyan(opencodeDir)}`);
    console.log(`  Modified: ${chalk.gray(stats.mtime.toLocaleString("en-US"))}`);
    console.log(`  Entries:  ${chalk.yellow(totalEntries)}`);
  }

  if (hasAgentsMd) {
    console.log(chalk.white("\n  AGENTS.md"));
    console.log(`  Path:     ${chalk.cyan(agentsMdPath)}`);
    console.log(`  Status:   ${chalk.green("present")}`);
  }

  console.log(chalk.gray("\n----------------------------------------\n"));
};

// ---------------------------------------------------------------------------
// Error wrapper
// ---------------------------------------------------------------------------

const withErrorHandling = (handler) => async (rawOptions) => {
  try {
    await handler(rawOptions);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    console.error(chalk.red(`Error: ${message}`));
    process.exit(1);
  }
};

// ---------------------------------------------------------------------------
// CLI definition
// ---------------------------------------------------------------------------

const targetOption = [
  "-t, --target <platform>",
  `Target platform: ${VALID_TARGETS.join(", ")}`,
  "antigravity",
];

const program = new Command();
program
  .name("python-agent-kit")
  .description("CLI tool to install and manage Python Agent Kit")
  .version(pkg.version, "-v, --version", "Display version number")
  .showHelpAfterError();

program
  .command("init")
  .description("Install .agent folder into your project")
  .option("-f, --force", "Overwrite if already exists", false)
  .option("-p, --path <dir>", "Target project directory", process.cwd())
  .option("-b, --branch <name>", "Repository branch to use")
  .option("-q, --quiet", "Suppress output", false)
  .option("--dry-run", "Preview without writing files", false)
  .option(...targetOption)
  .action(withErrorHandling(initCommand));

program
  .command("update")
  .description("Update existing installation")
  .option("-f, --force", "Skip confirmation prompt", false)
  .option("-p, --path <dir>", "Target project directory", process.cwd())
  .option("-b, --branch <name>", "Repository branch to use")
  .option("-q, --quiet", "Suppress output", false)
  .option("--dry-run", "Preview without writing files", false)
  .option(...targetOption)
  .action(withErrorHandling(updateCommand));

program
  .command("status")
  .description("Check installation status")
  .option("-p, --path <dir>", "Target project directory", process.cwd())
  .action(withErrorHandling(statusCommand));

program.parse(process.argv);

if (process.argv.slice(2).length === 0) {
  program.outputHelp();
}
