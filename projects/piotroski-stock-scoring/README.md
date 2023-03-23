# Turning a financial idea into rules

**How can a financial framework become an inspectable sequence of calculations?**

[Back to the portfolio](../../README.md) · [Browser project page](index.html)

![A typeset excerpt of a cash-flow rule and score increment from the original Python notebook.](../../assets/previews/scoring.jpg)

*Original cash-flow comparison code from the group notebook.*

## Substance

This group notebook translates a Piotroski-style financial scoring idea into Python. It gives an early example of turning a framework learned in economics and finance into explicit calculations that another reader can follow.

## Methods

yfinance retrieves company statements; pandas-style positional indexing extracts entries; ratios and comparisons contribute to an accumulated score. Markdown explanations sit beside the corresponding Python calculations.

## What the work brings out

The notebook places explanations of accounting concepts beside the exact conditions that increment the score. This is the part to inspect: the financial judgement has been decomposed into smaller rules, so disagreements can be traced to a definition, a data entry or a calculation.

## The connection

The interesting transition is from an informal judgement to a rule. Once that rule is written in code, its definitions, assumptions and implementation become visible and open to checking.

## Open the work

- [Financial-scoring notebook](piotroski-score.ipynb) · 29 cells · Python notebook

  [Read code and saved outputs in a browser](notebook.html).

<details>
<summary>Scope, interpretation and available material</summary>


This is a coursework implementation, not a validated canonical F-score or investment tool. Positional statement indexing is fragile; the notebook also reuses the same average-assets expression for both periods. Those implementation choices are preserved for inspection, not silently presented as verified finance logic. Live API execution has not been tested.


</details>

## Credit

Group work by Vaibhav, Hami and Abhinav, as credited in the first notebook cell.

## Connected work

[From a public webpage to a dataset](../public-distribution-scraping/) · [Rebuilding the evidence on water pricing](../replication-water-pricing/)
