use crate::Finding;
use std::{fs, path::Path};
use walkdir::WalkDir;

const CACHE_WEIGHT: f64 = 5.0;
const TEXT_EXTENSIONS: &[&str] = &[
    "html", "htm", "jsx", "tsx", "vue", "svelte", "astro", "md", "mdx", "js", "ts",
    "json", "yaml", "yml", "toml", "conf",
];

fn candidate_files(root: &Path) -> Vec<(String, String)> {
    WalkDir::new(root)
        .into_iter()
        .filter_entry(|entry| {
            let name = entry.file_name().to_string_lossy();
            name != ".git" && name != "target" && name != "node_modules" && name != "vendor"
        })
        .filter_map(Result::ok)
        .filter(|entry| entry.file_type().is_file())
        .filter_map(|entry| {
            let path = entry.path();
            let extension = path.extension()?.to_str()?.to_ascii_lowercase();
            if !TEXT_EXTENSIONS.contains(&extension.as_str()) {
                return None;
            }
            let text = fs::read_to_string(path).ok()?;
            let relative = path.strip_prefix(root).ok()?.display().to_string();
            Some((relative, text))
        })
        .collect()
}

fn has_image_usage(files: &[(String, String)]) -> bool {
    files.iter().any(|(_, text)| {
        let lower = text.to_ascii_lowercase();
        lower.contains("<img") || lower.contains("<image") || lower.contains("![")
    })
}

fn immutable_header_evidence(files: &[(String, String)]) -> Vec<String> {
    files
        .iter()
        .filter_map(|(path, text)| {
            let lower = text.to_ascii_lowercase();
            (lower.contains("cache-control")
                && lower.contains("immutable")
                && (lower.contains("max-age") || lower.contains("s-maxage")))
            .then_some(path.clone())
        })
        .collect()
}

fn versioned_asset_evidence(files: &[(String, String)]) -> Vec<String> {
    files
        .iter()
        .filter_map(|(path, text)| {
            let lower = text.to_ascii_lowercase();
            let query_versioned = ["?v=", "?ver=", "?version="].iter().any(|needle| {
                lower.contains(needle)
                    && [".png", ".jpg", ".jpeg", ".gif", ".webp", ".avif", ".svg"]
                        .iter()
                        .any(|ext| lower.contains(ext))
            });
            let framework_fingerprinted = lower.contains("/_next/static/")
                || lower.contains("/assets/") && contains_hash_like_token(&lower);
            (query_versioned || framework_fingerprinted).then_some(path.clone())
        })
        .collect()
}

fn contains_hash_like_token(text: &str) -> bool {
    text.split(|c: char| !c.is_ascii_alphanumeric())
        .any(|token| token.len() >= 8 && token.chars().all(|c| c.is_ascii_hexdigit()))
}

pub(crate) fn finding(root: &Path) -> Finding {
    let files = candidate_files(root);
    if !has_image_usage(&files) {
        return Finding {
            rule_id: "WEB-007".to_string(),
            category: "Web Assets".to_string(),
            title: "Image assets have immutable cache strategy evidence".to_string(),
            status: "SKIP",
            score: 0.0,
            weight: 0.0,
            evidence: vec!["no image usage detected".to_string()],
            remediation: String::new(),
        };
    }

    let immutable = immutable_header_evidence(&files);
    let versioned = versioned_asset_evidence(&files);
    let passed = !immutable.is_empty() || !versioned.is_empty();
    let mut evidence = Vec::new();
    evidence.extend(
        immutable
            .iter()
            .take(12)
            .map(|path| format!("immutable_cache_policy={path}")),
    );
    evidence.extend(
        versioned
            .iter()
            .take(12)
            .map(|path| format!("versioned_asset_reference={path}")),
    );
    if evidence.is_empty() {
        evidence.push("no immutable cache policy or versioned asset reference detected".to_string());
    }

    Finding {
        rule_id: "WEB-007".to_string(),
        category: "Web Assets".to_string(),
        title: "Image assets have immutable cache strategy evidence".to_string(),
        status: if passed { "PASS" } else { "FAIL" },
        score: if passed { CACHE_WEIGHT } else { 0.0 },
        weight: CACHE_WEIGHT,
        evidence,
        remediation: "Use explicit immutable long-lived cache policy for versioned image assets, or serve image URLs with stable content versioning/fingerprints.".to_string(),
    }
}

#[cfg(test)]
mod tests {
    use super::{contains_hash_like_token, immutable_header_evidence, versioned_asset_evidence};

    #[test]
    fn detects_immutable_cache_header_policy() {
        let files = vec![(
            "next.config.js".to_string(),
            "Cache-Control: public, max-age=31536000, immutable".to_string(),
        )];
        assert_eq!(immutable_header_evidence(&files), vec!["next.config.js"]);
    }

    #[test]
    fn detects_versioned_image_reference() {
        let files = vec![(
            "page.tsx".to_string(),
            "<img src=\"/logo.webp?v=20260827\" />".to_string(),
        )];
        assert_eq!(versioned_asset_evidence(&files), vec!["page.tsx"]);
    }

    #[test]
    fn detects_hex_fingerprint_token() {
        assert!(contains_hash_like_token("/assets/logo.a1b2c3d4.webp"));
        assert!(!contains_hash_like_token("/assets/logo.production.webp"));
    }
}
