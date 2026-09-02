# Guides

A Guide is an opinionated path that sequences several Practices toward a defined outcome, with an intended Practitioner, prerequisites, modules, a capstone, and an evaluation gate ([TAXONOMY.md](../docs/framework/TAXONOMY.md)). It orders existing Practices; it does not copy them.

## What exists

One Guide, The AI-Native Practitioner. Its front matter carries its `status` and `version`; this index does not restate them.

| File | What it holds | Open it when |
|---|---|---|
| [ai-native-practitioner/README.md](ai-native-practitioner/README.md) | The Guide: intended Practitioner, outcomes, prerequisites, the six-module path, capstone, evaluation gate, maintainers, changelog | You want the whole path and its completion gate |
| [ai-native-practitioner/CURRICULUM.md](ai-native-practitioner/CURRICULUM.md) | The curriculum map: per-module contracts, the applied, technical, and organizational route overlays, and the capstone dossier | You are working through the path or authoring a module |
| [01-foundations.md](ai-native-practitioner/01-foundations.md) | Module 1, Learn: frame a bounded AI task and produce a task-and-risk brief | You are starting |
| [02-effective-use.md](ai-native-practitioner/02-effective-use.md) | Module 2, Use: complete one discrete task deliberately and check it against a baseline | You have a task-and-risk brief |
| [03-context-engineering.md](ai-native-practitioner/03-context-engineering.md) | Module 3, Use: build a governed, maintainable context pack | You have a reviewed task record |
| [04-automation-agents.md](ai-native-practitioner/04-automation-agents.md) | Module 4, Automate: make a recurring workflow dependable before making it autonomous | You have a context pack |
| [05-agentic-engineering.md](ai-native-practitioner/05-agentic-engineering.md) | Module 5, Build: deliver a system change another engineer can inspect and recover | You have a workflow with an approval boundary |
| [06-organizational-ai.md](ai-native-practitioner/06-organizational-ai.md) | Module 6, Transform: tie the workflow to accountable operating change | You are changing how a team operates |

Modules 1–4 are the starter path; stopping there yields a checked workflow trial, not Guide completion. The methods the modules apply are the proposed candidates in [../practices/](../practices/README.md); a module link does not change a method's maturity, and promotion is a separate human decision.

## Add one

- Template: [GUIDE.md](../templates/GUIDE.md). Schema: [GUIDE_SCHEMA.md](../docs/schemas/GUIDE_SCHEMA.md). Flow: [../CONTRIBUTING.md](../CONTRIBUTING.md), "Guide, Lab, or Story" path.
- Layout: one directory per Guide. The Guide is that directory's `README.md` with front matter; modules are `NN-slug.md` files beside it. `python3 scripts/validate_artifacts.py` validates any file under `guides/` that carries front matter as a full Guide, and `NN-` files as modules.
- No Guide issue form exists; the Lab and Story forms cover the other two artifacts on that contribution path.
