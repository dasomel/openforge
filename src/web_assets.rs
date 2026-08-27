use crate::Finding;
use std::{fs, path::Path};
use walkdir::WalkDir;

const SOURCE_EXTENSIONS: &[&str] = &[
    "html", "htm", "jsx", "tsx", "vue", "svelte", "astro", "md", "mdx", "js", "ts",
];

#[derive(Debug, Clone)]
struct ImageUsage {
    location: String,
    fragment: String,
    framework_image: bool,
    markdown_image: bool,
}

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

fn extract_tag_usages(path: &str, text: &str, needle: &str, framework_image: bool) -> Vec<ImageUsage> {
    let mut usages = Vec::new();
    let mut offset = 0usize;

    while let Some(relative_start) = text[offset..].find(needle) {
        let start = offset + relative_start;
        let tail = &text[start..];
        let Some(relative_end) = tail.find('>') else {
            break;
        };
        let end = start + relative_end + 1;
        let line = text[..start].bytes().filter(|byte| *byte == b'\n').count() + 1;
        usages.push(ImageUsage {
            location: format!("{path}:{line}"),
            fragment: text[start..end].to_string(),
            framework_image,
            markdown_image: false,
        });
        offset = end;
    }

    usages
}

fn extract_markdown_usages(path: &str, text: &str) -> Vec<ImageUsage> {
    let mut usages = Vec::new();
    for (line_index, line) in text.lines().enumerate() {
        let mut offset = 0usize;
        while let Some(relative_start) = line[offset..].find("![") {
            let start = offset + relative_start;
            let tail = &line[start..];
            let Some(close_alt) = tail.find("](") else {
                break;
            };
            let after_open = close_alt + 2;
            let Some(close_url) = tail[after_open..].find(')') else {
                break;
            };
            let end = start + after_open + close_url + 1;
            usages.push(ImageUsage {
                location: format!("{path}:{}", line_index + 1),
                fragment: line[start..end].to_string(),
                framework_image: false,
                markdown_image: true,
            });
            offset = end;
        }
    }
    usages
}

