use crate::Finding;
use std::{fs, path::Path};
use walkdir::WalkDir;

const CACHE_WEIGHT: f64 = 5.0;
const TEXT_EXTENSIONS: &[&str] = &[
    "html", "htm", "jsx", "tsx", "vue", "svelte", "astro", "md", "mdx", "js", "ts", "json", "yaml",
    "yml", "toml", "conf",
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

fn cache_evidence(files: &[(String, String)]) -> Vec<String> {
    files
        .iter()
        .filter_map(|(path, text)| {
            let lower = text.to_ascii_lowercase();
            let explicit_immutable = lower.contains("immutable")
                && (lower.contains("max-age=31536000") || lower.contains("s-maxage=31536000"));
            let framework_fingerprint = lower.contains("/_next/static/");
            (explicit_immutable || framework_fingerprint).then_some(path.clone())
        })
        .collect()
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

    let evidence = cache_evidence(&files);
    let passed = !evidence.is_empty();
    Finding {
        rule_id: "WEB-007".to_string(),
        category: "Web Assets".to_string(),
        title: "Image assets have immutable cache strategy evidence".to_string(),
        status: if passed { "PASS" } else { "FAIL" },
        score: if passed { CACHE_WEIGHT } else { 0.0 },
        weight: CACHE_WEIGHT,
        evidence: if passed {
            evidence
                .into_iter()
                .take(12)
                .map(|path| format!("cache_evidence={path}"))
                .collect()
        } else {
            vec!["no long-lived immutable cache or framework fingerprint evidence detected".to_string()]
        },
        remediation: "Use long-lived immutable caching for versioned image assets or a framework/build pipeline with fingerprinted immutable asset URLs.".to_string(),
    }
}

#[cfg(test)]
mod tests {
    use super::{cache_evidence, has_image_usage};

    #[test]
    fn requires_image_usage_for_applicability() {
        let files = vec![(
            "config.js".to_string(),
            "max-age=31536000, immutable".to_string(),
        )];
        assert!(!has_image_usage(&files));
    }

    #[test]
    fn detects_explicit_immutable_cache_policy() {
        let files = vec![(
            "next.config.js".to_string(),
            "Cache-Control: public, max-age=31536000, immutable".to_string(),
        )];
        assert_eq!(cache_evidence(&files), vec!["next.config.js"]);
    }

    #[test]
    fn rejects_short_lived_cache_policy() {
        let files = vec![(
            "nginx.conf".to_string(),
            "Cache-Control: public, max-age=60".to_string(),
        )];
        assert!(cache_evidence(&files).is_empty());
    }
}
