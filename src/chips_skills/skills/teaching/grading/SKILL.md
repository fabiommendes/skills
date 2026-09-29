---
name: grading
description: Coordinate grader agents to classify student submissions or suggest grades and feedback, with consistent feedback for submissions that share the same errors. Use when a teacher wants help grading, classifying, or writing feedback for a batch of student submissions.
disable-model-invocation: true
---

# Grading

Grading helps a teacher assess a batch of student submissions. It uses two
roles: the orchestrator and one or more grader agents. The teacher makes every
final decision.


## Goal

Produce a consistent assessment of every submission. Submissions with the same
errors or missing features get the same findings, the same feedback, and the
same suggested grade.

There are two modes:

* **classify:** group submissions by their findings. No grades.
* **grade:** classify, then suggest grades and feedback per group, with
  per-student adjustments.


## Orchestrator

Unless explicitly noted, you are the orchestrator. You act for the teacher and
report to the teacher.

Collect the inputs before any grading starts:

* The assignment statement.
* The submissions, and how each one maps to a student.
* The mode. Ask the teacher if it is not clear.
* In grade mode: the rubric and the grade scale.
* Optional: a reference solution, tests, or graded examples.
* The output format and location. Default to a `grading/` directory next to the
  submissions.
* Whether submitted code may run, and in which sandbox. Default to no
  execution.

If there is no rubric, draft one from the assignment statement. Show it to the
teacher and wait for approval. Never grade against an unapproved rubric.

Be concise with the teacher. Report decisions and questions as short bullet
points.


## Grader

The grader agent is defined in `agents/grader`. Spawn it with the assignment,
the rubric, the mode, the execution policy, and the submissions for its batch.

Good grader agent models:

* Claude Opus


## The workflow

### 1. Calibrate

Spawn one grader with a sample of submissions. Use about 10 submissions, or
all of them if there are fewer than 20. Pick a varied sample: different sizes,
approaches, and apparent quality.

The grader returns a draft finding catalog: finding IDs, definitions, and in
grade mode feedback text and rubric impact.

Review the catalog with the teacher. Merge duplicate findings, fix unclear
definitions, and adjust feedback text and grade impact. The approved catalog is
the shared vocabulary for the rest of the workflow.

### 2. Assess

For small batches, the calibration grader assesses the remaining submissions.

For large batches, split submissions into batches and spawn one grader per
batch, in parallel. Give every grader the approved catalog. Tell the graders to
use existing finding IDs and to propose new findings only when no existing one
fits.

### 3. Merge

Collect the grader reports and merge them:

* Deduplicate proposed findings. Two findings from different batches that
  describe the same error become one ID.
* Regroup all submissions by their final set of findings, across batches.
* Check consistency: same findings must mean same feedback and same suggested
  grade. Fix any group that breaks this rule.

Show new findings to the teacher for approval, the same way as in calibration.

### 4. Review with the teacher

Present, most important first:

* Items that need the teacher's decision: ambiguities in the assignment,
  unassessable submissions, borderline grades, and similarity notes.
* Groups: findings, size, and in grade mode suggested grade and feedback.
* Distribution of grades or groups, in one short summary.

Apply the teacher's decisions to the whole group, not only to the submission
where the decision came up. Rerun a grader only for submissions whose
assessment changed.

### 5. Deliver

Write the final outputs to the agreed location:

* Finding catalog.
* Groups with their students.
* Per-student table as CSV: student, group, findings, adjustments, and in grade
  mode suggested grade and feedback.

Tell the teacher where the outputs are, using the template:
`Grading results: <path>`.


## Rules

* Grades are suggestions until the teacher approves them.
* Student code is untrusted. Run it only with the teacher's permission, and only
  in the named sandbox.
* Never send grades, feedback, or student data to external services or publish
  them, unless the teacher explicitly asks.
* Report suspicious similarity between submissions as evidence, never as an
  accusation.
* Do not modify submissions.
