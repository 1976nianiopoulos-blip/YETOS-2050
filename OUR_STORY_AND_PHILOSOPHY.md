# YETOS 2050 — The Land We Leave Behind

**The Land Alchemists | NASA Space Apps Challenge 2026 — Field Shift**  
**Same Rain. Different Soil. Different Futures.**

> **Two Generations. One Responsibility. The Land We Leave Behind.**

## A human question before a technical one

YETOS 2050 did not begin with a dashboard or an algorithm. It began with a question about responsibility: **What condition will the soil, water and agricultural land be in when the next generation inherits them?**

Our point of departure is Greece, and especially the region of Karditsa in Thessaly. The devastation caused by Storm Daniel in September 2023 sharpened our concern for rural communities, damaged land and the consequences of extreme weather. The event inspired our inquiry; it does not, by itself, establish the causes or mechanisms of damage on any particular field.

The Land Alchemists is a father–son initiative bringing together agricultural studies and spatial planning and development engineering. Two generations approach the same problem from different perspectives. Our ambition is not to make decisions on behalf of farmers, but to make evidence more intelligible, to expose assumptions, and to preserve the farmer's right to judge.

## Why the same rain is not the same outcome

Rainfall alone does not determine how an agricultural field responds. Soil texture and structure, prior moisture, drainage, ground cover, slope and land management all matter. The same meteorological input can produce different *modeled* water-storage and drainage outcomes when soil assumptions change.

We initially chose **Limerick, Ireland**, as a methodological study area because it offers relevant soil-survey literature and accessible gridded meteorological information. Limerick is not presented as equivalent to Karditsa. These are different places with different soils, landscapes and hazards. The purpose is to demonstrate a transparent approach that would require local measurements and independent validation before use on a real farm.

## Four philosophical inspirations — one responsibility

Our influences come from different traditions and must not be confused with one another or treated as scientific proof.

### Aristotle — purpose and responsible action

The Aristotelian ideas of *telos*, human flourishing and the movement from possibility to action inspire a basic question: **What is technology for?** We believe agricultural intelligence should serve the lasting well-being of people and the land, not merely optimize a number for one season. This is our contemporary interpretation, not a claim that Aristotle described a modern computational model.

### Masanobu Fukuoka — observe before intervening

Fukuoka's approach to natural farming asks us to pay attention to ecological processes and challenge unnecessary interventions. In YETOS 2050 that inspiration becomes a design principle: **show the conditions and the uncertainties before suggesting any action**. We do not confuse a model output with knowledge of an actual field.

### Erwin Schrödinger — the organization of living systems

In *What Is Life?* (1944), Schrödinger explored the physical organization of life and discussed negative entropy. His work encourages us to think about living systems as organized and vulnerable. It is a philosophical and scientific inspiration; **YETOS does not calculate “negentropy” of soil or claim to reverse the laws of thermodynamics**.

### Oromo Safuu and Gadaa — ethics, limits and accountability

Safuu is an Indigenous Oromo ethical tradition concerned with right conduct, mutual respect, relationships and limits. It is culturally connected with the Oromo Gadaa system, which UNESCO recognized in 2016. We acknowledge this tradition's Oromo origin and draw a respectful analogy: **the ability to influence a system carries an obligation of restraint and accountability**. Safuu is not a physical variable or an invention of our project; UNESCO's listing concerns Gadaa, not a separate inscription of Safuu.

## How ethics influenced what we built

For us, philosophy matters only if it changes practical decisions.

- **Evidence before recommendation.** Missing measurements are identified, not replaced with fabricated certainty.
- **Farmer in control.** Users can examine different priorities; the software must not invent one universally “best” decision.
- **Same inputs, transparent comparisons.** Differences in illustrative soils are explored under shared, documented weather inputs where applicable.
- **An explicit right to abstain.** If a comparison is not supported, the appropriate answer is *Unresolved* or *Evidence Required*, rather than an unsupported winner.
- **Responsibility across generations.** Decisions today should not diminish the ability of future generations to grow food on functioning soil with usable water.

The last point is not an output of a climate model. It is the reason we chose to build a decision-support tool with explicit scientific boundaries.

