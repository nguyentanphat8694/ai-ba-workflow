#!/usr/bin/env node
"use strict";

/**
 * ai-ba-workflow
 *
 * Scaffolds the BA Spec Harness into the current project for a chosen agent.
 *
 * What it does:
 *   1. Asks which agent you use (kiro / claude / gemini).
 *   2. Downloads the shared `harness/` tree from the GitHub repo.
 *   3. Downloads the loader file(s) specific to the chosen agent:
 *        - kiro   -> .kiro/steering/harness.md
 *        - claude -> CLAUDE.md
 *        - gemini -> GEMINI.md
 *   4. Creates empty `inputs/` and `outputs/` folders.
 *
 * It writes into the directory you run it from (process.cwd()).
 */

const fs = require("fs");
const path = require("path");
const https = require("https");
const readline = require("readline");
const { spawn } = require("child_process");

// ---- Config -----------------------------------------------------------

const REPO_OWNER = "nguyentanphat8694";
const REPO_NAME = "ai-ba-workflow";
const REPO_BRANCH = "main";

// Loader files per agent. "src" is the path inside the repo, "dest" is where
// it lands in the user's project (relative to cwd).
const AGENT_FILES = {
  kiro: [{ src: ".kiro/steering/harness.md", dest: ".kiro/steering/harness.md" }],
  claude: [{ src: "CLAUDE.md", dest: "CLAUDE.md" }],
  gemini: [{ src: "GEMINI.md", dest: "GEMINI.md" }],
};

// Folders to create empty (so the pipeline has somewhere to read/write).
const EMPTY_DIRS = ["inputs", "outputs"];

// ---- Tiny color helpers (no dependency) -------------------------------

const useColor = process.stdout.isTTY;
const c = (code, s) => (useColor ? `\x1b[${code}m${s}\x1b[0m` : s);
const bold = (s) => c("1", s);
const green = (s) => c("32", s);
const yellow = (s) => c("33", s);
const cyan = (s) => c("36", s);
const red = (s) => c("31", s);
const dim = (s) => c("2", s);

// ---- HTTP helpers -----------------------------------------------------

function httpsGet(url, { json = false } = {}) {
  return new Promise((resolve, reject) => {
    const req = https.get(
      url,
      {
        headers: {
          "User-Agent": "ai-ba-workflow-cli",
          Accept: json ? "application/vnd.github+json" : "*/*",
        },
      },
      (res) => {
        // Follow redirects (raw.githubusercontent sometimes 302s).
        if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
          res.resume();
          httpsGet(res.headers.location, { json }).then(resolve, reject);
          return;
        }
        if (res.statusCode !== 200) {
          res.resume();
          reject(new Error(`HTTP ${res.statusCode} for ${url}`));
          return;
        }
        const chunks = [];
        res.on("data", (d) => chunks.push(d));
        res.on("end", () => {
          const buf = Buffer.concat(chunks);
          if (json) {
            try {
              resolve(JSON.parse(buf.toString("utf8")));
            } catch (e) {
              reject(new Error(`Bad JSON from ${url}: ${e.message}`));
            }
          } else {
            resolve(buf);
          }
        });
      }
    );
    req.on("error", reject);
    req.setTimeout(30000, () => {
      req.destroy(new Error(`Timeout fetching ${url}`));
    });
  });
}

// Recursively list every file under a repo directory using the GitHub
// contents API. Returns an array of repo-relative file paths.
async function listRepoDir(dirPath) {
  const api = `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/contents/${encodeURI(
    dirPath
  )}?ref=${REPO_BRANCH}`;
  const entries = await httpsGet(api, { json: true });
  const files = [];
  for (const entry of entries) {
    if (entry.type === "dir") {
      const nested = await listRepoDir(entry.path);
      files.push(...nested);
    } else if (entry.type === "file") {
      files.push(entry.path);
    }
  }
  return files;
}

function rawUrl(repoPath) {
  return `https://raw.githubusercontent.com/${REPO_OWNER}/${REPO_NAME}/${REPO_BRANCH}/${repoPath
    .split("/")
    .map(encodeURIComponent)
    .join("/")}`;
}

async function downloadFile(repoPath, destAbs) {
  const data = await httpsGet(rawUrl(repoPath));
  fs.mkdirSync(path.dirname(destAbs), { recursive: true });
  fs.writeFileSync(destAbs, data);
}

// ---- Prompt -----------------------------------------------------------

function ask(question) {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      rl.close();
      resolve(answer.trim());
    });
  });
}

// Yes/no prompt. Returns true for yes. `defaultYes` controls the answer on
// an empty Enter press. If stdin isn't a TTY (non-interactive run), falls
// back to the default without blocking.
async function askYesNo(question, defaultYes = false) {
  if (!process.stdin.isTTY) return defaultYes;
  const hint = defaultYes ? "(Y/n)" : "(y/N)";
  while (true) {
    const answer = (await ask(`${question} ${hint} `)).toLowerCase();
    if (answer === "") return defaultYes;
    if (["y", "yes"].includes(answer)) return true;
    if (["n", "no"].includes(answer)) return false;
    console.log(red("Please answer y or n.\n"));
  }
}

// Run a command inheriting stdio so the user sees its live output.
// Resolves with the exit code; never rejects.
function runCommand(command, args) {
  return new Promise((resolve) => {
    const child = spawn(command, args, { stdio: "inherit", shell: process.platform === "win32" });
    child.on("error", (e) => {
      console.error(red(`Failed to run ${command}: ${e.message}`));
      resolve(1);
    });
    child.on("close", (code) => resolve(code == null ? 1 : code));
  });
}

