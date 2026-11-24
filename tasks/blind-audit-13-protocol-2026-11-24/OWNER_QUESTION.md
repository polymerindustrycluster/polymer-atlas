# Owner ruling requested before sampling

**After the repairs, should the controller run the smoke test alone or authorize a full audit if the smoke passes?**

- **A · Smoke only (recommended).** Read up to 40 random PIC-18 records. Stop on the third record with a confirmed error or unresolved claim. Estimate 4.15M input tokens (OpenAI 1.69M, Google 1.92M, Anthropic 0.54M). Review the unresolved causes, plant detection and measured provider costs before authorizing a draw. Even a clean smoke leaves publication undecided.
- **B · Authorize both stages conditionally.** Use the same smoke, spend and plant gates. If they pass, draw up to 265 fresh PIC-18 records and 131 records in each of the other five strata. One independent reader checks each record; a different family reads flags and a random 15% of the rest. The third adverse record in any stratum ends the audit. Passing all six strata supports P1 exit. Estimated combined spend is 83.83M input tokens (OpenAI 37.43M, Google 39.85M, Anthropic 6.54M), versus about 450M for audit 12. Under the stressed detection model, a stratum at its error limit passes about 2.5% of the time. Even with perfect readers and only 2% of PIC-18 records wrong, PIC-18 passes just 9.9% of draws.
- **C · Defer.** Spend zero reader tokens now. Keep P1 open pending further repairs or a revised decision rule.
