use crate::Finding;
use std::process::Command;

const WEIGHT: f64 = 6.0;

#[derive(Debug, Default, PartialEq, Eq)]
struct CacheHeaders {
    cache_control: Option<String>,
    age: Option<String>,
    etag: Option<String>,
    last_modified: Option<String>,
}

fn parse_final_headers(text: &str) -> CacheHeaders {
    let normalized = text.replace("\r\n", "\n");
    let block = normalized
        .split("\n\n")
        .rev()
        .find(|part| part.trim_start().starts_with("HTTP/"))
        .unwrap_or(&normalized);

    let mut headers = CacheHeaders::default();
    for line in block.lines().skip(1) {
        let Some((name, value)) = line.split_once(':') else {
            continue;
        };
        let value = value.trim().to_string();
        match name.trim().to_ascii_lowercase().as_str() {
            "cache-control" => headers.cache_control = Some(value),
            "age" => headers.age = Some(value),
            "etag" => headers.etag = Some(value),
            "last-modified" => headers.last_modified = Some(value),
            _ => {}
        }
    }
    headers
}

fn max_age_seconds(cache_control: &str) -> Option<u64> {
    cache_control.split(',').find_map(|part| {
        let part = part.trim();
        let value = part
            .strip_prefix("max-age=")
            .or_else(|| part.strip_prefix("s-maxage="))?;
        value.trim_matches('"').parse().ok()
    })
}

fn cache_policy_passes(headers: &CacheHeaders) -> bool {
    let Some(cache_control) = headers.cache_control.as_deref() else {
        return false;
    };
    let lower = cache_control.to_ascii_lowercase();
    lower.contains("immutable") && max_age_seconds(&lower).is_some_and(|seconds| seconds >= 86_400)
}

fn validate_url(url: &str) -> Result<(), &'static str> {
    if !(url.starts_with("https://") || url.starts_with("http://")) {
        return Err("web cache URL must use http:// or https://");
    }
    if url.contains('@') {
        return Err("web cache URL must not contain userinfo credentials");
    }
    Ok(())
}

pub(crate) fn finding(url: Option<&str>) -> Finding {
    let Some(url) = url else {
        return Finding {
            rule_id: "WEB-008".to_string(),
            category: "Web Assets".to_string(),
            title: "Runtime image endpoint returns immutable cache headers".to_string(),
            status: "SKIP",
            score: 0.0,
            weight: 0.0,
            evidence: vec!["no explicit --web-cache-url provided".to_string()],
            remediation: String::new(),
        };
    };

    if let Err(reason) = validate_url(url) {
        return failed(vec![format!("probe_error={reason}")]);
    }

    let output = Command::new("curl")
        .args([
            "--head",
            "--silent",
            "--show-error",
            "--location",
            "--max-redirs",
            "3",
            "--connect-timeout",
            "5",
            "--max-time",
            "10",
            url,
        ])
        .output();

    let output = match output {
        Ok(output) if output.status.success() => output,
        Ok(output) => {
            let stderr = String::from_utf8_lossy(&output.stderr).trim().to_string();
            return failed(vec![format!(
                "probe_error=curl exited with status {}{}",
                output.status,
                if stderr.is_empty() {
                    String::new()
                } else {
                    format!(" stderr={stderr}")
                }
            )]);
        }
        Err(error) => return failed(vec![format!("probe_error=cannot execute curl: {error}")]),
    };

    let headers = parse_final_headers(&String::from_utf8_lossy(&output.stdout));
    let passed = cache_policy_passes(&headers);
    let mut evidence = Vec::new();
    if let Some(value) = headers.cache_control {
        evidence.push(format!("cache-control={value}"));
    } else {
        evidence.push("cache-control=missing".to_string());
    }
    if let Some(value) = headers.age {
        evidence.push(format!("age={value}"));
    }
    if let Some(value) = headers.etag {
        evidence.push(format!("etag={value}"));
    }
    if let Some(value) = headers.last_modified {
        evidence.push(format!("last-modified={value}"));
    }

    Finding {
        rule_id: "WEB-008".to_string(),
        category: "Web Assets".to_string(),
        title: "Runtime image endpoint returns immutable cache headers".to_string(),
        status: if passed { "PASS" } else { "FAIL" },
        score: if passed { WEIGHT } else { 0.0 },
        weight: WEIGHT,
        evidence,
        remediation: "Serve the explicit image endpoint with Cache-Control containing immutable and a max-age or s-maxage of at least 86400 seconds.".to_string(),
    }
}

fn failed(evidence: Vec<String>) -> Finding {
    Finding {
        rule_id: "WEB-008".to_string(),
        category: "Web Assets".to_string(),
        title: "Runtime image endpoint returns immutable cache headers".to_string(),
        status: "FAIL",
        score: 0.0,
        weight: WEIGHT,
        evidence,
        remediation: "Provide a reachable explicit HTTP(S) image URL and ensure it returns long-lived immutable Cache-Control headers.".to_string(),
    }
}

#[cfg(test)]
mod tests {
    use super::{cache_policy_passes, max_age_seconds, parse_final_headers, validate_url};

    #[test]
    fn parses_last_redirect_response_headers() {
        let headers = parse_final_headers(
            "HTTP/1.1 301 Moved Permanently\r\nlocation: https://cdn.example/a.webp\r\n\r\nHTTP/2 200\r\ncache-control: public, max-age=31536000, immutable\r\nage: 42\r\netag: abc\r\n\r\n",
        );
        assert_eq!(
            headers.cache_control.as_deref(),
            Some("public, max-age=31536000, immutable")
        );
        assert_eq!(headers.age.as_deref(), Some("42"));
    }

    #[test]
    fn requires_immutable_and_at_least_one_day() {
        let headers = parse_final_headers(
            "HTTP/2 200\ncache-control: public, max-age=86400, immutable\n\n",
        );
        assert!(cache_policy_passes(&headers));

        let short = parse_final_headers(
            "HTTP/2 200\ncache-control: public, max-age=60, immutable\n\n",
        );
        assert!(!cache_policy_passes(&short));
    }

    #[test]
    fn parses_s_maxage() {
        assert_eq!(
            max_age_seconds("public, s-maxage=31536000, immutable"),
            Some(31_536_000)
        );
    }

    #[test]
    fn rejects_non_http_and_userinfo_urls() {
        assert!(validate_url("file:///tmp/a.webp").is_err());
        assert!(validate_url("https://user:pass@example.com/a.webp").is_err());
        assert!(validate_url("https://example.com/a.webp").is_ok());
    }
}