async function chooseAgent(cliArg) {
  const valid = Object.keys(AGENT_FILES);

  // Allow non-interactive use: `npx ai-ba-workflow kiro`
  if (cliArg && valid.includes(cliArg.toLowerCase())) {
    return cliArg.toLowerCase();
  }

  console.log(bold("\nWhich agent are you using?\n"));
  console.log(`  ${cyan("1")}) kiro    ${dim("-> .kiro/steering/harness.md")}`);
  console.log(`  ${cyan("2")}) claude  ${dim("-> CLAUDE.md")}`);
  console.log(`  ${cyan("3")}) gemini  ${dim("-> GEMINI.md")}`);
  console.log("");

  const map = { 1: "kiro", kiro: "kiro", 2: "claude", claude: "claude", 3: "gemini", gemini: "gemini" };

  while (true) {
    const answer = (await ask("Enter 1-3 (or name): ")).toLowerCase();
    const picked = map[answer];
    if (picked) return picked;
    console.log(red("Invalid choice. Type 1, 2, 3, or kiro/claude/gemini.\n"));
  }
}

// ---- Main -------------------------------------------------------------

async function main() {
  const target = process.cwd();

  console.log(bold(cyan("\n  BA Spec Harness installer")));
  console.log(dim(`  repo: github.com/${REPO_OWNER}/${REPO_NAME} (branch: ${REPO_BRANCH})`));
  console.log(dim(`  into: ${target}`));

  const agent = await chooseAgent(process.argv[2]);
  console.log(`\n${green("✓")} Agent: ${bold(agent)}\n`);

  // 1. Figure out the full list of harness files from GitHub.
  process.stdout.write(dim("Reading harness/ file list from GitHub... "));
  let harnessFiles;
  try {
    harnessFiles = await listRepoDir("harness");
  } catch (e) {
    console.log(red("failed."));
    console.error(red(`\nCould not list the harness/ directory: ${e.message}`));
    console.error(
      dim(
        "If this is a rate-limit error, wait a minute and retry, or set GITHUB_TOKEN. " +
          "Also confirm the repo and branch exist and are public."
      )
    );
    process.exit(1);
  }
  console.log(green(`${harnessFiles.length} files.`));

  // 2. Build the full download plan: shared harness + agent loader files.
  const plan = [
    ...harnessFiles.map((p) => ({ src: p, dest: p })),
    ...AGENT_FILES[agent],
  ];

  // 3. Download everything.
  console.log(bold(`\nDownloading ${plan.length} files...\n`));
  let done = 0;
  for (const item of plan) {
    const destAbs = path.join(target, item.dest);
    try {
      await downloadFile(item.src, destAbs);
      done++;
      console.log(`  ${green("✓")} ${item.dest}`);
    } catch (e) {
      console.log(`  ${red("✗")} ${item.dest} ${dim(`(${e.message})`)}`);
    }
  }

  // 4. Make sure the working folders exist.
  for (const d of EMPTY_DIRS) {
    const abs = path.join(target, d);
    fs.mkdirSync(abs, { recursive: true });
    const keep = path.join(abs, ".gitkeep");
    if (!fs.existsSync(keep)) fs.writeFileSync(keep, "");
  }

  // 5. Report.
  console.log("");
  if (done === plan.length) {
    console.log(green(bold("Done.")) + ` Installed the harness for ${bold(agent)}.`);
  } else {
    console.log(
      yellow(bold("Finished with some errors.")) +
        ` ${done}/${plan.length} files downloaded.`
    );
  }

  // 6. Optionally install the PDF reading skill.
  // Non-interactive override: pass --pdf / --no-pdf, or set AI_BA_PDF=1/0.
  console.log("");
  const argv = process.argv.slice(2).map((a) => a.toLowerCase());
  let wantPdf;
  if (argv.includes("--pdf") || process.env.AI_BA_PDF === "1") {
    wantPdf = true;
  } else if (argv.includes("--no-pdf") || process.env.AI_BA_PDF === "0") {
    wantPdf = false;
  } else {
    wantPdf = await askYesNo(
      "Install the agent skill to read PDFs (anthropics/skills -> pdf)?",
      false
    );
  }
  if (wantPdf) {
    console.log(dim("\nRunning: npx skills add https://github.com/anthropics/skills --skill pdf\n"));
    const code = await runCommand("npx", [
      "skills",
      "add",
      "https://github.com/anthropics/skills",
      "--skill",
      "pdf",
    ]);
    if (code === 0) {
      console.log(green("\n✓ PDF skill installed."));
    } else {
      console.log(yellow(`\nPDF skill install exited with code ${code}. You can retry manually:`));
      console.log(dim("  npx skills add https://github.com/anthropics/skills --skill pdf"));
    }
  } else {
    console.log(dim("Skipped PDF skill install."));
  }

  console.log(dim("\nNext steps:"));
  console.log(dim("  1. Drop a raw draft into ./inputs/"));
  if (agent === "kiro") {
    console.log(dim("  2. Open this folder in Kiro and say e.g. \"analyze <file>\"."));
  } else if (agent === "claude") {
    console.log(dim("  2. Run Claude Code in this folder and say e.g. \"analyze <file>\"."));
  } else {
    console.log(dim("  2. Run Gemini CLI in this folder and say e.g. \"analyze <file>\"."));
  }
  console.log("");
}

main().catch((e) => {
  console.error(red(`\nUnexpected error: ${e.message}`));
  process.exit(1);
});
