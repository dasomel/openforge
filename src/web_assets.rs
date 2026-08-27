use crate::Finding;
use std::{collections::BTreeSet, fs, path::Path};
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

fn extract_tag_usages(
    path: &str,
    text: &str,
    needle: &str,
    framework_image: bool,
) -> Vec<ImageUsage> {
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

fn contains_any(text: &str, needles: &[&str]) -> bool {
    let lower = text.to_ascii_lowercase();
    needles
        .iter()
        .any(|needle| lower.contains(&needle.to_ascii_lowercase()))
}

fn attribute_value(fragment: &str, attribute: &str) -> Option<String> {
    let lower = fragment.to_ascii_lowercase();
    let needle = format!("{attribute}=");
    let start = lower.find(&needle)? + needle.len();
    let rest = fragment[start..].trim_start();
    let quote = rest.chars().next()?;
    if quote != '"' && quote != '\'' {
        return None;
    }
    let body = &rest[quote.len_utf8()..];
    let end = body.find(quote)?;
    Some(body[..end].to_string())
}

fn markdown_url(fragment: &str) -> Option<String> {
    let start = fragment.find("](")? + 2;
    let end = fragment[start..].find(')')? + start;
    Some(fragment[start..end].trim().to_string())
}

fn source_url(usage: &ImageUsage) -> Option<String> {
    if usage.markdown_image {
        markdown_url(&usage.fragment)
    } else {
        attribute_value(&usage.fragment, "src")
    }
}

fn host_from_url(url: &str) -> Option<String> {
    let rest = url
        .strip_prefix("https://")
        .or_else(|| url.strip_prefix("http://"))?;
    let authority = rest.split('/').next()?.split('?').next()?;
    let host = authority.rsplit('@').next()?.split(':').next()?;
    (!host.is_empty()).then(|| host.to_ascii_lowercase())
}

fn external_host(usage: &ImageUsage) -> Option<String> {
    source_url(usage).and_then(|url| host_from_url(&url))
}

fn lazy_applies(usage: &ImageUsage) -> bool {
    if usage.markdown_image {
        return false;
    }
    if usage.framework_image {
        return !contains_any(
            &usage.fragment,
            &["priority", "loading=\"eager\"", "loading='eager'"],
        );
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

fn optimizer_applies(usage: &ImageUsage) -> bool {
    if usage.framework_image {
        return true;
    }
    contains_any(
        &usage.fragment,
        &[
            "wsrv.nl",
            "weserv",
            "imagekit.io",
            "cloudinary",
            "imgix",
            "cdn-cgi/image",
            "/_next/image",
        ],
    )
}

fn configured_origin_hosts(files: &[(String, String)]) -> BTreeSet<String> {
    let mut hosts = BTreeSet::new();
    for (_, text) in files {
        let lower = text.to_ascii_lowercase();
        if !contains_any(
            &lower,
            &[
                "remotepatterns",
                "images.domains",
                "allowedorigins",
                "allowed_origins",
                "origin allow",
                "origin_allow",
            ],
        ) {
            continue;
        }
        for token in text.split(|c: char| {
            c.is_whitespace() || matches!(c, ',' | '[' | ']' | '{' | '}' | '(' | ')' | ';')
        }) {
            let cleaned = token.trim_matches(|c: char| matches!(c, '"' | '\'' | '`' | ':' | '='));
            if let Some(host) = host_from_url(cleaned) {
                hosts.insert(host);
            } else if cleaned.contains('.')
                && !cleaned.contains('/')
                && cleaned
                    .chars()
                    .all(|c| c.is_ascii_alphanumeric() || matches!(c, '.' | '-' | '*'))
            {
                hosts.insert(cleaned.to_ascii_lowercase());
            }
        }
    }
    hosts
}

fn host_allowed(host: &str, allowed: &BTreeSet<String>) -> bool {
    allowed.iter().any(|pattern| {
        pattern == host
            || pattern
                .strip_prefix("*.")
                .is_some_and(|suffix| host == suffix || host.ends_with(&format!(".{suffix}")))
    })
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
        status: if passed_count == total {
            "PASS"
        } else {
            "FAIL"
        },
        score: (ratio * weight * 10.0).round() / 10.0,
        weight,
        evidence,
        remediation: remediation.to_string(),
    }
}

fn external_proxy_finding(usages: &[ImageUsage]) -> Finding {
    let external: Vec<&ImageUsage> = usages
        .iter()
        .filter(|usage| external_host(usage).is_some())
        .collect();
    if external.is_empty() {
        return skipped(
            "WEB-005",
            "External images use an optimization or CDN path",
            "no external image usage detected",
        );
    }
    coverage_finding(
        "WEB-005",
        "External images use an optimization or CDN path",
        6.0,
        &external.into_iter().cloned().collect::<Vec<_>>(),
        optimizer_applies,
        "Route external images through an application-native optimizer, controlled proxy, or image CDN when transformation/caching is required.",
    )
}

fn origin_coverage_finding(files: &[(String, String)], usages: &[ImageUsage]) -> Finding {
    let external_hosts: BTreeSet<String> = usages.iter().filter_map(external_host).collect();
    if external_hosts.is_empty() {
        return skipped(
            "WEB-006",
            "External image origins are constrained",
            "no external image usage detected",
        );
    }

    let allowed = configured_origin_hosts(files);
    let covered: Vec<String> = external_hosts
        .iter()
        .filter(|host| host_allowed(host, &allowed))
        .cloned()
        .collect();
    let missing: Vec<String> = external_hosts
        .iter()
        .filter(|host| !host_allowed(host, &allowed))
        .cloned()
        .collect();
    let total = external_hosts.len();
    let ratio = covered.len() as f64 / total as f64;
    let mut evidence = vec![format!(
        "origin_coverage={}/{} coverage_percent={:.1}",
        covered.len(),
        total,
        ratio * 100.0
    )];
    evidence.extend(
        covered
            .iter()
            .take(12)
            .map(|host| format!("allowed={host}")),
    );
    evidence.extend(
        missing
            .iter()
            .take(12)
            .map(|host| format!("missing_allowlist={host}")),
    );

    Finding {
        rule_id: "WEB-006".to_string(),
        category: "Web Assets".to_string(),
        title: "External image origins are constrained".to_string(),
        status: if missing.is_empty() { "PASS" } else { "FAIL" },
        score: (ratio * 6.0 * 10.0).round() / 10.0,
        weight: 6.0,
        evidence,
        remediation: "Declare explicit allowed external image origins and keep them aligned with actual external image usage.".to_string(),
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
                "External images use an optimization or CDN path",
                "no image usage detected",
            ),
            skipped(
                "WEB-006",
                "External image origins are constrained",
                "no image usage detected",
            ),
        ];
    }

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
        external_proxy_finding(&usages),
        origin_coverage_finding(&files, &usages),
    ]
}

