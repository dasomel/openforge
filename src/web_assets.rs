use crate::Finding;
use std::{fs, path::Path};
use walkdir::WalkDir;

const SOURCE_EXTENSIONS: &[&str] = &[
    "html", "htm", "jsx", "tsx", "vue", "svelte", "astro", "md", "mdx", "js", "ts",
];

fn source_files(root: &Path) -> Vec<(String, String)> {
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
            if !SOURCE_EXTENSIONS.contains(&extension.as_str()) {
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
        lower.contains("<img")
            || lower.contains("<image")
            || lower.contains("![")
            || lower.contains("next/image")
    })
}

fn evidence_for(files: &[(String, String)], needles: &[&str]) -> Vec<String> {
    files
        .iter()
        .filter_map(|(path, text)| {
            let lower = text.to_ascii_lowercase();
            needles
                .iter()
                .any(|needle| lower.contains(&needle.to_ascii_lowercase()))
                .then_some(path.clone())
        })
        .collect()
}

fn finding(
    id: &str,
    title: &str,
    weight: f64,
    passed: bool,
    evidence: Vec<String>,
    remediation: &str,
) -> Finding {
    Finding {
        rule_id: id.to_string(),
        category: "Web Assets".to_string(),
        title: title.to_string(),
        status: if passed { "PASS" } else { "FAIL" },
        score: if passed { weight } else { 0.0 },
        weight,
        evidence,
        remediation: remediation.to_string(),
    }
}

fn skipped(id: &str, title: &str, reason: &str) -> Finding {
    Finding {
        rule_id: id.to_string(),
        category: "Web Assets".to_string(),
        title: title.to_string(),
        status: "SKIP",
        score: 0.0,
        weight: 0.0,
        evidence: vec![reason.to_string()],
        remediation: String::new(),
    }
}

pub(crate) fn findings(root: &Path) -> Vec<Finding> {
    let files = source_files(root);
    if !has_image_usage(&files) {
        return vec![
            skipped(
                "WEB-001",
                "Images use lazy loading",
                "no image usage detected",
            ),
            skipped(
                "WEB-002",
                "Images declare dimensions",
                "no image usage detected",
            ),
            skipped(
                "WEB-003",
                "Responsive image strategy is present",
                "no image usage detected",
            ),
            skipped(
                "WEB-004",
                "Modern image formats are referenced",
                "no image usage detected",
            ),
            skipped(
                "WEB-005",
                "Image optimization or CDN path is present",
                "no image usage detected",
            ),
            skipped(
                "WEB-006",
                "External image origins are constrained",
                "no image usage detected",
            ),
        ];
    }

    let lazy = evidence_for(
        &files,
        &["loading=\"lazy\"", "loading='lazy'", "loading={\"lazy\"}"],
    );
    let dimensions = evidence_for(&files, &[" width=", " width={", " height=", " height={"]);
    let responsive = evidence_for(&files, &["srcset=", "sizes=", "<picture", "next/image"]);
    let modern = evidence_for(
        &files,
        &[
            ".webp",
            ".avif",
            "output=webp",
            "output=avif",
            "format=webp",
            "format=avif",
        ],
    );
    let optimization = evidence_for(
        &files,
        &[
            "wsrv.nl",
            "weserv",
            "imagekit.io",
            "cloudinary",
            "imgix",
            "/_next/image",
            "next/image",
            "cdn-cgi/image",
        ],
    );
    let constrained = evidence_for(
        &files,
        &[
            "remotePatterns",
            "images.domains",
            "allowedOrigins",
            "allowed_origins",
            "origin allow",
            "origin_allow",
        ],
    );

    vec![
        finding(
            "WEB-001",
            "Images use lazy loading",
            4.0,
            !lazy.is_empty(),
            lazy,
            "Use native lazy loading or framework-equivalent deferred loading for non-critical images.",
        ),
        finding(
            "WEB-002",
            "Images declare dimensions",
            5.0,
            !dimensions.is_empty(),
            dimensions,
            "Declare image width and height, or use framework components that reserve intrinsic layout space.",
        ),
        finding(
            "WEB-003",
            "Responsive image strategy is present",
            6.0,
            !responsive.is_empty(),
            responsive,
            "Use srcset/sizes, picture, or a framework image component that generates responsive variants.",
        ),
        finding(
            "WEB-004",
            "Modern image formats are referenced",
            4.0,
            !modern.is_empty(),
            modern,
            "Provide WebP/AVIF delivery where compatible, with fallback when required.",
        ),
        finding(
            "WEB-005",
            "Image optimization or CDN path is present",
            6.0,
            !optimization.is_empty(),
            optimization,
            "Use an application-native optimizer, image proxy, or managed/self-hosted image CDN when repeated resizing and cache delivery are needed.",
        ),
        finding(
            "WEB-006",
            "External image origins are constrained",
            6.0,
            !constrained.is_empty(),
            constrained,
            "Constrain external image origins with allow-lists or equivalent policy, especially when using image proxies.",
        ),
    ]
}

#[cfg(test)]
mod tests {
    use super::{evidence_for, has_image_usage};

    #[test]
    fn detects_image_usage_and_features() {
        let files = vec![(
            "page.tsx".to_string(),
            "<img src=\"/a.webp\" width=\"100\" height=\"100\" loading=\"lazy\" srcSet=\"/a.webp 1x\" />"
                .to_string(),
        )];
        assert!(has_image_usage(&files));
        assert!(!evidence_for(&files, &["loading=\"lazy\""]).is_empty());
        assert!(!evidence_for(&files, &[".webp"]).is_empty());
    }
}
