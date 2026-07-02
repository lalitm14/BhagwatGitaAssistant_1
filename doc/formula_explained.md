# Hybrid Retrieval Scoring System for Theological Search

This equation models a **hybrid retrieval scoring system**, specifically tailored for a theological or scripture-based search engine. Instead of relying purely on semantic meaning (cosine similarity), it injects domain-specific knowledge (key concepts, authoritative verses) and quality control (penalties).

Here is a detailed, component-by-component breakdown of every mathematical notation.

---

## 1. The Dependent Variable: \( S_{final} \)

- **\( S_${final}$ \)** : The final ranking score assigned to a given `(query, document)` pair. The search engine sorts all retrieved passages by this score in descending order. It is an additive composite of four distinct signals.

---

## 2. The Baseline: \( S_{cos} \)

- **\( S_{cos} \)** : The raw **cosine similarity** score.

- **How it works**: The query is converted into a numerical vector \( \vec{q} \) and the document (passage) into \( \vec{d} \) using a dense embedding model (e.g., Sentence-BERT). \( S_{cos} \) measures the cosine of the angle between these two vectors, ranging from \(-1\) to \(1\) (or \(0\) to \(1\) if normalized).

- **Role**: It captures the **semantic gist**—passages that talk about the same topic as the query, even if they use completely different words, get a high baseline score.

---

## 3. The Concept Bonus: \( \sum_{c=1}^{C} \alpha_c(q, d) \)

- **\( c \)** : The index variable representing a specific theological concept (e.g., "covenant", "grace", "eschatology", "atonement").

- **\( C \)** : The total number of distinct theological concepts the system is programmed to recognize.

- **\( \alpha_c(q, d) \)** : A **concept-bonus function** for concept \( c \). It is a dynamic, query-dependent function that calculates the **lexical overlap** of domain-specific terms.

  - **How it works**: If the query \( q \) contains strong indicators of concept \( c \) (e.g., the word "forgiveness") and the document \( d \) contains exact keyword matches or known synonyms for that concept (e.g., "pardon", "remit"), this function returns a positive numerical bonus.

  - **Why it's a function of both \( q \) and \( d \)**: The bonus only triggers if *both* the query and the document discuss the same concept. If the query mentions it but the document doesn't, \( \alpha_c \) returns \( 0 \) (or a negative value).

---

## 4. The Authority Boost: \( \sum_{v=1}^{V} \beta_v \cdot \mathbf{1}_{v \in d} \)

This term is a static, rule-based boost for universally recognized "pivotal" verses.

- **\( v \)** : The index variable representing a specific, pre-identified pivotal verse (e.g., John 3:16, Quran 2:255, or a specific Bhagavad Gita verse).

- **\( V \)** : The total number of these "golden" verses stored in the authority lookup table.

- **\( \beta_v \)** : A **static, high-magnitude weight** (authority boost) assigned exclusively to verse \( v \). Crucially, this value is **fixed**—it does not change based on the query. The examples given are:

  - \( \beta_{18.66} = 0.35 \) (Verse identified as 18.66 gets a \( 0.35 \) boost).
  - \( \beta_{13.23} = 1.00 \) (Verse 13.23 gets a massive \( 1.00 \) boost—this is treated as the highest authoritative text in the corpus).

- **\( \mathbf{1}_{v \in d} \)** : This is the **Indicator Function** (also called the characteristic function).

  - It evaluates to \( 1 \) if the specific verse \( v \) is contained within the retrieved document/passage \( d \).
  - It evaluates to \( 0 \) if the verse is *not* in \( d \).

- **Combined effect**: Because of the multiplication \( \beta_v \cdot \mathbf{1}_{v \in d} \), the system automatically adds \( \beta_v \) to the score *only* when a retrieved passage happens to be one of these authoritative verses. This guarantees that the most important scriptures always appear at the top, regardless of how poorly their wording matches the user's query.

---

## 5. The Contextual Penalty: \( \gamma(q, d) \)

- **\( \gamma(q, d) \)** : A **contextual penalty function** that subtracts a value from the total score based on undesirable textual features.

- **Triggers**: It evaluates both the query and the document to check for:

  - **Question-markers**: If the passage is phrased as a rhetorical question rather than a declarative theological statement.
  - **Malformed OCR text**: If the passage contains garbled characters, broken Unicode, or formatting errors from the digitization process (e.g., "w1th", "G0d").
  - **Theologically negative examples**: If the passage is explicitly describing a sin, heresy, or a cautionary tale (e.g., "Judas betrayed him") rather than a prescriptive doctrine, the system penalizes it to avoid surfacing negative context when the user likely wants positive or neutral doctrine.

---

## 6. Why Additive ( \( + \) and \( - \) ) instead of Multiplicative ( \( \times \) )?

The text explicitly notes this is a **deliberate design choice**.

- If the equation were multiplicative (e.g., \( S_{cos} \times \text{Authority} \times \text{Concept} \)), then if the raw cosine similarity \( S_{cos} \) happened to be \( 0 \) (orthogonal vectors) or a very small number due to an embedding anomaly, the entire final score would collapse to **zero**—completely nullifying the Authority Boost (\( \beta \)).

- By using **addition**, the system ensures **robustness**. Even if the semantic embedding fails completely (\( S_{cos} = 0 \)), the Authority Boost term (\( \sum \beta \)) will still carry the most pivotal verse to the top of the search results, ensuring the system is fail-safe for critical religious texts.