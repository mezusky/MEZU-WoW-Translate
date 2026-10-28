# Cross-page quality evidence (v1)

The stop gate in `scripts/quality_trend.py` reads `qualitySample` from compact
`audits/*.json` reports. Existing source-only reports remain valid but cannot
count as clean browser cycles. Do not mirror copyrighted guide text.

For a browser-rendered cycle, record `cycleId`, ISO `auditedAt`,
`newPagesAudited`, `novelIssueFamilies`, `browserVerifiedPages`,
`auditMethod: "browser-rendered"`, `sourceLanguage: "en"`,
`targetLanguage: "fr"`, `crossRoleVerified: true`,
`unrelatedHeldoutsVerified: true`, and `strictAuditPassed: true` **only
when directly verified**. Include a `browserCases` array with one object per
new page, for example:

```json
{
  "url": "https://www.wowhead.com/guide/classes/warrior/protection/rotation-cooldowns-pve-tank",
  "wowClass": "warrior",
  "spec": "protection",
  "role": "tank",
  "section": "rotation",
  "sourceLanguage": "en",
  "targetLanguage": "fr",
  "heldout": true,
  "browserRendered": true,
  "strictPass": true
}
```

The gate requires at least five **distinct** browser-verified Wowhead pages,
three classes and specs, all three roles (tank, healer, dps), two sections,
and two unrelated heldouts. Every case must pass its strict audit. The rate
of novel issue families per new page must be at most 5%, and two consecutive
clean cycles are required. Those cycles must use the **same source/target
language pair**, have different offset-aware audit timestamps, and contain
**disjoint sets of newly verified page URLs**. Rechecking the same five pages
cannot establish generalization or satisfy the stop condition. Missing evidence is **unknown**, never zero.

A browser case must reflect the actual translated rendered page, including
entity names, Translator API fallback, preserved links/widgets, and DOM
reconstruction. Indexed English source snippets, source-side locale mixtures,
and server-side translation approximations cannot establish these results.
The gate is locale-independent: record `sourceLanguage` and `targetLanguage`
on each quality sample **and** browser case. They must be valid language tags,
match within the cycle, and differ (same-language pages require no translation).
Never infer source prose language from a Wowhead URL locale: `/fr/` pages can
contain English prose alongside French spell names. Language detection and
canonical entity localization are separate concerns. The current audit target
is English-source to French-target, but the evidence schema is multilingual.
