# RepoPilot Team: Technical Report Writing Guide

**Applies to:** every technical report the team writes (workstream research reports, design proposals, experiment reports)
**Based on:** *A Guide to Technical Report Writing*, The Institution of Engineering and Technology (IET), hosted by IEEE IAS [1]. Citation style: IEEE numeric.
**Version:** 1.0, 14 October 2026

---

## Summary

Every report we write follows **one fixed structure** (Section 3) and **one set of rules** (Sections 4 to 8), so that the four reports can be read side by side and merged into the final capstone document without rewriting. The structure adapts the IET long-report format (Title page → Summary → Contents → Introduction → Procedure → Findings → Conclusions → Recommendations → References → Appendices) to our needs. It adds two mandatory parts the team needs: an **Inputs / Process / Outputs** section and an **Alternatives Considered** section. Using an AI assistant to draft is allowed, but the result must match this structure exactly and pass the checklist in Section 9. A ready-to-fill template is provided in `03_Technical_Report_Template.md`, and a prompt to give your AI assistant is in Appendix A.

---

## Contents

1. Purpose
2. The Ten Laws (IET)
3. Mandatory Report Structure
4. Headings and Numbering
5. Writing Style
6. Figures, Tables and Diagrams
7. References and Citations
8. Summary vs Abstract
9. Checking Before Submission (Checklist)
10. File Naming and Submission
11. References

Appendix A: Prompt for AI-Assisted Drafting
Appendix B: Common Mistakes, with Before/After Examples

---

## 1. Purpose

Four people research four different parts of RepoPilot. Without a shared format we end up with one slide-style summary, one essay, one bullet dump and one chat transcript, and none of them can be compared. This guide fixes the format so that:

- any team member can find the **inputs, process and outputs** of any workstream in the same place;
- reports can be pasted into the final capstone document with no restructuring;
- reviewers (supervisor, examiners) see consistent engineering-grade writing.

**Reader of these reports:** the other three team members first, then the supervisor. Assume the reader knows the RepoPilot idea but has **not** read your papers or your tool's documentation.

---

## 2. The Ten Laws (IET)

These come directly from the IET guide [1]. Everything else in this document applies them.

| # | Law | What it means for us |
|---|---|---|
| 1 | **The reader is the most important person.** | Write for a teammate who has not read your sources. Define every term once. |
| 2 | **Keep the report as short as possible.** | Main text should be 6–12 pages. Move raw logs, long tables and extra detail to appendices. |
| 3 | **Organise for the convenience of the report user.** | People read the Summary, then the Conclusions, then the section they care about. Every section must make sense on its own. |
| 4 | **All references should be correct in all details.** | Every paper, tool and number has a full citation. No invented references. |
| 5 | **The writing should be accurate, concise and unobtrusive.** | Plain words, short sentences, no filler, no hype. |
| 6 | **The right diagram with the right labels in the right place.** | Each figure sits next to the text that discusses it, is numbered, captioned and referred to in the text. |
| 7 | **Summaries give the whole picture, in miniature.** | Summary is at most 250 words, continuous prose, states the answer and recommendation. Written last. |
| 8 | **Check for technical errors, typing errors and inconsistency.** | Every number checked against its source. Same term for the same thing throughout. |
| 9 | **The report should look as good as it is.** | Consistent headings, spacing and formatting; nothing overflowing the page. |
| 10 | **The reader is the most important person.** | Repeated on purpose: it is the one law never to break. |

---

## 3. Mandatory Report Structure

Use these sections **in this order with these exact headings**. Sections marked *(optional)* may be removed. All others are required, even if short.