#[cfg(test)]
mod tests {
    use super::{
        configured_origin_hosts, dimensions_apply, external_host, host_allowed, image_usages,
        lazy_applies, modern_format_applies, optimizer_applies, responsive_applies,
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
    fn treats_next_image_as_lazy_responsive_and_optimized_by_default() {
        let files = vec![(
            "page.tsx".to_string(),
            "<Image src=\"https://images.example.com/hero.jpg\" width={1200} height={800} />"
                .to_string(),
        )];
        let usages = image_usages(&files);
        assert_eq!(usages.len(), 1);
        assert!(lazy_applies(&usages[0]));
        assert!(dimensions_apply(&usages[0]));
        assert!(responsive_applies(&usages[0]));
        assert!(optimizer_applies(&usages[0]));
        assert_eq!(
            external_host(&usages[0]).as_deref(),
            Some("images.example.com")
        );
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

    #[test]
    fn extracts_and_matches_allowed_external_origins() {
        let files = vec![(
            "next.config.js".to_string(),
            "images: { remotePatterns: [{ hostname: 'images.example.com' }, { hostname: '*.cdn.example.net' }] }"
                .to_string(),
        )];
        let hosts = configured_origin_hosts(&files);
        assert!(host_allowed("images.example.com", &hosts));
        assert!(host_allowed("a.cdn.example.net", &hosts));
        assert!(!host_allowed("evil.example.org", &hosts));
    }
}
