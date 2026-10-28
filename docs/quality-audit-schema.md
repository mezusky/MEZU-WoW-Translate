# Cross-page quality evidence (v1)

The stop gate in `scripts/quality_trend.py` reads `qualitySample` from compact
`audits/*.json` reports. Existing source-only reports remain valid but cannot
count as clean browser cycles. Do not mirror copyrighted guide text.

For a browser-rendered cycle, record `cycleId`, ISO `auditedAt`,
`newPagesAudited`, `novelIssueFamilies`, `browserVerifiedPages`,
`auditMethod: "browser-rendered"`, `crossRoleVerified: true`,
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
  "heldout": true,
  "browserRendered": true,
  "strictPass": true
}
```

The gate requires at least five **distinct** browser-verified Wowhead pages,
three classes and specs, all three roles (tank, healer, dps), two sections,
and two unrelated heldouts. Every case must pass its strict audit. The rate
of novel issue families per new page must be at most 5%, and two consecutive
clean cycles are required. Missing evidence is **unknown**, never zero.

A browser case must reflect the actual translated rendered page, including
entity names, Translator API fallback, preserved links/widgets, and DOM
reconstruction. Indexed English source snippets, source-side locale mixtures,
and server-side translation approximations cannot establish these results.
The gate is locale-independent: record `sourceLanguage` and `targetLanguage`
separately in the audit report; never assume English/French in the engine.
