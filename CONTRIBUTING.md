# Contributing to SatyaMark

Thank you for your interest in contributing to **SatyaMark** 🎯
SatyaMark is an open-source, multi-modal verification infrastructure for text, images, and future media types. Contributions of all kinds are welcome.

This guide explains how you can contribute and what standards to follow.

---

## Ways to Contribute

You can help SatyaMark by:

* **Improving verification accuracy**

  * Text verification pipelines
  * **Image verification (most important focus area)**
* **Adding new verification modalities**

  * Video verification
  * Audio verification
* **Hybrid verification**

  * Content containing multiple elements such as:

    * Text + Image
    * Image + Audio
    * Video + Text + Audio
* Improving confidence scoring and explainability
* Enhancing SDKs, demos, or developer experience
* Improving documentation and examples
* Fixing bugs or refactoring existing code

Both small and large contributions are valued.

---

## Getting Started

1. **Fork** the repository on GitHub
2. **Clone** your fork locally:

   ```bash
   git clone https://github.com/<your-username>/SatyaMark.git
   ```
3. Create a new branch:

   ```bash
   git checkout -b feature/your-change
   ```

---

## Project Structure (High Level)

* `Backend/` – Core verification APIs and services
* `AI/` – Verification pipelines (text, image, ML, forensics)
* `Frontend/` – SDKs, demos, and documentation UI
* `Docs/` – Project documentation

Refer to module-level README files for detailed instructions.

---

## Development Guidelines

All contributions should follow these principles:

* Code must be **well-documented**
* Code should be **tested wherever applicable**
* Keep logic modular and easy to understand
* Prefer clarity over cleverness
* Follow existing patterns and naming conventions
* Update documentation when behavior changes

Poorly documented or untested changes may be requested for revision.

---

## Commit Messages

Use clear, conventional commit messages:

```text
feat: add image ensemble confidence scoring
fix: handle invalid image URLs
docs: update image verification README
```

---

## Submitting a Pull Request

1. Ensure your changes work locally
2. Add or update relevant documentation
3. Push your branch:

   ```bash
   git push origin feature/your-change
   ```
4. Open a Pull Request against the `main` branch
5. In the PR description, explain:

   * What you changed
   * Why the change is needed
   * Any limitations or future improvements

Pull requests should be focused and easy to review.

---

## Reporting Issues

If you find a bug or want to propose an enhancement:

* Open a GitHub Issue
* Provide clear reproduction steps (if applicable)
* Attach logs, screenshots, or sample inputs when useful

For security-related issues, follow **SECURITY.md**.

---

## Code of Conduct

All contributors are expected to follow the project’s
**Code of Conduct**. Please maintain a respectful and professional environment.

---

## License

By contributing to SatyaMark, you agree that your contributions will be licensed under the **MIT License**.

---

## Need Help?

If you’re unsure where to start:

* Look for issues labeled **good first issue**
* Improve documentation or examples
* Ask questions in issues or discussions

Your contributions help build a universal verification layer for the internet 🚀
