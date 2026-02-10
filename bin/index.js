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
const TEMP_FOLDER_NAME = ".temp_python_agent_kit";

const normalizeOptions = (rawOptions) => {
  if (rawOptions && typeof rawOptions.opts === "function") {
    return rawOptions.opts();
  }
  return rawOptions ?? {};
};

const showBanner = (quiet) => {
  if (quiet) {
    return;
  }

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

const printInitDryRun = (repoSource, agentDir) => {
  console.log(chalk.cyan("\n[Dry Run] No changes will be made\n"));
  console.log(chalk.white("Actions:"));
  console.log(chalk.gray("----------------------------------------"));
  console.log(`1) Download source: ${chalk.cyan(repoSource)}`);
  console.log(`2) Install folder:  ${chalk.cyan(agentDir)}`);
  console.log(chalk.gray("----------------------------------------\n"));
};

const performInstall = async (rawOptions) => {
  const options = normalizeOptions(rawOptions);
  const quiet = Boolean(options.quiet);
  const dryRun = Boolean(options.dryRun);
  const force = Boolean(options.force);

  if (!options.skipBanner) {
    showBanner(quiet);
  }

  const targetDir = path.resolve(options.path ?? process.cwd());
  ensureDirectoryExists(targetDir);

  const branchSuffix = options.branch ? `#${options.branch}` : "";
  const repoSource = `${REPOSITORY_SOURCE}${branchSuffix}`;
  const tempDir = path.join(targetDir, TEMP_FOLDER_NAME);
  const agentDir = path.join(targetDir, AGENT_FOLDER_NAME);

  if (dryRun) {
    printInitDryRun(repoSource, agentDir);
    return;
  }

  if (fs.existsSync(agentDir) && !force) {
    const shouldOverwrite = await confirm(
      `${AGENT_FOLDER_NAME} already exists. Overwrite it?`
    );

    if (!shouldOverwrite) {
      if (!quiet) {
        console.log(chalk.gray("Operation cancelled."));
      }
      return;
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

    if (spinner) {
      spinner.text = "Installing .agent folder...";
    }

    const sourceAgentDir = path.join(tempDir, AGENT_FOLDER_NAME);
    if (!fs.existsSync(sourceAgentDir)) {
      throw new Error(
        `Could not find ${AGENT_FOLDER_NAME} in downloaded repository.`
      );
    }

    if (fs.existsSync(agentDir)) {
      fs.rmSync(agentDir, { recursive: true, force: true });
    }

    fs.cpSync(sourceAgentDir, agentDir, { recursive: true });
    cleanupTemp(tempDir);

    if (spinner) {
      spinner.succeed(chalk.green("Installation completed."));
    }

    if (!quiet) {
      console.log(chalk.gray("----------------------------------------"));
      console.log(`Installed: ${chalk.cyan(agentDir)}`);
      console.log(chalk.gray("----------------------------------------"));
      console.log(chalk.green("Done."));
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

const initCommand = async (rawOptions) => {
  await performInstall(rawOptions);
};

const updateCommand = async (rawOptions) => {
  const options = normalizeOptions(rawOptions);
  const quiet = Boolean(options.quiet);

  showBanner(quiet);

  const targetDir = path.resolve(options.path ?? process.cwd());
  ensureDirectoryExists(targetDir);

  const agentDir = path.join(targetDir, AGENT_FOLDER_NAME);
  if (!fs.existsSync(agentDir)) {
    console.error(
      chalk.red(
        `Could not find ${AGENT_FOLDER_NAME} in: ${targetDir}. Run python-agent-kit init first.`
      )
    );
    process.exit(1);
  }

  if (!options.force && !options.dryRun) {
    const shouldUpdate = await confirm(
      `Update will overwrite ${AGENT_FOLDER_NAME}. Continue?`
    );

    if (!shouldUpdate) {
      if (!quiet) {
        console.log(chalk.gray("Operation cancelled."));
      }
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
  console.log(chalk.cyan("\nPython Agent Kit status\n"));

  if (!fs.existsSync(agentDir)) {
    console.log(chalk.red("Status: not installed"));
    console.log(chalk.yellow("Run `python-agent-kit init` to install.\n"));
    return;
  }

  const stats = fs.statSync(agentDir);
  const totalEntries = countEntries(agentDir);

  console.log(chalk.green("Status: installed"));
  console.log(chalk.gray("----------------------------------------"));
  console.log(`Path:     ${chalk.cyan(agentDir)}`);
  console.log(`Modified: ${chalk.gray(stats.mtime.toLocaleString("en-US"))}`);
  console.log(`Entries:  ${chalk.yellow(totalEntries)}`);
  console.log(chalk.gray("----------------------------------------\n"));
};

const withErrorHandling = (handler) => async (rawOptions) => {
  try {
    await handler(rawOptions);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    console.error(chalk.red(`Error: ${message}`));
    process.exit(1);
  }
};

const program = new Command();
program
  .name("python-agent-kit")
  .description("CLI tool to install and manage Python Agent Kit")
  .version(pkg.version, "-v, --version", "Display version number")
  .showHelpAfterError();

program
  .command("init")
  .description("Install .agent folder into your project")
  .option("-f, --force", "Overwrite if .agent already exists", false)
  .option("-p, --path <dir>", "Target project directory", process.cwd())
  .option("-b, --branch <name>", "Repository branch to use")
  .option("-q, --quiet", "Suppress output", false)
  .option("--dry-run", "Preview without writing files", false)
  .action(withErrorHandling(initCommand));

program
  .command("update")
  .description("Update existing .agent folder")
  .option("-f, --force", "Skip confirmation prompt", false)
  .option("-p, --path <dir>", "Target project directory", process.cwd())
  .option("-b, --branch <name>", "Repository branch to use")
  .option("-q, --quiet", "Suppress output", false)
  .option("--dry-run", "Preview without writing files", false)
  .action(withErrorHandling(updateCommand));

program
  .command("status")
  .description("Check .agent installation status")
  .option("-p, --path <dir>", "Target project directory", process.cwd())
  .action(withErrorHandling(statusCommand));

program.parse(process.argv);

if (process.argv.slice(2).length === 0) {
  program.outputHelp();
}
