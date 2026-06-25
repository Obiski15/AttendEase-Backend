# Git Branching & Collaboration Workflow

## 1. Branching Model

We use **Trunk-Based Development** with short-lived feature branches.

- **`main`**: Production-ready code. No developer commits directly to `main`.
- **`dev`**: The integration branch. All features are branched from `dev` and merged back via Pull Requests.

---

## 2. Branch Naming Conventions

Prefix your branch with the category, followed by a short descriptive name (kebab-case):

- **Features**: `feature/<feature-name>` (e.g., `feature/lecturer-dashboard`)
- **Bug Fixes**: `bugfix/<fix-name>` (e.g., `bugfix/qr-parsing-leak`)
- **Refactoring**: `refactor/<refactor-name>` (e.g., `refactor/reusable-alert-dialog`)
- **Documentation**: `docs/<doc-name>` (e.g., `docs/api-contracts`)

---

## 3. Pull Request Guidelines

1. **Before opening a Pull Request**:
   - Pull latest changes from `dev` and rebase your feature branch:
     ```bash
     git checkout dev
     git pull origin dev
     git checkout your-feature-branch
     git rebase dev
     ```
   - Ensure the project builds cleanly:
     - Android: `./gradlew compileDebugKotlin`
   - Run local unit tests:
     - `./gradlew test`

2. **Opening the PR**:
   - Provide a clear title referencing the task.
   - Add a brief summary of what was done.
   - Tag at least **one** other dever for code review.

3. **Merging**:
   - PRs can only be merged after receiving **at least 1 approval** and passing all automated checks.
   - Use **Squash and Merge** to keep a clean history.

---

## 4. Commit Message Standard

We follow **Conventional Commits**:
`<type>(<scope>): <description>`

- **`feat`**: A new feature (e.g., `feat: add lecturer active session`)
- **`fix`**: A bug fix (e.g., `fix: prevent crash on empty string`)
- **`refactor`**: Code changes that neither fix bugs nor add features (e.g., `refactor: extract shared function`)