fn image_usages(files: &[(String, String)]) -> Vec<ImageUsage> {
    let mut usages = Vec::new();
    for (path, text) in files {
        usages.extend(extract_tag_usages(path, text, "<img", false));
        usages.extend(extract_tag_usages(path, text, "<Image", true));
        usages.extend(extract_markdown_usages(path, text));
    }
    usages
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

fn contains_any(text: &str, needles: &[&str]) -> bool {
    let lower = text.to_ascii_lowercase();
    needles
        .iter()
        .any(|needle| lower.contains(&needle.to_ascii_lowercase()))
}

fn lazy_applies(usage: &ImageUsage) -> bool {
    if usage.markdown_image {
        return false;
    }
    if usage.framework_image {
        return !contains_any(&usage.fragment, &["priority", "loading=\"eager\"", "loading='eager'"]);
    }
    contains_any(
        &usage.fragment,
        &["loading=\"lazy\"", "loading='lazy'", "loading={\"lazy\"}"],
    )
}

fn dimensions_apply(usage: &ImageUsage) -> bool {
    if usage.markdown_image {
        return false;
    }
    if usage.framework_image && contains_any(&usage.fragment, &[" fill", "fill={true}"]) {
        return true;
    }
    let has_width = contains_any(&usage.fragment, &[" width=", " width={"]);
    let has_height = contains_any(&usage.fragment, &[" height=", " height={"]);
    has_width && has_height
}

fn responsive_applies(usage: &ImageUsage) -> bool {
    if usage.framework_image {
        return true;
    }
    contains_any(&usage.fragment, &["srcset=", "sizes=", "<picture"])
}

fn modern_format_applies(usage: &ImageUsage) -> bool {
    contains_any(
        &usage.fragment,
        &[
            ".webp",
            ".avif",
            "output=webp",
            "output=avif",
            "format=webp",
            "format=avif",
        ],
    )
}

fn coverage_finding<F>(
    id: &str,
    title: &str,
    weight: f64,
    usages: &[ImageUsage],
    predicate: F,
    remediation: &str,
) -> Finding
where
    F: Fn(&ImageUsage) -> bool,
{
    let passed: Vec<&ImageUsage> = usages.iter().filter(|usage| predicate(usage)).collect();
    let passed_count = passed.len();
    let total = usages.len();
    let ratio = passed_count as f64 / total as f64;
    let mut evidence = vec![format!(
        "coverage={passed_count}/{total} coverage_percent={:.1}",
        ratio * 100.0
    )];
    evidence.extend(
        passed
            .iter()
            .take(12)
            .map(|usage| format!("covered={}", usage.location)),
    );
    evidence.extend(
        usages
            .iter()
            .filter(|usage| !predicate(usage))
            .take(12)
            .map(|usage| format!("missing={}", usage.location)),
    );

    Finding {
        rule_id: id.to_string(),
        category: "Web Assets".to_string(),
        title: title.to_string(),
        status: if passed_count == total { "PASS" } else { "FAIL" },
        score: (ratio * weight * 10.0).round() / 10.0,
        weight,
        evidence,
        remediation: remediation.to_string(),
    }
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
    let usages = image_usages(&files);
    if usages.is_empty() {
        return vec![
            skipped("WEB-001", "Images use lazy loading", "no image usage detected"),
            skipped("WEB-002", "Images declare dimensions", "no image usage detected"),
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
        coverage_finding(
            "WEB-001",
            "Images use lazy loading",
            4.0,
            &usages,
            lazy_applies,
            "Use native lazy loading or framework-equivalent deferred loading for non-critical images.",
        ),
        coverage_finding(
            "WEB-002",
            "Images declare dimensions",
            5.0,
            &usages,
            dimensions_apply,
            "Declare both image width and height, or use framework components that reserve intrinsic layout space.",
        ),
        coverage_finding(
            "WEB-003",
            "Responsive image strategy is present",
            6.0,
            &usages,
            responsive_applies,
            "Use srcset/sizes, picture, or a framework image component that generates responsive variants.",
        ),
        coverage_finding(
            "WEB-004",
            "Modern image formats are referenced",
            4.0,
            &usages,
            modern_format_applies,
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
    use super::{
        dimensions_apply, image_usages, lazy_applies, modern_format_applies, responsive_applies,
    };

    #[test]
    fn calculates_html_image_features_per_usage() {
        let files = vec![(
            "page.tsx".to_string(),
            "<img src=\"/a.webp\" width=\"100\" height=\"100\" loading=\"lazy\" srcset=\"/a.webp 1x\" /><img src=\"/b.png\" />"
                .to_string(),
        )];
        let usages = image_usages(&files);
        assert_eq!(usages.len(), 2);
        assert!(lazy_applies(&usages[0]));
        assert!(dimensions_apply(&usages[0]));
        assert!(responsive_applies(&usages[0]));
        assert!(modern_format_applies(&usages[0]));
        assert!(!lazy_applies(&usages[1]));
        assert!(!dimensions_apply(&usages[1]));
    }

    #[test]
    fn treats_next_image_as_lazy_and_responsive_by_default() {
        let files = vec![(
            "page.tsx".to_string(),
            "<Image src=\"/hero.jpg\" width={1200} height={800} />".to_string(),
        )];
        let usages = image_usages(&files);
        assert_eq!(usages.len(), 1);
        assert!(lazy_applies(&usages[0]));
        assert!(dimensions_apply(&usages[0]));
        assert!(responsive_applies(&usages[0]));
    }

    #[test]
    fn markdown_images_are_counted_without_inferred_browser_features() {
        let files = vec![(
            "README.md".to_string(),
            "![diagram](docs/architecture.webp)".to_string(),
        )];
        let usages = image_usages(&files);
        assert_eq!(usages.len(), 1);
        assert!(!lazy_applies(&usages[0]));
        assert!(!dimensions_apply(&usages[0]));
        assert!(modern_format_applies(&usages[0]));
    }
}