## PRE research and the competition BUILD

Before the official 14–15 November 2026 BUILD period, we had developed the research question, a documented evidence register, an MVP specification, candidate crop rotations and decision rules. This was **pre-competition research and design**, not a pre-existing competition application.

During the BUILD we developed a separate **Python/Streamlit prototype** and publicly documented its source code, provenance, tests and decisions. The current demonstration includes:

- **NASA POWER historical reference weather (2023)** for the Limerick study area.
- **Illustrative soil-water accounting**, comparing conditional responses rather than asserting measured field conditions.
- **S1:** hypothetical interruption of irrigation supply.
- **S2:** a synthetic extreme-rainfall input; the modeled unretained-water measure is a proxy, **not a validated flood or erosion forecast**.
- **S3:** a separate hypothetical two-month period with no rainfall.
- **Candidate rotation and farmer-priority comparisons**, without presenting an unsupported agronomic winner.
- A separate **NASA NEX-GDDP-CMIP6 Climate 2050 Lens** examining precipitation for **one simulated year** under **MPI-ESM1-2-HR / SSP2-4.5**; it is **not a weather forecast or evidence of a long-term climate trend**.
- **35 passing automated tests** at the documented development checkpoint.

The soil scenarios are illustrative, not field-calibrated. The project does not provide validated crop-yield, waterlogging injury, runoff, erosion or river-flood predictions, and it does not replace agronomic expertise. The historical 2023 NASA POWER series and the modeled 2050 NEX series are different sources and must not be compared as evidence of a climatic trend.

## The people, the tools and the pictures

The project's question, values, research direction, visual direction, scientific decisions and final judgment were led by the human team. We used AI assistance for literature discovery, critical review, writing, programming support, testing guidance and **AI-generated visual artwork**. Research tools included Perplexity, Consensus, Elicit, NotebookLM, Gemini and ChatGPT; DeepSeek was consulted briefly for exploratory critique, with errors identified, and was not accepted as independent scientific evidence or implemented code. AI assistance does not constitute a NASA partnership or independent scientific validation.

The **seven demonstration slides** contain AI-generated, symbolic imagery, not photographs of actual study plots or team members, and tablet screens are artistic illustrations rather than literal application screenshots. References within the illustrations to NASA missions such as SMAP or GRACE are conceptual only: the **data sources actually used in the current prototype are NASA POWER and NASA NEX-GDDP-CMIP6**. The slides are marked *AI GENERATED*.

This YETOS 2050 prototype is distinct from the founder's broader, pre-existing **Alchemist Negentropy Matrix** regenerative-agriculture vision. No private application or unreleased business system is presented as part of this competition BUILD.

## The land we leave behind

We cannot choose every storm, every drought, or the climate our children will face. We can choose whether to treat soil as expendable, whether to be transparent about the limits of our knowledge, and whether to leave room for the judgment of the people who live with the consequences.

**Science informs choices. Farmers decide. Future generations inherit the consequences.**

---

### Key sources and research context

- [YETOS 2050 — public source code and development evidence](https://github.com/1976nianiopoulos-blip/YETOS-2050)
- [NASA POWER](https://power.larc.nasa.gov/)
- [NASA NEX-GDDP-CMIP6](https://www.nccs.nasa.gov/data-collections/nex-gddp-cmip6/)
- Allen, Pereira, Raes & Smith, *FAO Irrigation and Drainage Paper 56* (1998): <https://www.fao.org/4/X0490E/X0490E00.htm>
- Masanobu Fukuoka, *The One-Straw Revolution* (1978)
- Erwin Schrödinger, *What Is Life?* (1944)
- Aristotle, *Nicomachean Ethics* and *Metaphysics* (philosophical inspiration)
- [UNESCO — Gadaa system of the Oromo](https://ich.unesco.org/en/RL/gadaa-system-an-indigenous-democratic-socio-political-system-of-the-oromo-people-01164)
- Dasta Alamayo (2021), *Safuu: The indigenous Oromo moral thought*, DOI: <https://doi.org/10.5897/JPC2019.0046>

**Public disclosure boundary:** This narrative intentionally contains no private health information, employment applications, possible appointments or private relocation and farm plans.
