// ─── CI/CD Pipeline Generation ─────────────────────────────────────────────────
// Generates CI/CD configuration files based on the team context profile.
// ──────────────────────────────────────────────────────────────────────────────

import type { TeamContextProfile } from "@/core/context/types";

/** Generate a CI/CD configuration file */
export function generateCICDConfig(context: TeamContextProfile): {
  filename: string;
  content: string;
} {
  const provider = context.infra?.cicd?.provider ?? "github-actions";

  switch (provider) {
    case "github-actions":
      return generateGitHubActions(context);
    case "gitlab-ci":
      return generateGitLabCI(context);
    default:
      return generateGitHubActions(context);
  }
}

function generateGitHubActions(context: TeamContextProfile): {
  filename: string;
  content: string;
} {
  const hasTests =
    context.codePatterns?.testFramework &&
    context.codePatterns.testFramework !== "none";
  const deployBranch = context.infra?.cicd?.autoDeployBranch ?? "main";

  let content = `name: CI/CD Pipeline

on:
  push:
    branches: [${deployBranch}]
  pull_request:
    branches: [${deployBranch}]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Lint
        run: npm run lint
`;

  if (hasTests) {
    content += `
      - name: Run tests
        run: npm test
`;
  }

  content += `
      - name: Build
        run: npm run build
`;

  // Add deployment step based on hosting
  const hosting = context.infra?.hosting;
  if (hosting === "vercel") {
    content += `
  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/${deployBranch}'

    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: \${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: \${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: \${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
`;
  }

  return { filename: ".github/workflows/ci.yml", content };
}

function generateGitLabCI(context: TeamContextProfile): {
  filename: string;
  content: string;
} {
  const hasTests =
    context.codePatterns?.testFramework &&
    context.codePatterns.testFramework !== "none";

  let content = `stages:
  - build
  - test
  - deploy

build:
  stage: build
  image: node:20
  script:
    - npm ci
    - npm run build
  artifacts:
    paths:
      - dist/
`;

  if (hasTests) {
    content += `
test:
  stage: test
  image: node:20
  script:
    - npm ci
    - npm test
`;
  }

  return { filename: ".gitlab-ci.yml", content };
}
