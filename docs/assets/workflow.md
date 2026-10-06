# ExperimentGuard workflow image

Asset: [workflow.png](workflow.png). Generated with the built-in OpenAI image-generation tool on 6 October 2026 and reviewed against the project source. Style: modern light theme, warm white background, navy text and teal accents. This is an architecture illustration, not a screenshot or measured result chart.

## Meaning and source

The README supplies the accessible text summary and links to the owning technical/data/protocol documents. Model metrics remain sourced from the saved analytical artifacts. The diagram does not certify deployment or operational impact.

## Generation prompt

```text
Use case: infographic-diagram. Asset type: a GitHub README workflow image. Wide landscape 2:1, at least 1600 pixels wide. Modern light theme: warm white background, navy text, restrained teal accents, flat rounded cards, thin clean arrowheads, original small line icons, generous whitespace. No dark panels, gradients, logos, watermarks or fake screenshots. Large readable typography at a 900-pixel display width. Use EXACT labels given below. Explain implemented source architecture; do not invent metrics, successful deployment, automatic retraining or measured commercial impact.
Exact title: "ExperimentGuard". Exact subtitle: "From a frozen protocol to an evidence-based A/B decision".
Main workflow with large clear cards:
"Freeze protocol" -> "Validate assigned users" -> diamond "Integrity checks pass?".
The diamond YES branch leads to "Effect + confidence interval" -> "Protocol decision" -> "Report + figures".
The diamond NO branch leads down to a distinct amber card "Block outcome decision".
A small supporting card "Prospective power plan" connects to "Freeze protocol", not to the final decision.
Below the validation card a short note says "Retain zero-round users".
Footer: "Retrospective public dataset" and "Negative and inconclusive results are valid".
Constraints: no predictive model, API, deployment or invented result. The diagram must make the integrity blocking path unambiguous; no arrow from the blocked card to effect estimation or the success report path. Put YES and NO labels beside the corresponding arrows.
```
