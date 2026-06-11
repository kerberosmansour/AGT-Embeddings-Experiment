//! REFERENCE SKELETON for the upstream AGT contribution
//! (RFC: "Strengthen and surface content normalization as a shared pre-detection
//! control"). This is NOT a drop-in — it sketches the proposed public API so
//! maintainers have something concrete to react to before any PR. Heavy
//! transform bodies are stubbed and reference the measured Python implementation
//! (https://github.com/kerberosmansour/AGT-Embeddings-Experiment →
//! meta/harness/round6-cascade/normalize.py).
//!
//! Proposed location: agent-governance-rust/agentmesh/src/normalize.rs
//! Intent: promote the existing private `normalize_for_detection` into a public,
//! configurable module that (a) adds FP-guarded de-obfuscation transforms and
//! (b) RETURNS WHAT IT CHANGED, so the detector, policy annotators, IFC, and
//! audit can all consume the canonical text and the transform record.

use std::collections::BTreeSet;

/// Closed set of transforms a normalization pass may apply. Surfaced to callers
/// so every control (and audit) can see what was un-disguised — never a
/// free-form string (keeps the audit surface a fixed, reviewable vocabulary).
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum Transform {
    WidthFold,          // fullwidth -> ASCII   (AGT already does this)
    StripInvisible,     // zero-width + BIDI override/isolate (Trojan Source) (AGT already does this)
    Lowercase,          // (AGT already does this)
    WhitespaceCollapse, // (AGT already does this)
    Confusables,        // homoglyph fold: Cyrillic/Greek look-alikes -> Latin  (NEW)
    Leet,               // `1gn0r3` -> `ignore`, token-guarded                  (NEW)
    SpacingCollapse,    // `i.g.n.o.r.e` / `i g n o r e`, run-length-guarded     (NEW)
    Rot13,              // actual decode, not just the literal "rot13"          (NEW)
    Base64,             // (AGT decodes this inside detection; here it's surfaced)
    Hex,                // (NEW)
    Percent,            // %69%67%6e... URL-encoding                            (NEW)
    UnicodeEscape,      // \uXXXX / \xNN  (AGT decodes \-escapes in detection)
    HtmlEntity,         // &#105; / &#x69; / &amp;                              (NEW)
    DecodeRejected,     // a decode was attempted but failed the acceptance guard
    DecodeDepthCapped,  // nesting beyond max_decode_depth
    OutputCapped,       // expansion beyond max_output_ratio
}

/// Result of a normalization pass: the canonical text plus which transforms fired.
#[derive(Debug, Clone)]
pub struct Normalized {
    pub text: String,
    pub transforms: BTreeSet<Transform>,
}

/// Knobs, all defaulted to the values measured FP-safe on the research corpus.
#[derive(Debug, Clone)]
pub struct NormalizeConfig {
    /// Max nested decode layers (base64(percent(text)) = depth 2). Default 2.
    pub max_decode_depth: u8,
    /// Reject a decode that expands output beyond this ratio. Default 4.
    pub max_output_ratio: u8,
    /// A decode is accepted only if the result is >= this fraction printable
    /// UTF-8. Default 0.90. The single most important FP guard.
    pub printable_min_ratio: f32,
    /// Toggle the decode layers independently of the char-level transforms.
    pub enable_decoders: bool,
}

impl Default for NormalizeConfig {
    fn default() -> Self {
        Self { max_decode_depth: 2, max_output_ratio: 4, printable_min_ratio: 0.90, enable_decoders: true }
    }
}

/// Public entry point. Contract:
///   * deterministic and idempotent: `normalize(&normalize(x).text).text == normalize(x).text`
///   * benign-safe: aggressive transforms fire only under their guards, so
///     legitimate inputs (percentages, `&amp;`, legit base64, code, structured
///     data) pass through unchanged (the part to scrutinize in review).
pub fn normalize(text: &str, cfg: &NormalizeConfig) -> Normalized {
    let mut t = BTreeSet::new();
    // 1. char-level canonicalization (existing AGT behaviour, kept):
    //    width fold -> strip invisible (incl. BIDI override/isolate) -> lowercase
    //    -> collapse whitespace. Record WidthFold/StripInvisible/Lowercase/WhitespaceCollapse.
    // 2. confusable fold (Confusables) — only unambiguous homoglyph map.
    // 3. spacing/separator collapse (SpacingCollapse) — run-length >= 4 guard.
    // 4. leet de-substitution (Leet) — token guard: >=2 alpha in token.
    // 5. decode layers up to cfg.max_decode_depth, each via `try_decode_once`,
    //    each gated by `accept_decode`. Tag the scheme or DecodeRejected/Capped.
    // 6. enforce cfg.max_output_ratio (OutputCapped).
    // Bodies omitted in this skeleton — see the Python reference for the exact,
    // measured logic and the guards.
    let _ = (text, cfg, &mut t);
    Normalized { text: text.to_string(), transforms: t }
}

/// The acceptance guard that makes decoding benign-safe. A decode is kept only if
/// it is valid UTF-8, >= printable_min_ratio printable, and (for length-preserving
/// schemes like rot13) increases a generic English-marker signal that is NOT
/// derived from attack labels. This is what prevents mangling `50% off`, `Tom &
/// Jerry`, legitimate base64 payloads, etc.
fn accept_decode(_original: &str, _decoded: &str, _cfg: &NormalizeConfig) -> bool {
    // stub — see normalize.py::_try_decode_once / _printable_ratio / _english_score
    unimplemented!("see Python reference for the measured acceptance guard")
}

#[cfg(test)]
mod tests {
    // The benign-safety + idempotency suite is the contract that matters.
    // These names mirror the Python test suite that measured 0 benign-control FP.

    // #[test] fn benign_percentage_unchanged()      { /* "50% off" stays "50% off" */ }
    // #[test] fn benign_ampersand_unchanged()       { /* "Tom &amp; Jerry" not over-decoded */ }
    // #[test] fn benign_high_entropy_not_decoded()  { /* random blob fails printable guard */ }
    // #[test] fn leet_decodes_under_guard()         { /* "1gn0r3 4ll" -> "ignore all" */ }
    // #[test] fn confusables_fold()                 { /* Cyrillic 'о' -> 'o' */ }
    // #[test] fn bidi_override_stripped()           { /* U+202E / isolates removed (Trojan Source) */ }
    // #[test] fn rot13_decoded_not_just_referenced(){ /* actual decode, vs current reference-match */ }
    // #[test] fn idempotent()                       { /* normalize(normalize(x)) == normalize(x) */ }
    // #[test] fn deterministic()                    { /* two runs identical */ }
}