| # | Section | Content | Length guide |
|---|---|---|---|
| — | **Title Page** | Title (specific, not "Report 1"), author, workstream ID (WS1–WS4), report ID, version, date. **No summary on the title page.** | ½ page |
| — | **Summary** | The whole report in miniature: problem, approach chosen, key findings, recommendation. Prose, no lists or figures. | ≤ 250 words |
| — | **Table of Contents** | Numbered headings down to level 2 (level 3 if long). | auto |
| — | **List of Abbreviations** *(optional)* | Alphabetical. Use it if you have more than 5 abbreviations. | — |
| 1 | **Introduction** | 1.1 Objective (the question this report answers). 1.2 Scope (what is in and out). 1.3 Context within RepoPilot (which pipeline stage, which workstream). | ½–1 page |
| 2 | **Background** | Only the background the reader needs: relevant papers and concepts, each tied to our problem. Not a literature dump. | 1–2 pages |
| 3 | **Procedure / Method** | How you investigated: what you read, what you tried (spikes), on which sample app, what you measured. Enough for someone to repeat it. | ½–1 page |
| 4 | **Proposed Design** | The core of the report. **4.1 Inputs:** each input, its format and its source workstream. **4.2 Process:** step-by-step pipeline, tools, models and algorithms, with an architecture figure. **4.3 Outputs:** each artifact with a schema sketch and its consumer. **4.4 Context-window and cost considerations:** token budget, model, estimated cost per app. **4.5 Integration points:** which other workstreams you depend on and which depend on you. | 3–5 pages |
| 5 | **Findings / Results** | Evidence: spike results, measurements, tool comparisons, numbers from papers that support the design. Facts, not opinions. | 1–3 pages |
| 6 | **Alternatives Considered** | A comparison table of the options evaluated, with criteria and the reason each was chosen or rejected. | ½–1 page |
| 7 | **Risks and Open Questions** | What might not work, what is still unknown, what the team must decide together. | ½ page |
| 8 | **Conclusions** | What the findings mean. No new information. Each conclusion must follow from Sections 4–6. | ½ page |
| 9 | **Recommendations** | Numbered, actionable, each with an owner where possible ("R1: Use X for Y because Z"). | ½ page |
| 10 | **References** | IEEE numeric style, in order of first citation (Section 7). | — |
| A, B, … | **Appendices** | Raw data, long logs, full schemas, extra tables, prompt texts. Lettered: Appendix A, A.1, A.2, Appendix B… | as needed |

**Notes**

- The IET guide recommends writing the **Findings first** (they are the easiest), then the Proposed Design, then Introduction and Conclusions, and the **Summary last** [1].
- **Conclusions vs Recommendations:** conclusions say *what is true*; recommendations say *what we should do*. Do not mix them.
- **Inputs / Process / Outputs** (Section 4) is what the team meeting will check against the other workstreams. Make it precise.

---

## 4. Headings and Numbering

1. Use **decimal notation**, at most three levels in the main text (four only if unavoidable):
   ```
   4. PROPOSED DESIGN            ← level 1
   4.2 Process                   ← level 2
   4.2.3 Retrieval Fusion        ← level 3
   ```
2. A level-3 heading anywhere should be of similar importance to any other level-3 heading.
3. **Appendices** use letters: Appendix B, B.1, B.2.4.
4. Headings must be **specific**. "Results of Hybrid vs Dense Retrieval on Sample App 2" is better than "Results"; "Other considerations" is not allowed.
5. Start each level-1 section on a new page in the final PDF.
6. Do not number paragraphs.
7. Page numbers appear in the footer as "Page X of Y".

---

## 5. Writing Style

### 5.1 Accuracy

- **Say exactly what you mean.** Ambiguity in technical writing is dangerous ("not" vs "now" changes the meaning and the spell-checker will not catch it).
- **Numbers carry units and sources:** "54.15% exact match on TFix [3]", not "about 54%".
- **Separate what a paper reports from what we infer.** For example: "TestAgent reports 83.69% mutation score [4]. We expect lower on JS apps because…"
- **Be careful with commas:** "The tests, which failed, were re-run" means all of them failed and were re-run. "The tests which failed were re-run" means only the failing ones were re-run.

### 5.2 Brevity

- One idea per paragraph. Do not let a single paragraph fill a page.
- Vary sentence length; split any sentence longer than about 3 lines.
- Cut filler: "at this present moment in time" → "now"; "in order to" → "to"; "it is worth noting that" → (delete).
- Avoid vague words: *basically, quite, rather, fairly, very, in due course, robust, seamless, cutting-edge, leverage*.

### 5.3 Unobtrusive (formal but plain)

