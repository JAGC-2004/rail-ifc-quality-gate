# IFC4.3 notes for linear assets

IFC4.3 (IFC4X3) enhances infrastructure modeling with:
- richer alignment and linear referencing concepts,
- domain entities for rail and other linear assets,
- more explicit spatial relationships for corridor-like assets.

Implications for this pipeline:
- R3 anchor consistency can leverage alignment-based placement when available.
- R4 semantic degradation can be assessed against domain-native entities (reducing the need for proxies).
- Owner profiles may introduce domain-specific PSETs for handover in rail operations.

This repo includes schema-neutral fallbacks so it remains usable on IFC2x3 corpora,
while anticipating improvements for IFC4.3.
