//! `agt-normalize` CLI: read text from stdin, emit `{"text":..,"transforms":[..]}`
//! JSON on stdout. Lets the Python research harness drive the **Rust** normalizer
//! so the A/B measures the artifact that ships to AGT. Hand-rolled JSON keeps the
//! binary dependency-free (no serde), matching the crate's "no new deps" rule.

use std::io::Read;

use agt_normalize::normalize;

fn main() {
    let mut input = String::new();
    if std::io::stdin().read_to_string(&mut input).is_err() {
        eprintln!("agt-normalize: could not read stdin");
        std::process::exit(1);
    }
    let result = normalize(&input);
    let transforms: Vec<String> = result
        .transforms
        .iter()
        .map(|tr| format!("\"{tr:?}\""))
        .collect();
    println!(
        "{{\"text\":\"{}\",\"transforms\":[{}]}}",
        json_escape(&result.text),
        transforms.join(",")
    );
}

fn json_escape(s: &str) -> String {
    let mut out = String::with_capacity(s.len() + 2);
    for c in s.chars() {
        match c {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            c if (c as u32) < 0x20 => out.push_str(&format!("\\u{:04x}", c as u32)),
            c => out.push(c),
        }
    }
    out
}