- Formal means: no contractions (*it is*, not *it's*), no slang, correct words. It does **not** mean pompous: use *use* not *utilise*, *send* not *dispatch*, *end* not *draw to a conclusion*.
- **Active voice is preferred**: "We recommend Qdrant", not "It is recommended that Qdrant be utilised".
- Use linking phrases to guide the reader: *however, as a result, on the other hand, for this reason*.
- **One term per concept, everywhere.** If you say "failure verdict", never switch to "failure label" or "classification result". Use the artifact names from the work plan exactly (`execution_result.json`, `failure_verdict.json`, …).
- Abbreviations: write the term in full at first use with the abbreviation in brackets, for example "Row-Level Security (RLS)". Add it to the abbreviation list.
- Write code identifiers, file names and commands in `monospace`.

---

## 6. Figures, Tables and Diagrams

1. **Position:** place each figure or table right after the paragraph that first refers to it. Put only supplementary material in appendices.
2. **Numbering by section:** Figure 4.2 is the second figure in Section 4. Tables use their own sequence: Table 4.1, Table 4.2.
3. **Every figure and table is referred to in the text** before it appears: "Figure 4.1 shows the retrieval pipeline."
4. **Captions:** figure captions go **below** the figure; table captions go **above** the table. Captions are brief and specific.
5. **Labels horizontal**, axes labelled with units, same scale when two graphs are compared.
6. **Do not rely on colour alone.** It must still read when printed in black and white; use patterns, labels or line styles as well.
7. **Choose the right form:** many exact numbers → table; comparing items → bar chart; trend → line graph; pipeline or architecture → block diagram.
8. **Tables:** units in the column header, numbers rounded to sensible precision, consistent decimal places, minimal rules (use spacing instead of a grid).
9. **Architecture diagrams** (required in Section 4.2): show inputs on the left/top, outputs on the right/bottom, and label every arrow with the artifact it carries.
10. Screenshots and exported images must be sharp; blurred numbers cause errors.
11. Before keeping a figure, ask: Does it give the required information? Is it accurate? Is it easy to use? Does it look tidy? [1]

---

## 7. References and Citations

**Style: IEEE numeric.** Cite in the text with square-bracket numbers in order of first appearance: "...hybrid retrieval [3], [5]–[7]." Reuse the same number every time the same source is cited.

**Formats:**

- **Journal:** [1] A. Author, B. Author, and C. Author, "Title of article," *Journal Name*, vol. X, no. Y, pp. ZZ–ZZ, Month Year, doi: …
- **Conference:** [2] W. Wang, Y. Wang, S. Joty, and S. C. H. Hoi, "RAP-Gen: Retrieval-augmented patch generation with CodeT5 for automatic program repair," in *Proc. ESEC/FSE*, 2023, pp. …
- **arXiv preprint:** [3] A. Author *et al.*, "Title," arXiv:2606.23130, 2026.
- **Software / documentation:** [4] Semgrep, "Writing rules," Semgrep Docs. [Online]. Available: https://semgrep.dev/docs/ (accessed Oct. 14, 2026).
- **Book:** [5] J. van Emden, *Writing for Engineers*, 3rd ed. Basingstoke, U.K.: Palgrave Macmillan, 2005.

**Rules:**

1. **Every reference must be real and checked.** Open the link or PDF and confirm the title, authors, year and venue. A fabricated or wrong reference is the most serious error in a report.
2. Online sources include the URL and the **date accessed**.
3. Cite the **original paper**, not a team summary, when you quote a number. If you only read the summary, say so ("as summarised in [6]").
4. Any figure or table copied or adapted from a paper must say so in its caption: "Adapted from [3, Fig. 2]."
5. Use a reference manager (Zotero or Mendeley) with the IEEE style to avoid formatting mistakes.

---

## 8. Summary vs Abstract

- **Summary (required):** for the busy reader, often the decision-maker, who may read nothing else. It gives the whole picture: problem, approach, main findings, **recommendation**. Prose only, at most 250 words, no citations or figures. Write it last. The IET guide notes that a first draft is usually about one third too long, so prune it [1].
- **Abstract:** a short description to help someone decide whether to read the report, often with keywords. We use an abstract only in the final capstone document and any paper submission, **not** in internal workstream reports.

---

## 9. Checking Before Submission (Checklist)

The IET guide says the ideal is two checkers: one technical, one careful non-expert. It also says to leave at least 48 hours between writing and checking if possible [1]. Before submitting, the author confirms **every** item:

**Structure**
- [ ] All mandatory sections present, in order, with the exact headings from Section 3.
- [ ] Section 4 has explicit **4.1 Inputs, 4.2 Process, 4.3 Outputs** with sources and consumers named.
- [ ] Summary ≤ 250 words, prose only, contains the recommendation.
- [ ] Conclusions contain no new information. Recommendations are numbered and actionable.

**Accuracy**
- [ ] Every number checked **digit by digit** against its source.
- [ ] Every reference opened and verified (title, authors, year, venue, URL).
- [ ] Paper claims and our own inferences are clearly separated.
- [ ] Artifact and tool names match the work plan exactly.

**Consistency**
- [ ] Same term for the same concept throughout.
- [ ] Abbreviations defined at first use and listed.
- [ ] Heading numbering continuous; figure and table numbers match their text references.

**Presentation**
- [ ] Every figure and table is numbered, captioned (figure below, table above) and referred to in the text.
- [ ] Figures readable in black and white; no overflowing tables or images.
- [ ] Page numbers "Page X of Y"; title page complete; no summary on the title page.
- [ ] Spell-check run, then a human read-through for wrong-but-real words (not/now, form/from).

**AI-assisted drafts (extra)**
- [ ] No invented references, tool features, API names or numbers. Each one was checked by a human.
- [ ] No generic filler paragraphs ("In today's rapidly evolving landscape…").
- [ ] Section 4 describes **our** design for **our** stack, not a generic tutorial.
- [ ] The author can explain and defend every sentence in the meeting.

---

## 10. File Naming and Submission

- **Source:** write in Markdown (or Word/Google Docs) using `03_Technical_Report_Template.md`.
- **Final:** export to PDF.
- **File name:** `RP-<WS>-<ShortTitle>-v<major>.<minor>.pdf`. Example: `RP-WS1-Repo-Ingestion-and-RAG-v1.0.pdf`.
- **Report ID on the title page** matches the file name without version: `RP-WS1-Repo-Ingestion-and-RAG`.
- **Version history:** v0.x = draft, v1.0 = submitted for the meeting, v1.x = revised after the meeting.
- **Figures:** keep the editable source (draw.io, Excalidraw, Mermaid) in the shared folder next to the PDF.

---

## 11. References

[1] The Institution of Engineering and Technology, *A Guide to Technical Report Writing*, J. van Emden and J. Easteal, rev. A. Kerr. London, U.K.: IET, 2015. [Online]. Available: https://ias.ieee.org/wp-content/uploads/2023/06/2020-01-16_IET_Technical_Report_Writing_Guidelines.pdf (accessed Oct. 14, 2026).
[2] IEEE, *IEEE Reference Guide*. Piscataway, NJ, USA: IEEE. [Online]. Available: https://journals.ieeeauthorcenter.ieee.org/ (accessed Oct. 14, 2026).
[3] M. Cutts, *Oxford Guide to Plain English*, 4th ed. Oxford, U.K.: Oxford Univ. Press, 2013.

---

## Appendix A: Prompt for AI-Assisted Drafting

If you draft with an AI assistant, give it this prompt **together with** `03_Technical_Report_Template.md`, this guide, and your own notes and sources. Then run the Section 9 checklist yourself; the assistant does not replace it.

```text
You are helping me write an internal technical report for our capstone project RepoPilot
(an evidence-driven multi-agent framework for automated QA and repair of AI-generated
React/Vite + Supabase + Stripe repositories).

Follow the attached template EXACTLY:
- Keep every heading, its number and its order. Do not add, rename or remove level-1 sections.
- Section 4 must contain 4.1 Inputs, 4.2 Process, 4.3 Outputs, 4.4 Context-window and cost,
  4.5 Integration points, using the artifact names from our work plan exactly.
- Summary: max 250 words, continuous prose, no citations, includes the recommendation.
- Style: formal but plain English, active voice, short sentences, no filler or marketing words,
  no contractions. Same term for the same concept throughout.
- Citations: IEEE numeric [n] in order of first use. Use ONLY the sources I give you.
  If a claim needs a source I did not give, write [CITATION NEEDED] instead of inventing one.
- Never invent numbers, tool features, APIs or results. If something is unknown, write
  [TO VERIFY] so I can check it.
- Figures/tables: number by section (Figure 4.1, Table 5.2), caption figures below and tables
  above, and refer to each one in the text before it appears. For diagrams, give Mermaid code.
- Conclusions contain no new information; Recommendations are numbered (R1, R2, ...) and actionable.

My workstream: <WS id and title>
My notes, findings and sources:
<paste here>
```

After drafting, search the document for `[CITATION NEEDED]` and `[TO VERIFY]` and resolve every one before submitting.

---

## Appendix B: Common Mistakes, with Before/After Examples

| Mistake | Before | After |
|---|---|---|
| Vague, filler-heavy | "Basically, RAG is a quite powerful approach that can leverage embeddings in a seamless way." | "Dense retrieval finds code by meaning; BM25 finds exact identifiers. We fuse both (Section 4.2.3)." |
| Number without unit or source | "Hybrid retrieval was better by a lot." | "Hybrid retrieval reached 54.15% exact match vs 53.93% for dense only [3]." |
| Passive and wordy | "It was decided by the author that Vitest would be utilised." | "We chose Vitest because it runs natively in Vite projects." |
| Mixing paper claims with ours | "TestAgent gets 83% mutation score so our tests will too." | "TestAgent reports 83.69% on Java projects [4]. Our JS result is untested; we will measure it with StrykerJS." |
| Conclusion with new info | "In conclusion, we also tried LanceDB, which was fast." | Move the LanceDB result to Findings; the conclusion only interprets it. |
| Unspecific heading | "4.3 Other Stuff" | "4.3 Outputs: `risk_map.json` and `test_plan.json`" |
| Inconsistent terms | "verdict" … "label" … "classification" | "verdict" everywhere |
| Undefined abbreviation | "We check RLS and SARIF." | "We check Row-Level Security (RLS) and export Static Analysis Results Interchange Format (SARIF)." |
