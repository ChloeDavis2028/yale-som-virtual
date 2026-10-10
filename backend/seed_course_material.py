"""Build data/course_material.db: course questions and answers the AI avatars can look up.

    backend/.venv/Scripts/python backend/seed_course_material.py

One table, course_qa(id, course_number, topic, question, answer). Re-running rebuilds it.
Add rows to QA below to teach the avatars more material.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "data" / "course_material.db"

STATS = "MGT 403"  # Probability Modeling & Statistics
AI = "MGT 409"  # AI Foundations for Managers

QA = [
    # ---- probability and distributions
    (STATS, "probability", "What is a random variable?",
     "A number whose value depends on chance, like the number of customers who walk in tomorrow. "
     "It has a distribution that says how likely each value is."),
    (STATS, "expected value", "What is the expected value?",
     "The long-run average of a random variable: E[X] = sum of x·P(X = x). Over many repeats, the average "
     "outcome gets close to E[X]."),
    (STATS, "variance", "What is variance and why do we use it?",
     "Variance measures how spread out a random variable is around its mean: Var(X) = E[(X − μ)²]. "
     "Squaring keeps positive and negative deviations from cancelling. Its units are squared, which is why "
     "we often report the standard deviation instead."),
    (STATS, "standard deviation", "What is the difference between variance and standard deviation?",
     "Standard deviation is the square root of variance: σ = √Var(X). It is in the same units as the data, "
     "so it is easier to interpret (e.g. 'sales vary by about ±$2,000')."),
    (STATS, "variance", "What is the variance of a sum of random variables?",
     "Var(X + Y) = Var(X) + Var(Y) + 2·Cov(X, Y). If X and Y are independent the covariance is 0, so the "
     "variances just add. Diversification works because negatively correlated assets reduce total variance."),
    (STATS, "normal distribution", "What is the normal distribution?",
     "The bell curve, set by its mean μ and standard deviation σ. About 68% of values fall within 1σ of the "
     "mean, 95% within 2σ, and 99.7% within 3σ."),
    (STATS, "bayes rule", "What is Bayes' rule?",
     "P(A | B) = P(B | A)·P(A) / P(B). It updates a prior belief P(A) with evidence B. Base rates matter: a "
     "99%-accurate test for a rare disease still produces mostly false positives."),
    # ---- sampling and inference
    (STATS, "central limit theorem", "What is the central limit theorem?",
     "For a large enough sample (rule of thumb n ≥ 30), the sample mean is approximately normal, no matter "
     "what the population looks like. Its mean is μ and its standard deviation (the standard error) is σ/√n."),
    (STATS, "central limit theorem", "Why does the central limit theorem matter for managers?",
     "It lets you use the normal distribution to make confidence intervals and tests about averages (mean "
     "order size, average wait time) even when individual values are skewed."),
    (STATS, "standard error", "What is the standard error?",
     "The standard deviation of an estimate across repeated samples. For a sample mean it is σ/√n, so "
     "quadrupling the sample size halves the standard error."),
    (STATS, "confidence intervals", "What is a confidence interval?",
     "A range that captures the true parameter in a stated share of repeated samples. A 95% interval for a "
     "mean is x̄ ± 1.96·(s/√n) for large samples (use a t value for small ones)."),
    (STATS, "confidence intervals", "What does '95% confidence' actually mean?",
     "If you repeated the sampling many times, about 95% of the intervals you build would contain the true "
     "value. It does NOT mean there is a 95% chance the true value is in this one interval."),
    (STATS, "confidence intervals", "How do I make a confidence interval narrower?",
     "Take a bigger sample (width shrinks like 1/√n), accept a lower confidence level, or reduce noise in the "
     "data. Going from n = 100 to n = 400 cuts the width in half."),
    (STATS, "hypothesis testing", "What is a p-value?",
     "The probability of seeing data at least as extreme as yours if the null hypothesis were true. A small "
     "p-value (often < 0.05) means the data would be surprising under the null, so you reject it. It is not "
     "the probability that the null is true."),
    (STATS, "hypothesis testing", "What are type I and type II errors?",
     "Type I: rejecting a true null (a false alarm), with probability α. Type II: failing to reject a false "
     "null (a missed effect), with probability β. Power = 1 − β."),
    # ---- regression
    (STATS, "regression", "What is linear regression?",
     "A model that fits a straight line y = β₀ + β₁x + ε by least squares, minimizing the sum of squared "
     "errors. β₁ is the expected change in y for a one-unit increase in x."),
    (STATS, "regression", "How do I interpret a regression coefficient?",
     "Holding the other variables constant, a one-unit increase in that x is associated with a change of β in "
     "y on average. It is an association, not proof of causation."),
    (STATS, "regression", "What does R-squared mean?",
     "The share of the variation in y explained by the model, from 0 to 1. A high R² does not mean the model "
     "is causal or useful for prediction outside the data's range."),
    (STATS, "regression", "What is multicollinearity?",
     "When predictors are highly correlated with each other. Coefficients become unstable with large standard "
     "errors, even though overall predictions can still be fine."),
    (STATS, "regression", "Correlation vs causation?",
     "Correlation means two variables move together. Causation needs more: an experiment (A/B test) or a design "
     "that rules out confounders. Ice cream sales and drownings are correlated because of summer heat."),
    # ---- AI agents (today's MGT 409 lecture)
    (AI, "ai agents", "What is an AI agent?",
     "A model plus instructions plus tools, running in a loop: it reads the request, decides whether to call a "
     "tool, reads the result, and repeats until it can give a final (ideally typed) answer."),
    (AI, "pydanticai", "How do I build an agent in PydanticAI?",
     "agent = Agent(model, instructions='...'); add tools with @agent.tool (gets RunContext) or "
     "@agent.tool_plain; run it with result = agent.run_sync('prompt') and read result.output."),
    (AI, "pydanticai", "What is output_type in PydanticAI?",
     "Pass a Pydantic model as output_type and the agent must return data that validates against it, so "
     "result.output is a typed object instead of free text."),
    (AI, "pydanticai", "What is the difference between run and run_sync?",
     "run is async (await agent.run(...)), good inside web servers like FastAPI. run_sync blocks until done, "
     "handy in scripts and notebooks."),
]


def main() -> None:
    DB.parent.mkdir(exist_ok=True)
    con = sqlite3.connect(DB)
    con.executescript(
        "DROP TABLE IF EXISTS course_qa;"
        "CREATE TABLE course_qa (id INTEGER PRIMARY KEY, course_number TEXT, topic TEXT, question TEXT, answer TEXT);"
    )
    con.executemany("INSERT INTO course_qa (course_number, topic, question, answer) VALUES (?, ?, ?, ?)", QA)
    con.commit()
    con.close()
    print(f"wrote {len(QA)} questions to {DB}")


if __name__ == "__main__":
    main()
